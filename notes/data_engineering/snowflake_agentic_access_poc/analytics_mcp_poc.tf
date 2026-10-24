# Standalone POC: one MCP, one Agent with two Analyst tools, one OAuth integration, three consumer roles.
# Existing database, warehouse, three dedicated non-production users, two semantic views, and dummy sources are prerequisites.
# Replace the dummy view/source defaults together; this file does not create or own those objects.
# Authenticate the provisioning provider through your existing Snowflake profile/environment.
# Its role needs CREATE SCHEMA, CREATE ROLE, CREATE INTEGRATION, source visibility, and grant authority.
# The MCP schema must inherit Snowflake OAuth, not an External OAuth authorization-server binding.
# Network policies must already allow ChatGPT's published egress addresses.
#
# Provider schemas: https://github.com/snowflakedb/terraform-provider-snowflake/tree/v2.22.0/docs/resources
# Agent specification: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-run
# Partial access: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-inaccessible-tool-handling
# OAuth/callback: https://developers.openai.com/plugins/build/auth

terraform {
  required_version = ">= 1.11.0"

  required_providers {
    snowflake = {
      source  = "snowflakedb/snowflake"
      version = "= 2.22.0"
    }
  }
}

provider "snowflake" {}

variable "database_name" {
  description = "Existing database for the new MCP/Agent schema; source databases are independent."
  type        = string
  default     = "DEVELOPMENT"

  validation {
    condition     = can(regex("^[A-Z_][A-Z0-9_]*$", var.database_name))
    error_message = "Use an uppercase, unquoted database identifier for this POC."
  }
}

variable "warehouse_name" {
  description = "Existing warehouse used for Agent queries and the POC users' MCP sessions."
  type        = string

  validation {
    condition     = can(regex("^[A-Z_][A-Z0-9_]*$", var.warehouse_name))
    error_message = "Use an uppercase, unquoted warehouse identifier for this POC."
  }
}

variable "poc_user_names" {
  description = "Three dedicated non-production users' exact object names, without SQL quotes; each receives one consumer role."
  type = object({
    sales       = string
    customers   = string
    all_domains = string
  })

  validation {
    condition     = length(toset(values(var.poc_user_names))) == 3 && alltrue([for name in values(var.poc_user_names) : length(trimspace(name)) > 0])
    error_message = "Use three distinct, nonempty Snowflake user names so each access level can be tested separately."
  }
}

variable "snowflake_account_url" {
  description = "Public account URL, such as https://myorg-myaccount.snowflakecomputing.com."
  type        = string

  validation {
    condition     = can(regex("^https://[A-Za-z0-9-]+\\.snowflakecomputing\\.com/?$", var.snowflake_account_url))
    error_message = "Use the public organization-account URL with hyphens rather than underscores."
  }
}

variable "chatgpt_redirect_uri" {
  description = "Copy the exact redirect URI shown when configuring this MCP connection in ChatGPT."
  type        = string

  validation {
    condition     = startswith(var.chatgpt_redirect_uri, "https://chatgpt.com/")
    error_message = "Use the HTTPS callback shown by ChatGPT; do not guess a callback ID."
  }
}

variable "oauth_refresh_token_validity_seconds" {
  description = "Refresh-token lifetime; expiry requires authorization again. Default is 24 hours, not Snowflake's 90-day default."
  type        = number
  default     = 86400

  validation {
    condition     = var.oauth_refresh_token_validity_seconds >= 86400 && var.oauth_refresh_token_validity_seconds <= 7776000 && floor(var.oauth_refresh_token_validity_seconds) == var.oauth_refresh_token_validity_seconds
    error_message = "Use an integer refresh-token lifetime between 86400 seconds (1 day) and 7776000 seconds (90 days)."
  }
}

variable "semantic_views" {
  description = "Two existing dummy semantic views; use uppercase, unquoted DATABASE.SCHEMA.NAME identifiers."
  type = object({
    sales     = string
    customers = string
  })
  default = {
    sales     = "DEVELOPMENT.POC_DATA.SV_SALES"
    customers = "DEVELOPMENT.POC_DATA.SV_CUSTOMERS"
  }

  validation {
    condition     = length(toset(values(var.semantic_views))) == 2 && alltrue([for name in values(var.semantic_views) : can(regex("^[A-Z_][A-Z0-9_]*\\.[A-Z_][A-Z0-9_]*\\.[A-Z_][A-Z0-9_]*$", name))])
    error_message = "Use two distinct semantic views with uppercase, unquoted three-part identifiers."
  }
}

variable "domain_sources" {
  description = "Existing dummy dependencies by domain: DATABASE.SCHEMA.NAME => TABLE or VIEW. Grants follow each domain."
  type = object({
    sales     = map(string)
    customers = map(string)
  })
  default = {
    sales = {
      "DEVELOPMENT.POC_DATA.DUMMY_SALES" = "TABLE"
    }
    customers = {
      "DEVELOPMENT.POC_DATA.DUMMY_CUSTOMERS" = "TABLE"
    }
  }

  validation {
    condition = alltrue([
      for sources in values(var.domain_sources) : length(sources) > 0 && alltrue([
        for name, object_type in sources :
        can(regex("^[A-Z_][A-Z0-9_]*\\.[A-Z_][A-Z0-9_]*\\.[A-Z_][A-Z0-9_]*$", name)) && contains(["TABLE", "VIEW"], object_type)
      ])
    ])
    error_message = "Enumerate the required dummy sources using uppercase three-part names and TABLE or VIEW types."
  }

  validation {
    condition     = length(setintersection(toset(keys(var.domain_sources.sales)), toset(keys(var.domain_sources.customers)))) == 0
    error_message = "Use separate dummy sources for the two domains in this isolation POC."
  }
}

locals {
  consumer_role_names = {
    sales       = "ROLE_SALES_ANALYTICS_POC"
    customers   = "ROLE_CUSTOMERS_ANALYTICS_POC"
    all_domains = "ROLE_ALL_ANALYTICS_POC"
  }

  domains = {
    sales = {
      semantic_view = var.semantic_views.sales
      sources       = var.domain_sources.sales
      description   = "Use for aggregate sales totals, order counts, and product-category breakdowns."
    }
    customers = {
      semantic_view = var.semantic_views.customers
      sources       = var.domain_sources.customers
      description   = "Use for aggregate customer counts and customer-segment breakdowns."
    }
  }

  domain_objects = {
    for domain, config in local.domains : domain => concat([config.semantic_view], keys(config.sources))
  }
  database_grants = merge([for domain, objects in local.domain_objects : {
    for database in toset(concat([var.database_name], [for name in objects : split(".", name)[0]])) :
    "${domain}:${database}" => { domain = domain, name = database }
  }]...)
  schema_grants = merge([for domain, objects in local.domain_objects : {
    for schema in toset(concat(
      ["${var.database_name}.${snowflake_schema.analytics.name}"],
      [for name in objects : join(".", slice(split(".", name), 0, 2))]
    )) : "${domain}:${schema}" => { domain = domain, name = schema }
  }]...)
  source_grants = merge([for domain, config in local.domains : {
    for name, object_type in config.sources :
    "${domain}:${name}" => { domain = domain, name = name, object_type = object_type }
  }]...)
}

resource "snowflake_schema" "analytics" {
  database = var.database_name
  name     = "ANALYTICS_POC"
}

resource "snowflake_account_role" "consumer" {
  for_each = local.consumer_role_names
  name     = each.value
}

# The combined primary role inherits both domain roles; secondary roles stay disabled in OAuth.
resource "snowflake_grant_account_role" "all_domains" {
  for_each         = local.domains
  role_name        = snowflake_account_role.consumer[each.key].name
  parent_role_name = snowflake_account_role.consumer["all_domains"].name
}

resource "snowflake_grant_account_role" "poc_user" {
  for_each  = var.poc_user_names
  role_name = snowflake_account_role.consumer[each.key].name
  user_name = format("\"%s\"", replace(each.value, "\"", "\"\""))
}

# PUBLIC may already inherit CORTEX_USER; feature entitlement does not grant Agent or data access.
resource "snowflake_grant_database_role" "agent_api" {
  for_each           = local.domains
  database_role_name = "\"SNOWFLAKE\".\"CORTEX_AGENT_USER\""
  parent_role_name   = snowflake_account_role.consumer[each.key].name
}

resource "snowflake_grant_privileges_to_account_role" "database_usage" {
  for_each          = local.database_grants
  account_role_name = snowflake_account_role.consumer[each.value.domain].name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "DATABASE"
    object_name = each.value.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "schema_usage" {
  for_each          = local.schema_grants
  account_role_name = snowflake_account_role.consumer[each.value.domain].name
  privileges        = ["USAGE"]

  on_schema {
    schema_name = each.value.name
  }
}

resource "snowflake_grant_privileges_to_account_role" "warehouse_usage" {
  for_each          = local.domains
  account_role_name = snowflake_account_role.consumer[each.key].name
  privileges        = ["USAGE"]

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = var.warehouse_name
  }
}

resource "snowflake_grant_privileges_to_account_role" "semantic_view_select" {
  for_each          = local.domains
  account_role_name = snowflake_account_role.consumer[each.key].name
  privileges        = ["SELECT"]

  on_schema_object {
    object_type = "SEMANTIC VIEW"
    object_name = each.value.semantic_view
  }
}

# Agents need source access too. These explicit dummy-source grants also permit direct reads.
resource "snowflake_grant_privileges_to_account_role" "source_select" {
  for_each          = local.source_grants
  account_role_name = snowflake_account_role.consumer[each.value.domain].name
  privileges        = ["SELECT"]

  on_schema_object {
    object_type = each.value.object_type
    object_name = each.value.name
  }
}

resource "snowflake_cortex_agent" "analytics" {
  database = var.database_name
  schema   = snowflake_schema.analytics.name
  name     = "ANALYTICS_AGENT_POC"

  specification = yamlencode({
    orchestration = {
      tool_not_accessible = "accept"
      # Starting limits for measurement; orchestration tokens exclude some tool consumption.
      budget = {
        seconds = 60
        tokens  = 8000
      }
    }
    instructions = {
      orchestration = "Use the sales or customers Analyst tool for its described domain, subject to caller access. Ask for clarification when the metric or period is ambiguous. Refuse unsupported joins and cross-domain calculations. Never substitute an accessible domain for an inaccessible one."
      response      = "Report the result, metric meaning, exact dates, and filters. Preserve access warnings and execution failures; explain when the requested data is unavailable to the caller. Never invent numbers or a freshness timestamp."
    }
    tools = [for domain, config in local.domains : {
      tool_spec = {
        type        = "cortex_analyst_text_to_sql"
        name        = domain
        description = config.description
      }
    }]
    tool_resources = {
      for domain, config in local.domains : domain => {
        semantic_view = config.semantic_view
        execution_environment = {
          type          = "warehouse"
          warehouse     = var.warehouse_name
          query_timeout = 30
        }
      }
    }
  })
}

resource "snowflake_grant_privileges_to_account_role" "agent_usage" {
  for_each          = local.domains
  account_role_name = snowflake_account_role.consumer[each.key].name
  privileges        = ["USAGE"]

  on_schema_object {
    object_type = "AGENT"
    object_name = snowflake_cortex_agent.analytics.fully_qualified_name
  }
}

resource "snowflake_mcp_server" "analytics" {
  database = var.database_name
  schema   = snowflake_schema.analytics.name
  name     = "ANALYTICS_MCP_POC"

  specification = yamlencode({
    tools = [{
      name        = "analytics"
      title       = "Analytics"
      type        = "CORTEX_AGENT_RUN"
      identifier  = snowflake_cortex_agent.analytics.fully_qualified_name
      description = "Ask aggregate sales or customer questions; available domains depend on your Snowflake role."
      annotations = {
        readOnlyHint    = true
        destructiveHint = false
        idempotentHint  = false
        openWorldHint   = false
      }
    }]
  })
}

# Snowflake's privilege reference includes tool invocation under USAGE; consumers need no MODIFY grant.
resource "snowflake_grant_privileges_to_account_role" "mcp_usage" {
  for_each          = local.domains
  account_role_name = snowflake_account_role.consumer[each.key].name
  privileges        = ["USAGE"]

  on_schema_object {
    object_type = "MCP SERVER"
    object_name = snowflake_mcp_server.analytics.fully_qualified_name
  }
}

# ChatGPT selects this client registration by client ID; it is not embedded in the MCP spec.
# OAUTH_ANY_ROLE_MODE is not exposed by this provider resource; a new integration defaults to DISABLE.
resource "snowflake_oauth_integration_for_custom_clients" "chatgpt" {
  name                             = "CHATGPT_ANALYTICS_POC"
  oauth_client_type                = "CONFIDENTIAL"
  oauth_redirect_uri               = var.chatgpt_redirect_uri
  enabled                          = "true"
  oauth_allow_non_tls_redirect_uri = "false"
  oauth_enforce_pkce               = "true"
  oauth_use_secondary_roles        = "NONE"
  allowed_roles_list               = [for role in snowflake_account_role.consumer : role.name]
  oauth_issue_refresh_tokens       = "true"
  oauth_refresh_token_validity     = var.oauth_refresh_token_validity_seconds
}

output "chatgpt_connection" {
  description = "Configure a custom Analytics MCP connection in ChatGPT with personal OAuth."
  value = {
    mcp_server_url = "${trimsuffix(var.snowflake_account_url, "/")}/api/v2/databases/${var.database_name}/schemas/${snowflake_schema.analytics.name}/mcp-servers/${snowflake_mcp_server.analytics.name}"
    authentication = "OAuth"
    integration    = snowflake_oauth_integration_for_custom_clients.chatgpt.name
    consumer_roles = { for scope, role in snowflake_account_role.consumer : scope => role.name }
    warehouse      = var.warehouse_name
  }
}

# User defaults remain outside this stack because the existing identities may be SCIM-managed.
output "poc_user_defaults_sql" {
  description = "For dedicated POC identities only: have the identity owner set defaults; Terraform does not execute this SQL."
  value = {
    for scope, user in var.poc_user_names : scope => format(
      "ALTER USER \"%s\" SET DEFAULT_ROLE = '%s' DEFAULT_WAREHOUSE = '%s';",
      replace(user, "\"", "\"\""), snowflake_account_role.consumer[scope].name, var.warehouse_name
    )
  }
}

# After an approved apply, obtain this integration's generated client ID/secret in a protected
# Snowflake admin session using SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('CHATGPT_ANALYTICS_POC').
# Enter credentials directly in ChatGPT's OAuth settings; do not fetch them into Terraform state.
# RBAC enforces access; resource bindings and response instructions do not guarantee metric-only execution.
