from datetime import datetime
import os
import tempfile

import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# small script to download a Google Doc as a PDF using google drive API
# it grabs credentials, downloads the file, and checks if the current file is
# the same as the downloaded file. if they're the same, it removes the downloaded
# file, but if they're different then the new one is saved and the old one is
# moved to an outdated folder with a timestamp

# the creds is just a service account w/ read access. after you create it and
# give it the permissions, you have to add a key which is a json file that stores the creds
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
CREDS_PATH = "resume/downloader_creds.json"


# Authenticate and create the service
def authenticate_google_account(creds_path: str):
    if os.path.exists(creds_path):
        creds = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES
        )
    else:
        raise FileNotFoundError(f"Credentials file not found: {creds_path}")

    return build("drive", "v3", credentials=creds)


# Function to download the Google Doc as PDF
def download_google_doc_as_pdf(file_id, save_path):
    service = authenticate_google_account(creds_path=CREDS_PATH)
    request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
    fh = open(save_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}%.")
    print(f"Download complete: {save_path}")


def move_outdated_file(current_path: str, outdated_file_path: str):
    outdated_file_path = os.path.expanduser(outdated_file_path)
    current_path = os.path.expanduser(current_path)

    outdated_dir = os.path.dirname(outdated_file_path)
    os.makedirs(outdated_dir, exist_ok=True)

    shutil.move(current_path, outdated_file_path)
    print(f"Moved outdated resume to: {outdated_file_path}")


def check_file_differences(file1: str, file2: str) -> bool:
    if not os.path.exists(file1) or not os.path.exists(file2):
        return False
    return open(file1, "rb").read() == open(file2, "rb").read()


resume_file_id = "1Tu6TiekdQUNRaTF2aGwHpwzfPAi_Xf5wwKeXyLd8n8c"

current_ts = datetime.now()
current_resume_path = os.path.expanduser("~/Documents/resume/jyablonski_resume.pdf")
outdated_file_path = os.path.expanduser(
    f"~/Documents/resume/outdated/jyablonski_resume_{current_ts}.pdf"
)

if __name__ == "__main__":
    # Step 1: Download to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        temp_download_path = tmp_file.name

    download_google_doc_as_pdf(file_id=resume_file_id, save_path=temp_download_path)

    # Step 2: Compare the files and optionally replace the current one
    if os.path.exists(current_resume_path) and check_file_differences(
        file1=current_resume_path, file2=temp_download_path
    ):
        print("No changes detected. Resume is up-to-date.")
        os.remove(temp_download_path)

    else:
        if os.path.exists(current_resume_path):
            move_outdated_file(current_resume_path, outdated_file_path)
        shutil.move(temp_download_path, current_resume_path)
        print(f"Saved updated resume to: {current_resume_path}")
