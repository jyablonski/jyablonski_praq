mock_provider "snowflake" {
  override_during = plan

  mock_resource "snowflake_cortex_agent" {
    defaults = {
      fully_qualified_name = "DEVELOPMENT.ANALYTICS_POC.ANALYTICS_AGENT_POC"
    }
  }

  mock_resource "snowflake_mcp_server" {
    defaults = {
      fully_qualified_name = "DEVELOPMENT.ANALYTICS_POC.ANALYTICS_MCP_POC"
    }
  }
}

variables {
  warehouse_name        = "POC_WH"
  snowflake_account_url = "https://example-example.snowflakecomputing.com"
  # Mock-only callback; live connections must supply the exact URI displayed by ChatGPT.
  chatgpt_redirect_uri = "https://chatgpt.com/connector_platform_oauth_redirect"
  poc_user_names = {
    sales       = "POC_SALES_USER"
    customers   = "POC_CUSTOMERS_USER"
    all_domains = "POC_ALL_USER"
  }
}

run "domain_authorization_matrix" {
  command = plan

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.semantic_view_select :
      "${grant.account_role_name}|${grant.on_schema_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT.POC_DATA.SV_SALES",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT.POC_DATA.SV_CUSTOMERS"
    ])
    error_message = "A restricted role received the other domain's semantic view or its own grant is missing."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.source_select :
      "${grant.account_role_name}|${grant.on_schema_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT.POC_DATA.DUMMY_SALES",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT.POC_DATA.DUMMY_CUSTOMERS"
    ])
    error_message = "Source grants must follow the restricted-domain matrix."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_account_role.all_domains :
      "${grant.parent_role_name}|${grant.role_name}"
      ]) == toset([
      "ROLE_ALL_ANALYTICS_POC|ROLE_SALES_ANALYTICS_POC",
      "ROLE_ALL_ANALYTICS_POC|ROLE_CUSTOMERS_ANALYTICS_POC"
    ])
    error_message = "Only the combined primary role should inherit both domain roles."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_account_role.poc_user :
      "${grant.user_name}|${grant.role_name}"
      ]) == toset([
      "\"POC_SALES_USER\"|ROLE_SALES_ANALYTICS_POC",
      "\"POC_CUSTOMERS_USER\"|ROLE_CUSTOMERS_ANALYTICS_POC",
      "\"POC_ALL_USER\"|ROLE_ALL_ANALYTICS_POC"
    ])
    error_message = "Users must be assigned their intended role rather than gaining all domains directly."
  }

  assert {
    condition = snowflake_oauth_integration_for_custom_clients.chatgpt.allowed_roles_list == toset([
      "ROLE_SALES_ANALYTICS_POC", "ROLE_CUSTOMERS_ANALYTICS_POC", "ROLE_ALL_ANALYTICS_POC"
      ]) && snowflake_oauth_integration_for_custom_clients.chatgpt.oauth_use_secondary_roles == "NONE" && (
      snowflake_oauth_integration_for_custom_clients.chatgpt.oauth_refresh_token_validity == 86400
    )
    error_message = "OAuth must allow the three primary roles, keep secondary roles off, and use the default 24-hour refresh lifetime."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.warehouse_usage :
      "${grant.account_role_name}|${grant.on_account_object[0].object_type}|${grant.on_account_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|WAREHOUSE|POC_WH",
      "ROLE_CUSTOMERS_ANALYTICS_POC|WAREHOUSE|POC_WH"
      ]) && alltrue([
      for grant in snowflake_grant_privileges_to_account_role.warehouse_usage : grant.privileges == toset(["USAGE"])
    ])
    error_message = "Only the two domain roles receive explicit usage of the configured warehouse; the combined role inherits it."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_database_role.agent_api :
      "${grant.parent_role_name}|${grant.database_role_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|\"SNOWFLAKE\".\"CORTEX_AGENT_USER\"",
      "ROLE_CUSTOMERS_ANALYTICS_POC|\"SNOWFLAKE\".\"CORTEX_AGENT_USER\""
    ])
    error_message = "Only the two domain roles receive explicit Agent feature entitlement; the combined role inherits it."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.agent_usage :
      "${grant.account_role_name}|${grant.on_schema_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC.ANALYTICS_AGENT_POC",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC.ANALYTICS_AGENT_POC"
      ]) && alltrue([
      for grant in snowflake_grant_privileges_to_account_role.agent_usage : grant.privileges == toset(["USAGE"])
    ])
    error_message = "Both domain roles need usage of the shared Agent without management privileges."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.mcp_usage :
      "${grant.account_role_name}|${grant.on_schema_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC.ANALYTICS_MCP_POC",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC.ANALYTICS_MCP_POC"
      ]) && alltrue([
      for grant in snowflake_grant_privileges_to_account_role.mcp_usage : grant.privileges == toset(["USAGE"])
    ])
    error_message = "Both domain roles need usage of the shared MCP without management privileges."
  }

  assert {
    condition = yamldecode(snowflake_cortex_agent.analytics.specification).orchestration.tool_not_accessible == "accept" && toset([
      for tool in yamldecode(snowflake_cortex_agent.analytics.specification).tools : tool.tool_spec.name
    ]) == toset(["sales", "customers"])
    error_message = "The shared Agent must continue with accessible tools when one domain is denied."
  }

  assert {
    condition     = length(yamldecode(snowflake_mcp_server.analytics.specification).tools) == 1 && yamldecode(snowflake_mcp_server.analytics.specification).tools[0].type == "CORTEX_AGENT_RUN"
    error_message = "The client must receive one shared Agent tool rather than independent SQL execution."
  }

  assert {
    condition = yamldecode(snowflake_mcp_server.analytics.specification).tools[0].annotations == {
      readOnlyHint    = true
      destructiveHint = false
      idempotentHint  = false
      openWorldHint   = false
    }
    error_message = "The analytics tool must retain its reviewed client annotations, including readOnlyHint=true."
  }
}

run "domain_parents_stay_separate" {
  command = plan

  variables {
    semantic_views = {
      sales     = "SALES_DB.SEMANTIC.SV_SALES"
      customers = "CUSTOMERS_DB.SEMANTIC.SV_CUSTOMERS"
    }
    domain_sources = {
      sales = {
        "SALES_DB.EVENTS.ORDERS"       = "TABLE"
        "SALES_DB.DIMENSIONS.PRODUCTS" = "VIEW"
      }
      customers = {
        "CUSTOMERS_DB.MARTS.CUSTOMERS" = "TABLE"
      }
    }
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.database_usage :
      "${grant.account_role_name}|${grant.on_account_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT",
      "ROLE_SALES_ANALYTICS_POC|SALES_DB",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT",
      "ROLE_CUSTOMERS_ANALYTICS_POC|CUSTOMERS_DB"
    ])
    error_message = "Restricted roles must not gain the other domain's parent database."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.schema_usage :
      "${grant.account_role_name}|${grant.on_schema[0].schema_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC",
      "ROLE_SALES_ANALYTICS_POC|SALES_DB.SEMANTIC",
      "ROLE_SALES_ANALYTICS_POC|SALES_DB.EVENTS",
      "ROLE_SALES_ANALYTICS_POC|SALES_DB.DIMENSIONS",
      "ROLE_CUSTOMERS_ANALYTICS_POC|DEVELOPMENT.ANALYTICS_POC",
      "ROLE_CUSTOMERS_ANALYTICS_POC|CUSTOMERS_DB.SEMANTIC",
      "ROLE_CUSTOMERS_ANALYTICS_POC|CUSTOMERS_DB.MARTS"
    ])
    error_message = "Grant only the shared control schema and each role's own domain schemas."
  }

  assert {
    condition = toset([
      for grant in snowflake_grant_privileges_to_account_role.source_select :
      "${grant.account_role_name}|${grant.on_schema_object[0].object_type}|${grant.on_schema_object[0].object_name}"
      ]) == toset([
      "ROLE_SALES_ANALYTICS_POC|TABLE|SALES_DB.EVENTS.ORDERS",
      "ROLE_SALES_ANALYTICS_POC|VIEW|SALES_DB.DIMENSIONS.PRODUCTS",
      "ROLE_CUSTOMERS_ANALYTICS_POC|TABLE|CUSTOMERS_DB.MARTS.CUSTOMERS"
    ])
    error_message = "Multiple source types must remain confined to their own domain role."
  }
}

run "duplicate_users_are_rejected" {
  command = plan
  variables {
    poc_user_names = {
      sales       = "SAME_USER"
      customers   = "SAME_USER"
      all_domains = "SAME_USER"
    }
  }
  expect_failures = [var.poc_user_names]
}

run "shared_dummy_sources_are_rejected" {
  command = plan
  variables {
    domain_sources = {
      sales     = { "DEVELOPMENT.POC_DATA.SHARED" = "TABLE" }
      customers = { "DEVELOPMENT.POC_DATA.SHARED" = "TABLE" }
    }
  }
  expect_failures = [var.domain_sources]
}

run "duplicate_views_are_rejected" {
  command = plan
  variables {
    semantic_views = {
      sales     = "DEVELOPMENT.POC_DATA.SAME_VIEW"
      customers = "DEVELOPMENT.POC_DATA.SAME_VIEW"
    }
  }
  expect_failures = [var.semantic_views]
}

run "maximum_refresh_lifetime_is_supported" {
  command = plan

  variables {
    oauth_refresh_token_validity_seconds = 7776000
  }

  assert {
    condition     = snowflake_oauth_integration_for_custom_clients.chatgpt.oauth_refresh_token_validity == 7776000
    error_message = "The configured refresh-token lifetime must reach the OAuth integration, including the supported upper bound."
  }
}

run "short_refresh_lifetime_is_rejected" {
  command = plan

  variables {
    oauth_refresh_token_validity_seconds = 86399
  }

  expect_failures = [var.oauth_refresh_token_validity_seconds]
}

run "long_refresh_lifetime_is_rejected" {
  command = plan

  variables {
    oauth_refresh_token_validity_seconds = 7776001
  }

  expect_failures = [var.oauth_refresh_token_validity_seconds]
}

run "fractional_refresh_lifetime_is_rejected" {
  command = plan

  variables {
    oauth_refresh_token_validity_seconds = 86400.5
  }

  expect_failures = [var.oauth_refresh_token_validity_seconds]
}
