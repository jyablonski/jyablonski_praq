# Gmail Draft Script Notes

This directory contains a minimal Python script that creates a Gmail draft via the Gmail API.

## Files

- [main.py](/home/jacob/Documents/jyablonski_praq/gmail/main.py): creates a draft using the Gmail API
- [credentials.json](/home/jacob/Documents/jyablonski_praq/gmail/credentials.json): OAuth client file downloaded from Google Cloud
- [token.json](/home/jacob/Documents/jyablonski_praq/gmail/token.json): cached user token created after first successful login

## What The Script Does

- Uses OAuth to authenticate as `jyablonski9@gmail.com`
- Requests only the Gmail compose scope
- Builds a small hello-world style email
- Creates a draft in that account's Gmail `Drafts`
- Leaves `To` optional by default

Important: this creates a draft in `Drafts`, not in the `Inbox`.

## Minimal Permission Scope

The script uses:

```text
https://www.googleapis.com/auth/gmail.compose
```

That is the narrow scope that still allows draft creation.

## Setup For A Personal Gmail Account

Use an OAuth client, not a service account.

1. Create a Google Cloud project.
1. Enable the Gmail API.
1. Configure the OAuth consent screen.
1. Set the app audience to `External`.
1. Create an OAuth client of type `Desktop app`.
1. Download the JSON file and save it as `gmail/credentials.json`.
1. Add `jyablonski9@gmail.com` under `Test users` while the app is in testing.
1. Run `python gmail/main.py`.
1. Sign in with `jyablonski9@gmail.com` and approve access.

After the first successful login, Google returns a token and the script saves it to `gmail/token.json`.

## Why The 403 Happened

This error:

```text
has not completed the Google verification process...
Error 403: access_denied
```

usually means the OAuth app is still in `Testing` and the Google account used during login is not listed as a `Test user`.

Fix:

1. Open the same Google Cloud project that owns `credentials.json`.
1. Go to the OAuth audience or test-user settings.
1. Add `jyablonski9@gmail.com` as a test user.
1. Delete `gmail/token.json` if needed.
1. Run the script again.

## Service Account Notes

For a personal `@gmail.com` inbox, a service account is not the right approach.

- A service account does not have its own Gmail mailbox
- It cannot access a personal Gmail inbox directly
- Personal Gmail automation should use OAuth user consent

Service accounts become relevant in a company Google Workspace environment when:

- the company has Google Workspace
- a super admin enables domain-wide delegation
- the service account is allowed to impersonate real users
- the granted scope is tightly limited, such as `gmail.compose`

In that setup, a script can create drafts in a stakeholder's mailbox on their behalf. That is an admin-controlled Workspace pattern, not a personal Gmail pattern.

## Running The Script

```bash
python gmail/main.py
```

If you change scopes later, delete `gmail/token.json` and re-run so Google issues a new token with the updated permissions.

## References

- https://developers.google.com/workspace/gmail/api/quickstart/python
- https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.drafts/create
- https://developers.google.com/workspace/gmail/api/auth/scopes
- https://developers.google.com/workspace/guides/auth-overview
- https://support.google.com/a/answer/162106?hl=en
