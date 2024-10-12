# Faker

## Providers 
[Link](https://faker.readthedocs.io/en/master/providers.html)

# memory usage
```
worker_df.info()
worker_df.info(memory_usage="deep")
worker_df.memory_usage(deep=True)
```
 - always use deep bc it actaully counts string columns where memory is extremely variable
 - 1 string that's 20 characters is way less memory than a string that has 5000+ characters in it.

# Lambda

``` sh
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 509399594058.dkr.ecr.us-east-1.amazonaws.com
docker build -t lambda_function_faker .
docker tag lambda_function_faker:latest 509399594058.dkr.ecr.us-east-1.amazonaws.com/jacobs_repo:lambda_function_faker
docker push 509399594058.dkr.ecr.us-east-1.amazonaws.com/jacobs_repo:lambda_function_faker

```