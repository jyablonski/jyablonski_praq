# GCP Service Account Permissions

## Mental Model

A Google Cloud service account is a non-human identity for a workload. It can authenticate to Google, receive OAuth access tokens, and call Google APIs as itself. It is not a normal Gmail or Workspace user unless it uses domain-wide delegation to impersonate one.

Service account access usually depends on several layers lining up:

1. The relevant API is enabled in the Google Cloud project.
1. The workload can authenticate as the service account.
1. The service account has IAM roles for Google Cloud resources.
1. The OAuth token has scopes that allow the API operation.
1. The target product has its own ACLs, such as Drive/Sheets sharing.
1. Organization policies and Workspace admin settings allow the action.

If any layer is missing, the result is usually a `403`, `404`, or `insufficient authentication scopes` error.

## How The Service Account Email Is Created

When you create a user-managed service account, you choose a service account ID. Google combines that ID with the project ID to create an email:

```text
sheets-sync@my-project-id.iam.gserviceaccount.com
```

That email is the service account principal. In IAM bindings, it is usually written with a `serviceAccount:` prefix:

```text
serviceAccount:sheets-sync@my-project-id.iam.gserviceaccount.com
```

Google also creates a permanent numeric unique ID. The display name and description can be changed later, but the ID in the email address cannot be changed after creation.

Default service accounts use special formats, such as:

```text
PROJECT_NUMBER-compute@developer.gserviceaccount.com
PROJECT_ID@appspot.gserviceaccount.com
```

Service agents are different: they are Google-managed service accounts used by Google services to act on your behalf. Treat them as service infrastructure, not application identities.

New service accounts can take roughly a minute to become visible everywhere because IAM reads are eventually consistent.

## IAM Roles vs Product ACLs

GCP IAM answers: can this identity access this Google Cloud resource?

Examples:

- Can this service account read objects in this Cloud Storage bucket?
- Can it run BigQuery jobs in this project?
- Can it read a Secret Manager secret?

Workspace product ACLs answer: can this identity access this user-facing file or workspace object?

Examples:

- Is this spreadsheet shared with the service account?
- Is the service account a member of this shared drive?
- Is the impersonated Workspace user allowed to read this document?

For Google Sheets, IAM roles on the GCP project do not grant access to a random spreadsheet in someone's Drive. The spreadsheet itself must be shared with the service account, created by the service account, accessible through shared drive membership, or accessed through domain-wide delegation.

## How Service Accounts Work With Spreadsheets

Google Sheets files are also Google Drive files, so visibility and sharing are governed by Drive permissions.

A plain service account has no automatic access to a user's My Drive. To let it read or edit a spreadsheet without domain-wide delegation:

1. Enable the Google Sheets API in the service account's GCP project.
1. Enable the Google Drive API too if the app lists files, reads metadata, creates files, or manages sharing.
1. Share the spreadsheet or parent folder with the service account email.
1. Grant an appropriate Drive role: `reader`, `commenter`, or `writer`.
1. Use the spreadsheet ID with the Sheets API.

Manual sharing works like sharing with a person: click Share in Sheets or Drive, paste the service account email, and grant the needed role. The service account does not need to accept an invite; the ACL entry is enough.

Programmatic sharing uses the Drive API `permissions.create` method. For a service account, the permission usually looks like:

```json
{
  "type": "user",
  "role": "reader",
  "emailAddress": "sheets-sync@my-project-id.iam.gserviceaccount.com"
}
```

The caller creating that permission must already be allowed to share the file or folder. If the spreadsheet lives in a shared drive, shared drive membership and shared drive restrictions can also matter.

Spreadsheet gotchas:

- `404 spreadsheet not found` often means "this token cannot see the file", not that the spreadsheet ID is wrong.
- A file created by the service account is owned by the service account, so a human user may need it shared back to them.
- Sheets API scopes apply to the whole spreadsheet file, not a single tab. Use protected ranges, separate spreadsheets, or app logic for per-tab or per-range controls.
- If the app only reads/writes cell values by known spreadsheet ID, Sheets API scopes may be enough. If it searches Drive, creates files, or edits sharing, it needs Drive API scopes too.

## Domain-Wide Delegation

Domain-wide delegation is a Google Workspace admin feature that lets an app use a service account to access Workspace user data without each user granting OAuth consent.

The usual flow:

1. Create a service account in a Google Cloud project.
1. Find the service account's OAuth client ID in its advanced settings.
1. A Workspace super admin opens Admin console -> Security -> Access and data control -> API controls -> Manage Domain Wide Delegation.
1. The admin adds the service account's client ID and the allowed OAuth scopes.
1. Application code creates credentials with a `subject` user, such as `alice@company.com`.
1. Google issues an access token for the requested scopes as that user.

With domain-wide delegation, the service account is impersonating a Workspace user. For Drive and Sheets, effective access is based on the impersonated user's file access plus the OAuth scopes on the token.

Example:

```text
service account: sheets-sync@my-project-id.iam.gserviceaccount.com
subject user:    alice@company.com
scopes:          https://www.googleapis.com/auth/spreadsheets.readonly
```

That token can read spreadsheets Alice can read, but it should not be able to write Sheets because the scope is read-only.

Domain-wide delegation is powerful:

- It can bypass individual user consent.
- OAuth scopes restrict data types and operations, not which users the service account can impersonate.
- Limit impersonated users in application logic.
- Prefer direct file sharing or a Google Group when that solves the problem.
- Review delegated clients and scopes regularly in the Admin console.
- Avoid long-lived service account keys when possible; prefer attached service accounts, service account impersonation, or workload identity federation.

Domain-wide delegation is a Workspace concept. It does not replace GCP IAM. If the same app reads BigQuery, Pub/Sub, Secret Manager, or Cloud Storage, the service account still needs normal IAM roles for those GCP resources.

## Limiting Permissions With Scopes

OAuth scopes define what an access token is allowed to ask an API to do. They are not the same thing as IAM roles.

For Workspace APIs, especially with domain-wide delegation, scopes are one of the main safety boundaries. The Admin console's delegation entry defines the maximum scopes the app may use. The code then requests a subset of those scopes when it creates a token.

Common Sheets/Drive scopes:

```text
https://www.googleapis.com/auth/spreadsheets.readonly
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive.file
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/drive
```

Prefer the narrowest scope that works:

- Use `spreadsheets.readonly` for read-only Sheets access.
- Use `spreadsheets` for reading and writing spreadsheet contents.
- Use `drive.file` when the app only needs files it creates or that the user explicitly opens/shares with the app.
- Avoid broad `drive` unless the app truly needs all Drive files visible to the identity.

For Google Cloud resources, IAM roles are the primary control. On Compute Engine VMs, access scopes are a legacy OAuth mechanism that can further limit some OAuth-based calls from that VM, but Google's current best practice is to use the broad `cloud-platform` access scope and restrict actual permissions with IAM roles.

Scopes do not grant access by themselves. A token with a broad scope still cannot read a spreadsheet the identity cannot see, and it cannot call a GCP API method if IAM denies the permission.

## APIs Must Be Enabled First

A service account cannot use a Google API just because it has an email, a key, or an IAM role. The API must also be enabled in the relevant GCP project.

Examples:

- Sheets automation needs the Google Sheets API enabled.
- Drive search or sharing needs the Google Drive API enabled.
- BigQuery jobs need the BigQuery API enabled.
- Secret reads need the Secret Manager API enabled.
- Managing service accounts needs the IAM API enabled.

API enablement is project-level, not service-account-level. Enabling an API may require accepting terms of service or billing responsibility. The caller enabling APIs needs `serviceusage.services.enable`, commonly via the Service Usage Admin role.

Depending on the architecture, APIs might need to be enabled in more than one project: the project that owns the service account, the quota/client project, and/or the project that owns the target resource.

Access scopes do not enable APIs. If the related API is disabled, the request can still fail even when the service account has the right IAM role and token scope.

For Workspace APIs, two separate admin actions are easy to confuse:

- Enable the API in the Google Cloud project used by the service account or OAuth client.
- If using domain-wide delegation, authorize the client ID and scopes in the Google Workspace Admin console.

## Practical Patterns

Direct service account + shared spreadsheet:

1. Create a dedicated service account, such as `sheets-sync`.
1. Enable Sheets API, and Drive API if needed.
1. Share the spreadsheet or folder with the service account email.
1. Grant the smallest Drive role: usually `reader` or `writer`.
1. Request the narrowest OAuth scopes.
1. Avoid broad project IAM roles unless the app also needs GCP resources.

Domain-wide delegation:

1. Create a dedicated service account per automation purpose.
1. Authorize only required scopes in the Workspace Admin console.
1. In code, impersonate explicit subject users.
1. Keep an allowlist of subjects or organizational units in app config.
1. Log the subject, scopes, target spreadsheet/file ID, and action.
1. Review delegated clients and service account keys regularly.

## Common Failure Modes

- `403 API has not been used or is disabled`: enable the API in the project.
- `403 insufficient authentication scopes`: token scope or VM access scope is too narrow.
- `403 permission denied`: IAM denies the GCP resource, or Drive/Sheets ACLs deny the file.
- `404 not found` for a spreadsheet: the authenticated identity cannot see it.
- `invalid_grant` with domain-wide delegation: client ID, scopes, subject user, clock skew, or Workspace admin authorization is wrong.
- Can read by spreadsheet ID but cannot list files: Sheets access exists, but Drive API access or Drive scopes are missing.

## Quick Checklist

- Which identity is the token actually for: service account or impersonated Workspace user?
- Is the needed API enabled in the relevant GCP project?
- Does the identity have required IAM roles for GCP resources?
- Is the spreadsheet shared with the identity, or can the delegated subject user access it?
- Are OAuth scopes narrow but sufficient?
- If using Compute Engine, are VM access scopes compatible?
- If using domain-wide delegation, did a Workspace super admin authorize the exact client ID and scopes?
- Is the app avoiding long-lived keys where a keyless option works?
