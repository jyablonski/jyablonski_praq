-- Run in sections after setup_poc.sql and verify_poc.sql, using the same trial user.
-- Replace the callback placeholder with the exact OAuth redirect URI shown by your ChatGPT connection before creating the integration.
-- This changes your trial user's default role and warehouse for new sessions; record the current values below first.
-- Custom OAuth setup: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp
-- ChatGPT setup: https://developers.openai.com/api/docs/guides/custom-mcp-server

USE ROLE ACCOUNTADMIN;

-- Use this URL in ChatGPT Plugins > Add custom MCP server, then select OAuth.
-- In Advanced OAuth settings, choose the registration method for manually entered client ID/secret credentials.
-- Copy that setup's complete Callback URL into OAUTH_REDIRECT_URI below; leave Registration URL empty.
-- Keep session:role:all selected, Base scopes empty, and OIDC disabled for this POC.
SELECT
    'https://'
    || REPLACE(LOWER(CURRENT_ORGANIZATION_NAME() || '-' || CURRENT_ACCOUNT_NAME()), '_', '-')
    || '.snowflakecomputing.com/api/v2/databases/AGENTIC_ACCESS_POC/schemas/ANALYTICS_POC/mcp-servers/ANALYTICS_MCP_POC'
    AS MCP_SERVER_URL;

SHOW USERS;
SELECT
    "name" AS USER_NAME,
    "default_role" AS PREVIOUS_DEFAULT_ROLE,
    "default_warehouse" AS PREVIOUS_DEFAULT_WAREHOUSE
FROM TABLE(RESULT_SCAN(LAST_QUERY_ID()))
WHERE "name" = CURRENT_USER();

-- Fill in the callback, then execute this CREATE once. Existing integrations are deliberately not replaced.
CREATE SECURITY INTEGRATION CHATGPT_ANALYTICS_POC
    TYPE = OAUTH
    OAUTH_CLIENT = CUSTOM
    OAUTH_CLIENT_TYPE = 'CONFIDENTIAL'
    OAUTH_REDIRECT_URI = 'REPLACE_WITH_EXACT_CHATGPT_CALLBACK_URL'
    ENABLED = TRUE
    OAUTH_ALLOW_NON_TLS_REDIRECT_URI = FALSE
    OAUTH_ENFORCE_PKCE = TRUE
    OAUTH_USE_SECONDARY_ROLES = NONE
    OAUTH_ANY_ROLE_MODE = DISABLE
    ALLOWED_ROLES_LIST = (
        'ROLE_SALES_ANALYTICS_POC',
        'ROLE_CUSTOMERS_ANALYTICS_POC',
        'ROLE_ALL_ANALYTICS_POC'
    )
    OAUTH_ISSUE_REFRESH_TOKENS = TRUE
    OAUTH_REFRESH_TOKEN_VALIDITY = 86400;

-- The default MCP scope uses DEFAULT_ROLE, not the role selected in your worksheet.
-- ACCOUNTADMIN is blocked from OAuth by default. Use the POC reader role and a non-null default warehouse.
EXECUTE IMMEDIATE $$
DECLARE
    poc_user VARCHAR;
BEGIN
    poc_user := '"' || REPLACE(CURRENT_USER(), '"', '""') || '"';
    ALTER USER IDENTIFIER(:poc_user)
        SET DEFAULT_ROLE = 'ROLE_ALL_ANALYTICS_POC'
            DEFAULT_WAREHOUSE = 'AGENTIC_ACCESS_POC_WH';
    RETURN 'POC OAuth defaults set for ' || poc_user;
END;
$$;

DESCRIBE SECURITY INTEGRATION CHATGPT_ANALYTICS_POC;

-- Run this manually in your Snowflake admin worksheet. Copy oauth_client_id and oauth_client_secret directly into ChatGPT's OAuth settings.
-- Keep the returned credentials out of repository files, chat messages, and shared query-result exports.
SELECT SYSTEM$SHOW_OAUTH_CLIENT_SECRETS('CHATGPT_ANALYTICS_POC');

-- Complete the ChatGPT connection using OAuth with the client ID and secret above, then sign in to Snowflake and consent.
-- If ChatGPT offers token endpoint authentication options, use client_secret_basic.
-- Select the "I understand and want to continue" checkbox before clicking Create as a plugin.
-- Install the plugin, start a new Work chat, and invoke it with @ followed by the plugin name.
-- Ask for September 2026 completed revenue (USD 1000), all-date completed revenue (USD 2000), and registered customers (6).
-- If the optional Agent checks in verify_poc.sql have not run yet, execute them before diagnosing ChatGPT-specific issues.
--
-- To test a restricted role with this one user, change DEFAULT_ROLE in the ALTER USER block to the desired POC role,
-- execute the block, then disconnect/reconnect the Snowflake account in ChatGPT to obtain a new OAuth token and start a fresh chat.
-- Existing tokens retain their authorized role; changing defaults alone does not change an existing connection.
-- This tests OAuth role behavior for one user. Separate-user identity isolation still needs dedicated users.
-- Full reconnect steps and expected results: pilot_suggestions.md#personal-trial-switch-roles-and-reconnect-chatgpt
