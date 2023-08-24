# S3 - Boto3 client vs resource
Client has been around longer, can access all AWS services, but harder to use.  have to use paginate to grab more than 1000 objects for example.
`s3 = boto3.client("s3")`

Resource is easier to use and more practical, you don't have to worry about as many underlying details.  Doesn't have 100% coverage that client has.
`s3 = boto3.resource("s3")`
