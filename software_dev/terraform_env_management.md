# Terraform Env Management
[Terraform Workspaces](https://developer.hashicorp.com/terraform/cloud-docs/workspaces)
[Gruntwork Article](https://blog.gruntwork.io/how-to-manage-multiple-environments-with-terraform-using-workspaces-98680d89a03e)
[Spacelift Article](https://spacelift.io/blog/terraform-environments)
[Stackoverflow](https://stackoverflow.com/questions/72331158/terraform-different-backend-for-each-project)

## Terraform Workspaces
As you develop infrastructure-as-code with Terraform you quickly run into a dilemma with how to manage Resources across multiple accounts and cloud environments. IaC requirements should enable:
- Possible to use the same IaC configurations for managing prod + nonprod environments to avoid drift
  - This is different than copy pasting configurations around
- Certain nonprod environments like Dev, QA, UAT should be identical and scaled-down versions of production
- Team Members should be able to create, manage, and destroy temporary environments that are identical to production
- All environments are not created in the same cloud account

Terraform offers a workspace feature that enables you to create and manage these environments using the same configuration.  These environments are completely isolated and do not interfere with each other.

Terraform Workspaces are different than Terraform Cloud Workspaces.
- In Terraform Cloud, workspaces are analogous to a Project, which corresponds to a Terraform Repo. It manages state, variables, credentials, history

``` sh
# show the one you're on
terraform workspace show

# create a new one
terraform workspace new beta

# show all the ones available to you.
terraform workspace list

# switch to a new one
terraform workspace select default

# delete it
terraform workspace delete beta
```

To use this feature, you must tell Terraform which workspace you're working with. For example, this is needed to set 1 EC2 instance in nonprod environments to t2.micro, or to build 3 m4.large ones in production.

``` tf
locals {
  escargot_instance_type = {
    dev   = "t2.micro"
    staging = "t2.small"
    prod  = "m4.large"
  }
}

resource "aws_instance" "escargo_app_instance" {
  count         = terraform.workspace == "default" ? 3 : 1
  ami           = var.ami //Ubuntu AMI
  instance_type = local.escargot_instance_type[terraform.workspace]

  tags = {
    Name = "example-server-${terraform.workspace}"
  }
}

```

This Feature also enables teams to spinup dev environments for testing & in isolation that can be quickly spun back down before they merge their changes up and find out they don't work.

## Accounts and State Management
Multiple environments require credentials to various cloud accounts.  AWS implements the concept of Organizations for companies that want to build out infra across many AWS Accounts.

``` tf
provider "aws" {
  shared_config_files      = ["/path/to/.aws/conf"]
  shared_credentials_files = ["/path/to/.aws/creds"]
  profile                  = "profile_name"
}

terraform {
  backend "s3" {
    bucket = "example-bucket"
    region = "us-east-2"
    key    = "example/terraform.tfstate"
  }
}

terraform {
  backend "s3" {
    // THIS CODE WILL NOT WORK!!!!
    bucket = (
      terraform.workspace == "prod" 
      ? "prod-bucket" 
      : "example-bucket"
    )
    // THIS CODE WILL NOT WORK!!!!
    region = "us-east-2"
    key    = "example/terraform.tfstate"
  }
}
```

State Management is handled using whichever backend is currently set.  There are 3 general options:
- Local Files
- S3
- Terraform Cloud / Enterprise

S3 is generally preferable so you can manage infra your team members are building without it being tied to their machine, and you don't have vendor lock-in by using Terraform Cloud.

The `backend` block does not allow you to use variables, interopolation, or references, so the code block above will not work.  You must use a single hard coded value, which means all of your environments end up in the same s3 bucket.  This is the primary reason Hashicorp does not recommend using Terraform Workspaces to manage environments.

But, you can pass in the `-backend-config` argument to `terraform plan` or `apply` 

## Branching Strategy
[Article](https://blog.gruntwork.io/how-to-manage-multiple-environments-with-terraform-using-branches-875d1a2ee647)
Using multiple branches to manage Environment state is not the best strategy.  Git is used to coordinate development efforts across a team.  It maintains source code and package releases for deployments.  It seems tempting to use different branches to correspond to various environments such as `main` for production, `qa` for QA people, and `dev` for developers. 

The issues with that approach include state file management, scaling across the different environment-specific attributes, and managing credentials for multiple accounts.

## Directory Structure
![image](https://github.com/jyablonski/jyablonski_praq/assets/16946556/05bbe0d7-a6ea-45e4-a44b-e27d2f1f2e7a)

Can split up environments into different structures like so, seems like the easiest path forward but there's absolutely potential for drift, divergence, and does not promote DRY code.

## Open Questions
1. Branching Strategy ?
2. How do you handle code promotion?  you shouldn't be deploying to all 3 dev / stg / prod at the same time
3. Use a Service Provider or not ?
4. Keep Terraform Code with Application Code ?
5. Separate Repo for Modules ?