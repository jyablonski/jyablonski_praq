import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContainerClient

service = BlobServiceClient(
    account_url=f"https://{os.environ.get('azure_storage_name')}.blob.core.windows.net/",
    credential=os.environ.get('azure_access_key')
)

container_client = ContainerClient.from_connection_string(conn_str="<connection_string>", container_name="my_container")

container_client.create_container()

blob = BlobClient.from_connection_string(conn_str="<connection_string>", container_name="my_container", blob_name="my_blob")

with open("./SampleSource.txt", "rb") as data:
    blob.upload_blob(data)