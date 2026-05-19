# dbt CI

## Workflow Example

- Build new or changed models
- Generate Docs
- Upload new manifest.json to S3 for next run's state comparison
- Build new Docker image with dbt and push to ECR

```yaml
name: dbt deploy

on:
  push:
    branches: [main]
    paths:
      - 'models/**'
      - 'macros/**'
      - 'seeds/**'
      - 'snapshots/**'
      - 'tests/**'
      - 'dbt_project.yml'
      - 'packages.yml'
      - 'profiles/**'
      - 'Dockerfile'
      - '.github/workflows/dbt-deploy.yml'

env:
  AWS_REGION: us-east-1
  DBT_ARTIFACTS_BUCKET: axios-dbt-artifacts
  DBT_DOCS_BUCKET: axios-dbt-docs
  ECR_REPOSITORY: axios-dbt
  DBT_PROFILES_DIR: ./profiles
  DBT_TARGET: prod

jobs:
  # 1. Run dbt against prod, building only new/changed models using slim CI
  dbt-run:
    name: Build changed models
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    outputs:
      sha: ${{ github.sha }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dbt
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt   # dbt-core + dbt-snowflake pinned here

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Fetch previous prod manifest for state comparison
        run: |
          mkdir -p prod-artifacts
          aws s3 cp s3://${DBT_ARTIFACTS_BUCKET}/prod/manifest.json prod-artifacts/manifest.json || \
            echo "No previous manifest found — first run, will build everything."

      - name: dbt deps
        run: dbt deps --target ${DBT_TARGET}

      - name: dbt build (slim CI)
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
        run: |
          if [ -f prod-artifacts/manifest.json ]; then
            dbt build \
              --target ${DBT_TARGET} \
              --select state:modified+ \
              --state prod-artifacts \
              --fail-fast
          else
            dbt build --target ${DBT_TARGET} --fail-fast
          fi

      - name: Generate docs
        if: success()
        env:
          SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
          SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
          SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
          SNOWFLAKE_ROLE: ${{ secrets.SNOWFLAKE_ROLE }}
          SNOWFLAKE_WAREHOUSE: ${{ secrets.SNOWFLAKE_WAREHOUSE }}
          SNOWFLAKE_DATABASE: ${{ secrets.SNOWFLAKE_DATABASE }}
        run: dbt docs generate --target ${DBT_TARGET}

      - name: Upload target/ as workflow artifact
        uses: actions/upload-artifact@v4
        with:
          name: dbt-target-${{ github.sha }}
          path: target/
          retention-days: 14

  # 2. Promote manifest.json to the slim CI location in S3
  publish-manifest:
    name: Publish prod manifest
    needs: dbt-run
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: actions/download-artifact@v4
        with:
          name: dbt-target-${{ github.sha }}
          path: target/

      - name: Upload manifest.json (versioned + latest)
        run: |
          aws s3 cp target/manifest.json \
            s3://${DBT_ARTIFACTS_BUCKET}/prod/manifest.json \
            --cache-control "no-cache"
          aws s3 cp target/manifest.json \
            s3://${DBT_ARTIFACTS_BUCKET}/prod/history/${GITHUB_SHA}/manifest.json
          aws s3 cp target/run_results.json \
            s3://${DBT_ARTIFACTS_BUCKET}/prod/history/${GITHUB_SHA}/run_results.json

  # 3. Publish the docs site to S3 + invalidate CloudFront
  publish-docs:
    name: Publish dbt docs site
    needs: dbt-run
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - uses: actions/download-artifact@v4
        with:
          name: dbt-target-${{ github.sha }}
          path: target/

      - name: Sync docs site to S3
        run: |
          # The site is really just these four files
          aws s3 cp target/index.html      s3://${DBT_DOCS_BUCKET}/ --cache-control "no-cache"
          aws s3 cp target/manifest.json   s3://${DBT_DOCS_BUCKET}/ --cache-control "no-cache"
          aws s3 cp target/catalog.json    s3://${DBT_DOCS_BUCKET}/ --cache-control "no-cache"
          aws s3 cp target/graph.gpickle   s3://${DBT_DOCS_BUCKET}/ --cache-control "no-cache" || true

      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.DBT_DOCS_CLOUDFRONT_ID }} \
            --paths "/*"

  # 4. Build & push the dbt Docker image
  publish-image:
    name: Build and push dbt image
    needs: dbt-run
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to ECR
        id: ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:${{ github.sha }}
            ${{ steps.ecr.outputs.registry }}/${{ env.ECR_REPOSITORY }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```
