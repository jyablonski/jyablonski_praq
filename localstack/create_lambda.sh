#!/bin/bash
# ./create_lambda.sh
set -e

function create_lambda() {
 # ! Absolute path to code
 local dir=$PWD/src/

 # * LocalStack localhost endpoint
 local endpoint=http://localhost:4566

 # * Lambda configuration
 local function_handler=main.lambda_handler
 local function_name=localstack-test
 local function_role=arn:aws:iam::000000000000:role/localstack-does-not-care
 local function_runtime=python3.9

 aws --endpoint-url $endpoint lambda delete-function --function-name $function_name || true

 # * Create lambda in LocalStack
 aws --endpoint-url $endpoint lambda create-function \
  --code S3Bucket="hot-reload",S3Key="$dir" \
  --function-name $function_name \
  --handler $function_handler \
  --role $function_role \
  --runtime $function_runtime
}

create_lambda