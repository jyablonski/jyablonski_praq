import os
import uuid

from azure.storage.blob import BlobServiceClient

import pandas as pd

container_name = "jacobs-container"

# connect to a storage account
service = BlobServiceClient(
    account_url=f"https://{os.environ.get('azure_storage_name')}.blob.core.windows.net/",
    credential=os.environ.get("azure_access_key"),
)

container_client = service.create_container(container_name)

# Create a file in the local data directory to upload and download
local_file_name = str(uuid.uuid4()) + ".txt"
upload_file_path = os.path.join("./data", local_file_name)

# Write text to the file
file = open(file=upload_file_path, mode="w")
file.write("Hello, World!")
file.close()


# create a client to insert objects into the specified container
blob_client = service.get_blob_client(container=container_name, blob=local_file_name)

print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

# Upload the created file
with open(file=upload_file_path, mode="rb") as data:
    blob_client.upload_blob(data)

df = pd.read_csv("../csvs/nba_tweets.csv")
blob_client = service.get_blob_client(container=container_name, blob="test-lol.csv")

with open(file="../csvs/nba_tweets.csv", mode="rb") as data:
    blob_client.upload_blob(data)
