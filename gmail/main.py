from __future__ import annotations

import base64
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
SCRIPT_DIR = Path(__file__).resolve().parent
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"
TOKEN_PATH = SCRIPT_DIR / "token.json"
ACCOUNT_EMAIL = "jyablonski9@gmail.com"
TO_EMAIL: str | None = None


def get_credentials() -> Credentials:
    creds: Credentials | None = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                "Missing gmail/credentials.json. Download an OAuth client JSON file "
                "from Google Cloud and save it next to this script."
            )

        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
        creds = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(creds.to_json())
    return creds


def build_draft_message() -> dict[str, dict[str, str]]:
    message = EmailMessage()
    message["From"] = ACCOUNT_EMAIL
    if TO_EMAIL:
        message["To"] = TO_EMAIL
    message["Subject"] = "Hello from the Gmail API"
    message.set_content(
        "Hello world-ish from a minimal Python script.\n\n"
        "This draft was created with the Gmail API."
    )

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"message": {"raw": encoded_message}}


def main() -> None:
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=build_draft_message())
        .execute()
    )

    print(f"Draft created for {ACCOUNT_EMAIL}")
    print(f"Draft ID: {draft['id']}")
    print(f"Message ID: {draft['message']['id']}")


if __name__ == "__main__":
    main()
