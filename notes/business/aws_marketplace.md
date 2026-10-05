# AWS Marketplace: Hosting and Recurring Billing

AWS requirements and fee examples last verified: October 4, 2026. Recheck the linked AWS documentation before implementation or quoting a customer.

## Overview

AWS Marketplace lets customers purchase your software through AWS. AWS handles billing and seller disbursements, while you remain responsible for the product, deployment, support, and billing integration.

Where the application runs and how the customer pays are separate decisions. The application can run in the customer's AWS account or your account, with Marketplace handling the software charge in either model.

Buyers need an AWS account to purchase through Marketplace and receive the software charges on their AWS bill. A fully vendor-hosted service can avoid deploying application resources in the buyer's account, but the buyer still needs an AWS account for purchasing. Account and billing setup can add onboarding friction for clients that do not already use AWS. [AWS Marketplace buyer requirements](https://docs.aws.amazon.com/marketplace/latest/buyerguide/what-is-marketplace.html)

## Hosting Models

| Model | Infrastructure payer | Software payment | Operational considerations |
| --------------------------- | ------------------------------------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Customer-hosted | Customer pays AWS for resources in their account | Customer purchases your software through Marketplace | Define deployment permissions, upgrades, monitoring, support access, and responsibility boundaries |
| Vendor-hosted, dedicated | You pay AWS for a dedicated customer environment | Customer purchases your software through Marketplace | Dedicated resources simplify cost attribution but can increase operating costs |
| Vendor-hosted, multi-tenant | You pay AWS for shared infrastructure | Customer purchases your software through Marketplace | Track tenant usage and allocate shared costs to understand customer margins |

Customer-hosted infrastructure charges and your Marketplace software fee are separate charges. Marketplace does not automatically reimburse your infrastructure costs or calculate the margin for each tenant.

Customer-hosted deployment can keep application data in the customer's environment, but data residency still depends on your telemetry, integrations, support tooling, and architecture.

## Marketplace Product Types

A SaaS listing is suitable when you provide and manage an ongoing service. The application plane can run in your account, the buyer's account, or both. For customer-hosted SaaS, the control plane must reside in infrastructure you manage. If you deploy your AMI or container image into the buyer's account, AWS requires a separate Marketplace listing for that artifact; it can use BYOL pricing as an extension of the SaaS offering. [AWS SaaS architecture guidelines](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-guidelines.html)

AMI and container listings are alternatives when customers purchase deployable software artifacts. Deployment templates can provision the surrounding AWS resources. The product type determines the applicable pricing, fulfillment, and licensing integration.

Terraform or CloudFormation can automate deployment, but provisioning alone does not implement Marketplace registration, entitlements, or billing.

CloudFormation templates supplied for customer-hosted SaaS must meet AWS Marketplace template policies and be published through the SaaS Quick Launch deployment option. [AWS SaaS deployment requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-guidelines.html)

## Pricing and Payment Options

| Pricing model | Commercial arrangement | Billing behavior |
| ------------------------------ | ----------------------------------------------------- | ------------------------------------------------------------- |
| SaaS contract | Fixed commitment for specified quantities or capacity | Upfront payment or a supported payment schedule |
| SaaS subscription | Usage-based purchase | Report usage hourly; AWS bills monthly in arrears |
| SaaS contract with consumption | Contract commitment plus usage above the entitlement | Contract charges plus metered overages |

A private offer is a mechanism for negotiating buyer-specific pricing and terms for a supported product and pricing model. Its payment structure depends on the underlying pricing model and negotiated offer. [Product types eligible for private offers](https://docs.aws.amazon.com/marketplace/latest/buyerguide/buyer-private-offers-types.html)

Negotiate the deal with the client, then create a private offer in the Marketplace console with the agreed pricing, legal terms, payment schedule, expiration date, and buyer AWS account IDs. Only the targeted accounts can view and accept the offer; the buyer must sign in to the correct account and accept before the offer expires. [AWS private offer workflow](https://docs.aws.amazon.com/marketplace/latest/userguide/private-offers-overview.html)

A Limited SaaS listing is visible only to your account and allowlisted accounts; a public listing can still have private offers with confidential pricing. For a nonpublic sales setup, confirm the supported workflow with AWS Seller Operations: the Catalog API supports private offers on eligible Limited products, while the console FAQ lists a paid public-product prerequisite for accessing private offers. [SaaS listing visibility](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-product-lifecycle.html), [Catalog API private offers](https://docs.aws.amazon.com/marketplace/latest/developerguide/work-with-private-offers.html), [Console prerequisites](https://docs.aws.amazon.com/marketplace/latest/userguide/private-offer-faq.html)

For a small client base buying an ongoing software service at flat prices, SaaS contracts through private offers are a practical starting point. Contract-only products require entitlement checks but no usage metering. Choose the offer structure based on the commercial terms and buyer preferences; client count does not determine the pricing model. [AWS contract integration requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-contracts.html)

Public SaaS contract durations include 1, 12, 24, and 36 months. Customers can agree to automatic renewal. SaaS contract private offers also support custom durations up to 144 months. [AWS SaaS contract pricing](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-contracts.html)

Contract duration and payment frequency are different. A 12-month commitment paid in monthly installments is still an annual commitment. Monthly invoicing does not imply month-to-month cancellation.

For an annual agreement with installments, use a private offer with a flexible payment schedule supported by the selected product type. Define billing dates, amounts, renewal terms, and cancellation conditions.

Define each billable unit precisely, including GB versus GiB, rounding, treatment of retries or reprocessing, included allowances, reset periods, and overage calculations. You must track consumption against purchased capacity to determine the billable excess.

SaaS product charges must be billed entirely through the listed Marketplace dimensions. You cannot collect customer credit card or bank account information for the SaaS product. [AWS customer information requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-guidelines.html)

## Example Commercial Structures

The following prices are illustrative.

| Offer | Commitment | Software charge |
| -------------------------------------- | ---------------------------------------------- | ---------------------------------------------- |
| Monthly contract | 1 month | $5,000 upfront for the month |
| Annual contract | 12 months | $54,000 upfront for the year |
| Annual private offer with installments | 12 months | $4,500 on each of 12 scheduled billing dates |
| Usage-based subscription | Metered consumption | $2 per GB processed, billed monthly |
| Contract plus overages | Purchased capacity plus additional consumption | Fixed contract price plus metered excess usage |

If the application runs in the customer's account, the customer also pays for its compute, database, storage, networking, and other AWS resources. If it runs in your account, you pay those infrastructure costs and price your software accordingly.

## Customer and Seller Flow

1. You complete seller eligibility, tax, banking, and disbursement setup, then create the product with pricing, terms, support information, and fulfillment instructions. Test the integration with allowed accounts and obtain AWS approval before public launch.
1. The customer subscribes to the public listing or accepts a private offer using their AWS account.
1. For SaaS, the customer completes registration on your fulfillment page. Your backend resolves the Marketplace registration token and associates the purchase license with your customer record.
1. You confirm that the subscription is active or the contract provides sufficient entitlement before provisioning access or deploying the application. Resolving the registration token alone does not establish authorization.
1. Your integration keeps access aligned with the license status and reports billable usage when required.
1. AWS bills the customer through Marketplace and, after collecting payment, disburses proceeds to you under the applicable seller payment terms, minus applicable fees and adjustments.
1. You process subscription changes, renewals, expiration, and cancellation events to keep application access aligned with the agreement.

The purchase, authorization, and testing requirements depend on the pricing model. [Seller setup](https://docs.aws.amazon.com/marketplace/latest/userguide/user-guide-for-sellers.html), [SaaS contract integration](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-integrate-contract.html), [SaaS subscription integration](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-integrate-subscription.html)

AWS handles the payment channel. You remain responsible for pricing, usage accuracy, customer support, refund handling, and internal accounting.

## Technical Integration

### SaaS Licensing and Lifecycle

Since June 1, 2026, new SaaS products must support Concurrent Agreements, which allow multiple active purchases of the same product in one AWS account. New integrations must use `CustomerAWSAccountId` and `LicenseArn` for customer and license identification, and Amazon EventBridge for lifecycle notifications. Older listings can retain their existing integration until they opt in. [AWS Concurrent Agreements integration guide](https://aws.amazon.com/blogs/awsmarketplace/complete-guide-to-upgrading-your-saas-product-to-aws-marketplace-concurrent-agreements/)

SaaS onboarding requires a fulfillment landing page that accepts AWS's HTTP POST containing the temporary `x-amzn-marketplace-token` and lets the buyer create or link an application account. Your backend calls the Marketplace Metering Service `ResolveCustomer` API to resolve the token. Persist the returned `CustomerAWSAccountId`, `LicenseArn`, and product identifiers. Define how multiple licenses map to application tenants and which license pays for each unit of usage; an account and product pair no longer uniquely identifies a purchase. [AWS SaaS onboarding requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-integrate-contract.html)

For SaaS contracts, call the Marketplace Entitlement Service `GetEntitlements` API with the `LICENSE_ARN` filter to determine purchased quantities and expiration for the relevant license. Pure usage-based subscriptions do not use `GetEntitlements`; their access state comes from subscription lifecycle events. [Contract integration](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-integrate-contract.html), [subscription integration](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-integrate-subscription.html)

Marketplace sends agreement and license events to your default EventBridge bus with source `aws.agreement-marketplace`. Create rules in `us-east-1`; in the console, select AWS services and AWS Marketplace Agreements and Licenses. Route matching events to a handler, such as Lambda or an SQS queue with a consumer. [AWS SaaS EventBridge integration](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-eventbridge-integration.html), [Rule region requirements](https://aws.amazon.com/blogs/awsmarketplace/complete-guide-to-upgrading-your-saas-product-to-aws-marketplace-concurrent-agreements/)

For direct sales, handle the following event types. Renewals and replacements create new agreements, while cancellation, expiration, and termination produce agreement-ended events. Channel partner sales use the applicable manufacturer agreement events instead. [AWS event types and schemas](https://docs.aws.amazon.com/marketplace/latest/userguide/notifications-eventbridge.html)

| Event (`detail-type`, for direct sales) | Action |
| -------------------------------------- | ------ |
| `Purchase Agreement Created - Proposer` | Record the new, renewed, or replacement agreement |
| `Purchase Agreement Amended - Proposer` | Update the agreement record |
| `Purchase Agreement Ended - Proposer` | Process cancellation, expiration, or termination |
| `License Updated - Manufacturer` | Refresh contract entitlements and update access |
| `License Deprovisioned - Manufacturer` | Begin offboarding and flush final billable usage |

The event handler complements the fulfillment page and registration APIs; both are needed. Make event processing safe to retry, reconcile access state periodically, and handle future-dated agreements without granting access before activation. Some AWS documentation still includes legacy SNS examples; use the Concurrent Agreements guide as the baseline for a new listing.

### Usage Metering

For usage-based pricing or contract overages, submit billable quantities through `BatchMeterUsage`. Include `LicenseArn` in each usage record. During a migration, sending both legacy `ProductCode`-based and license-based records for the same usage window can cause duplicate billing. [AWS BatchMeterUsage API reference](https://docs.aws.amazon.com/marketplace/latest/APIReference/API_marketplace-metering_BatchMeterUsage.html)

- Aggregate and finalize usage for each license, customer, dimension, and UTC hour before submission. AWS deduplicates records for that combination; multiple submissions are not summed, and a later quantity does not amend the original.
- Report usage hourly and keep durable usage records so failed submissions can be retried and reconciled with AWS billing reports.
- Retry transient failures and `UnprocessedRecords`; inspect each record's result rather than treating a successful HTTP response as confirmation that every record was billed.
- Submit usage within 24 hours of the recorded event. At month end, submit previous-month usage before 06:00 UTC on the first day of the next month, even if the normal reporting window would extend later.
- On cancellation or termination of a usage-based agreement, immediately flush remaining usage for that license. The `License Deprovisioned - Manufacturer` event starts the one-hour final reporting window. Other active licenses for the customer remain separate. [Final usage reporting requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/saas-eventbridge-integration.html)

These deadlines can cause unreported usage to go unbilled. Monitor submission failures and reporting lag. [AWS metering requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/metering-for-usage.html)

### Deployment Operations

AMI and container contract products use AWS License Manager integrations for license checks. The SaaS entitlement integration does not apply unchanged to deployable products.

For customer-hosted deployments, define least-privilege deployment and support roles, an upgrade process, and any outbound connectivity needed for licensing or metering.

For multi-tenant deployments, instrument tenant usage and define how shared infrastructure costs are allocated.

## Fees and Procurement

Marketplace fees vary by product type and offer structure. The standard software listing fees below were verified on October 4, 2026. [AWS listing fee schedule](https://docs.aws.amazon.com/marketplace/latest/userguide/listing-fees.html)

Private offer tiers apply to each deal's pre-tax total contract value (TCV). Selling more deals does not move existing deals into a lower fee tier. For new deals below $1M TCV, budget a 3% standard fee; qualifying renewals use the 1.5% standard rate.

| Offer structure | Standard listing fee |
| ------------------------------------------------ | -------------------- |
| Public SaaS offer | 3% |
| Public AMI or container offer | 20% |
| Private offer with total contract value below $1M | 3% |
| Private offer from $1M to below $10M | 2% |
| Private offer of $10M or more | 1.5% |
| Qualifying private offer renewal | 1.5% |

Channel partner private offers add 0.5 percentage points to the standard fee, and regional uplifts can also apply. South Korea adds 1 percentage point, so a new private offer below $1M TCV sold to a buyer there has a 4% total fee before any channel partner uplift. Confirm renewal eligibility and the applicable fee schedule before quoting. [AWS fee uplifts](https://docs.aws.amazon.com/marketplace/latest/userguide/listing-fees.html)

At a standard 3% listing fee, the illustrative $54,000 annual sale leaves $52,380 before infrastructure, support, and other operating costs, assuming no additional fees, taxes, or refunds. A qualifying renewal at the same price and a 1.5% fee leaves $53,190.

The listing fee is a percentage of transaction proceeds, deducted after the buyer pays. Budget separately for the engineering and infrastructure needed to build and maintain the integration. [AWS seller fee explanation](https://d1.awsstatic.com/awsmp/solutions/aws-seller-faq.pdf)

Your disbursement timing is separate from the customer's billing schedule. AWS disburses funds only after collecting customer payment, so invoice dates do not guarantee cash receipt on those dates. Model collection delays and refunds, especially when you fund the customer's infrastructure. [AWS disbursement requirements](https://docs.aws.amazon.com/marketplace/latest/userguide/managing-disbursements.html)

Marketplace can simplify purchasing through an existing AWS relationship, but customers may still require security reviews, legal review, vendor approval, and contract negotiation.

Eligible Marketplace purchases can count toward a buyer's AWS committed spend, including EDP or PPA commitments. Confirm product eligibility and the buyer's agreement limits with their AWS account team before promising that benefit. [AWS committed-spend benefits](https://aws.amazon.com/blogs/awsmarketplace/private-offer-auto-renewals-scale-predictable-revenue-with-aws-marketplace/)

Before investing in the integration, ask target clients whether they want to purchase through AWS. For a small client base, compare the buyer's procurement benefits and eligible committed-spend drawdown with the implementation effort and fees. Direct invoicing or a separate sales channel using a billing provider such as Stripe may be simpler when clients have no AWS purchasing requirement.

Define support and SLA terms, refund approval and processing, agreement amendments, and renewal ownership. Offboarding should cover access revocation, data export and retention, deletion, and the disposition of customer resources.

## Decisions Before Implementation

- Confirm buyer AWS account readiness and demand for Marketplace procurement, and verify any committed-spend eligibility.
- Choose customer-hosted, vendor-hosted dedicated, or vendor-hosted multi-tenant deployment.
- Select the Marketplace product type based on delivery and management responsibilities.
- Choose public or nonpublic listing visibility and confirm the private-offer workflow and buyer allowlisting requirements.
- Identify any required AMI or container add-on listings and customer deployment requirements.
- Define fixed pricing, usage pricing, or a contract with overages, including billable units and allowance accounting.
- Set contract duration separately from payment frequency and renewal behavior.
- Decide how tenants, customer AWS accounts, and multiple purchase licenses relate, including usage allocation per license.
- Define deployment ownership, support access, upgrades, data handling, and offboarding.
- Complete seller eligibility, tax, banking, and disbursement setup.
- Model net revenue and cash flow using applicable fees, infrastructure costs, and collection timing.
- Test successful and failed purchases, registration, insufficient entitlements, concurrent licenses, future-dated activation, entitlement changes, metering retries, cancellation, and expiration before launch.
