import os
import uuid

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContainerClient

container_name = "jacobs-container"

service = BlobServiceClient(
    account_url=f"https://{os.environ.get('azure_storage_name')}.blob.core.windows.net/",
    credential=os.environ.get('azure_access_key')
)

container_client = service.create_container(container_name)

# Create a file in the local data directory to upload and download
local_file_name = str(uuid.uuid4()) + ".txt"
upload_file_path = os.path.join("./data", local_file_name)

# Write text to the file
file = open(file=upload_file_path, mode='w')
file.write("Hello, World!")
file.close()

blob_client = service.get_blob_client(container=container_name, blob=local_file_name)

print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

# Upload the created file
with open(file=upload_file_path, mode="rb") as data:
    blob_client.upload_blob(data)