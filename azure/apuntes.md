# Microsoft Azure
[PyPi](https://pypi.org/project/azure-storage-blob/)
[Python Guide](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli)
[Moving from S3 to Azure Blob Storage](https://www.thomasmaurer.ch/2019/06/migrate-aws-s3-buckets-to-azure-blob-storage/)

## Blob Storage
Azure equivalent of AWS S3.  BLOB technically stands for "binary large object" but in a cloud context, it means that you use S3 or Azure Blob Storage to store any kind of file.  Images, CSVs, Parquets, Videos, Logs etc.

Libraries available to Java, Node, Python, Go etc.

## Storage Account
Provides a unique namespace for your data.

`https://jyablonski.blob.core.windows.net`

## Container
Containers organize a set of blobs similar to a directory in a file system.  

A Storage Account can have an unlimited amount of containers, and a container can store an unlimited amount of blobs.

`https://jyablonski.blob.core.windows.net/jacobscontainer`

## Blob
Blobs are individual files stored in a Container.
- Block Blob
- Append Blob
- Page Blob


`https://jyablonski.blob.core.windows.net/jacobscontainer/jacobsblob`

Can use Python or Azure Data Factory to move existing data to Blob Storage.


## Access Tier