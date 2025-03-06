# Business Terminology

### Revenue & Sales Metrics
- Revenue (Sales, Turnover): Total income from sales before expenses.

- Gross Revenue: Total sales before deducting returns, discounts, or allowances.

- Net Revenue: Revenue after deductions like returns and discounts.

- Annual Recurring Revenue (ARR): Revenue expected per year from subscriptions.

- Monthly Recurring Revenue (MRR): Revenue expected per month from subscriptions.

- Average Revenue Per User (ARPU): Revenue generated per customer on average.

---

### Profitability Metrics
- Gross Profit: Revenue minus Cost of Goods Sold (COGS).  
  - Formula: Gross Profit = Revenue - COGS

- Gross Margin: Percentage of revenue retained after COGS.  
  - Formula: (Gross Profit / Revenue) × 100

- Operating Profit: Earnings before interest and taxes (EBIT).  
  - Formula: Operating Profit = Gross Profit - Operating Expenses

- Net Profit (Net Income): Final profit after all expenses, including taxes and interest.  
  - Formula: Net Profit = Total Revenue - Total Expenses

- Profit Margin: Profit as a percentage of revenue.  
  - Formula: (Net Profit / Revenue) × 100

- EBITDA (Earnings Before Interest, Taxes, Depreciation, and Amortization): Indicator of operational profitability without non-cash expenses.
    - EBITDA is a financial metric that measures a company's profitability before accounting for interest expenses, taxes, depreciation, and amortization. It is commonly used to evaluate a company's operating performance and compare profitability across companies and industries.
    - It measures core profitability, it compares companies fairly, and is often used in valuations to estimate a company's value relative to earnings
    - Its limitations are that it ignores debt and interest, excludes capital expenditures like manufacturing, and is not a GAAP (generally accepted accounting prinicples) metric so some companies may calculate it differently for their own gains

---

### Cash Flow Metrics
- Cash Flow: Movement of cash in and out of the business.

- Operating Cash Flow (OCF): Cash generated from core business activities.

- Free Cash Flow (FCF): Cash left after capital expenditures (CapEx).  
  - Formula: FCF = OCF - CapEx

- Cash Burn Rate: How fast a company is using its cash reserves.

- Runway: How long a company can operate before running out of cash.  
  - Formula: Runway = Cash Balance / Burn Rate

---

### Efficiency & Performance Metrics
- Return on Investment (ROI): Measures profitability of an investment.  
  - Formula: (Net Profit / Investment Cost) × 100

- Return on Assets (ROA): Efficiency in using assets to generate profit.  
  - Formula: (Net Income / Total Assets) × 100

- Return on Equity (ROE): Profitability relative to shareholders' equity.  
  - Formula: (Net Income / Shareholders’ Equity) × 100

- Working Capital: Short-term liquidity measure.  
  - Formula: Current Assets - Current Liabilities

- Asset Turnover Ratio: Efficiency in generating sales from assets.  
  - Formula: Revenue / Total Assets

---

### Valuation Metrics
- Market Capitalization (Market Cap): Value of a company based on stock price.  
  - Formula: Share Price × Number of Shares

- Enterprise Value (EV): Total value of a company, including debt and cash.  
  - Formula: Market Cap + Debt - Cash

- Price-to-Earnings (P/E) Ratio: Valuation metric comparing stock price to earnings.  
  - Formula: Stock Price / Earnings per Share (EPS)

- Price-to-Sales (P/S) Ratio: Compares stock price to revenue per share.  
  - Formula: Market Cap / Revenue

- EV/EBITDA: Compares enterprise value to EBITDA for valuation.

---

### Growth & Retention Metrics
- Customer Acquisition Cost (CAC): Cost to acquire a new customer.  
  - Formula: Total Sales & Marketing Expenses / Number of New Customers

- Customer Lifetime Value (LTV): Total revenue expected from a customer over their lifetime.  
  - Formula: (ARPU × Gross Margin %) × Average Customer Lifespan

- Churn Rate: Percentage of customers lost over a period.  
  - Formula: (Lost Customers / Total Customers) × 100

- Retention Rate: Percentage of customers retained.  
  - Formula: 100% - Churn Rate

- Net Promoter Score (NPS): Measures customer satisfaction and loyalty.

## Tools

## 1. Customer Data Platform (CDP)
- Purpose: Unifies first-party customer data from multiple sources (web, mobile, CRM, transactions, etc.) into a single customer profile.
- Key Features:
  - Identity resolution (matching customer identities across sources)
  - Real-time customer segmentation
  - Data activation (syncing data with marketing tools, analytics)
  - Personalization & customer journey tracking
- Use Case: A company wants to combine web behavior, purchase history, and email engagement into a unified customer profile for better marketing.
- Examples:
  - Segment (by Twilio)
  - Tealium
  - Salesforce CDP
  - Adobe Experience Platform
  - mParticle
  - RudderStack

📌 CDP vs CRM: CDPs focus on aggregating and unifying raw customer data for insights and marketing activation, while CRMs are built for managing direct interactions with known customers.

## 1️⃣ CDP APIs (Customer Data Platform)
📌 Purpose: CDPs unify and manage customer data from multiple sources for analytics, personalization, and activation.  

### Common CDP APIs & What They're Used For
| API Type | Use Cases | Example Providers |
|-------------|-------------|-----------------|
| Data Ingestion API | Send event data (clicks, purchases, logins) from apps, websites, CRMs, and other sources. | Segment, mParticle, Tealium |
| Identity Resolution API | Merge customer identities across multiple touchpoints. | Segment, Adobe Real-time CDP |
| Profile Enrichment API | Append third-party data to customer profiles. | Liveramp, Amperity |
| Audience API | Create and update audience segments dynamically. | BlueConic, Treasure Data |
| Data Export API | Send customer data to analytics, BI, and advertising platforms. | RudderStack, Segment |
| Event Streaming API | Send real-time data to marketing automation or personalization tools. | Tealium EventStream, Segment |

### Example Use Case:
📌 Real-time Personalization:  
- Use Segment's Data Ingestion API to collect customer activity.  
- Call the Identity Resolution API to unify cross-device behavior.  
- Use the Audience API to create a “High-Value Customers” segment.  
- Push data to a CRM (Salesforce) or CEP (Braze) for marketing actions.  

---

## 2. Customer Relationship Management (CRM)
- Purpose: Tracks and manages direct interactions with customers (sales, support, marketing, etc.).
- Key Features:
  - Contact management (name, email, phone, notes)
  - Sales pipeline tracking (lead status, deals, opportunities)
  - Customer support and ticketing
  - Marketing automation (email campaigns, workflows)
- Use Case: A sales team tracks deals in a pipeline, logs customer calls, and automates follow-ups.
- Examples:
  - Salesforce CRM
  - HubSpot CRM
  - Microsoft Dynamics 365
  - Zoho CRM
  - Pipedrive

📌 CRM vs CDP: CRMs store structured customer interactions for business operations (e.g., sales, customer support), whereas CDPs unify raw behavioral data for broader customer insights.

## 2️⃣ CRM APIs (Customer Relationship Management)
📌 Purpose: CRMs store customer interactions, sales data, and support tickets to manage relationships across marketing, sales, and support teams.  

### Common CRM APIs & What They're Used For
| API Type | Use Cases | Example Providers |
|-------------|-------------|-----------------|
| Contacts API | Create, update, or retrieve customer records. | Salesforce, HubSpot, Zoho CRM |
| Leads API | Add and manage potential customers. | Salesforce, Pipedrive |
| Opportunities API | Track and manage sales deals. | Dynamics 365, Close CRM |
| Activity Logging API | Log emails, calls, and meetings. | Salesforce, HubSpot |
| Workflow Automation API | Automate lead scoring, follow-ups, and notifications. | HubSpot, Zoho CRM |
| Reporting & Analytics API | Extract sales performance data. | Salesforce, SugarCRM |
| Integration API | Connect CRM with other tools (CDP, ERP, Support, etc.). | Salesforce, Microsoft Dynamics 365 |

### Example Use Case:
📌 Automating Lead Nurturing in HubSpot CRM  
- Capture form submissions via a Webhooks API.  
- Use the Leads API to add new contacts to HubSpot.  
- Use the Workflow Automation API to trigger an email sequence.  
- Pull engagement data via the Reporting API to measure lead conversion.  

---

## 3. Customer Engagement Platforms (CEP)
- Purpose: Automates multi-channel customer engagement (email, SMS, push notifications, in-app messages).
- Key Features:
  - Omnichannel messaging
  - AI-driven personalization
  - Behavioral triggers (e.g., sending an offer if a customer abandons their cart)
- Use Case: A retail company sends automated email and SMS follow-ups based on customer browsing behavior.
- Examples:
  - Braze
  - Iterable
  - CleverTap
  - MoEngage

📌 CEP vs CDP: CEPs focus on engagement and messaging, while CDPs unify data to power those engagements.

## 3️⃣ CEP APIs (Customer Engagement Platform)
📌 Purpose: CEPs manage real-time, personalized customer engagement across channels (email, SMS, push notifications, in-app messages).  

### Common CEP APIs & What They're Used For
| API Type | Use Cases | Example Providers |
|-------------|-------------|-----------------|
| Messaging API | Send personalized SMS, emails, push notifications. | Twilio, Braze, Iterable, OneSignal |
| Behavioral Triggers API | Trigger real-time engagement based on customer actions. | Braze, MoEngage, Airship |
| Campaign Management API | Create, schedule, and manage marketing campaigns. | Iterable, Klaviyo |
| Event Tracking API | Capture customer behavior and trigger automations. | Customer.io, Braze |
| A/B Testing API | Run experiments on messaging effectiveness. | Optimizely, Braze |
| Audience Segmentation API | Create dynamic audience segments based on engagement. | Cordial, Twilio Segment |
| Multichannel Orchestration API | Coordinate messaging across SMS, push, email, and in-app. | OneSignal, Braze |

### Example Use Case:
📌 Personalized Push Notification Campaign Using Braze  
- Use a CDP (Segment) to track user behavior (e.g., abandoned cart).  
- Call Braze’s Behavioral Triggers API to send a push notification.  
- Use A/B Testing API to test different messages.  
- Capture engagement via the Event Tracking API and refine messaging.  


## Startup

### How a Startup Gets Off the Ground & Acquires Funding 🚀  

Starting and scaling a startup involves securing funding, proving market fit, and generating revenue. The journey usually follows these stages:  

---

## 1️⃣ Ideation & Validation (Pre-Seed Stage)  
📌 Goal: Validate the business idea before raising money.  

### Steps to Get Started:  
✔ Market Research: Identify the problem, market demand, and competitors.  
✔ Minimum Viable Product (MVP): Build a simple version of the product.  
✔ Customer Validation: Get early adopters and feedback.  
✔ Form a Legal Entity: Register as an LLC, C-Corp, or S-Corp (C-Corp is common for venture-backed startups).  
    - Most venture capital (VC) firms will only invest in C-Corps.
    - They prefer C-Corps because they allow for multiple classes of stock (common vs preferred shares) which is essential for structuring equity investments
    - LLCs and S-Corps doesn't support preferred stock, making them unattractive to VCs
    - C-Corps are best for issuing stock options (ISOs, RSUs etc)
    - Most startups offer stock-based comp to attract & retain talent, 409A valuations make this easier
    - C-Corps have double taxation (corporate tax + personal tax on dividends), but most dont pay dividends they just re-invest the profits
✔ Bootstrapping or Pre-Seed Funding: Use personal savings or raise a small amount from friends, family, or angel investors.  

Funding Options at This Stage:  
✅ Personal savings (Bootstrapping)  
✅ Angel investors (high-net-worth individuals)  
✅ Incubators/accelerators (e.g., Y Combinator, Techstars)  

---

## 2️⃣ Seed Funding (Product-Market Fit & Early Growth)  
📌 Goal: Get initial users, refine the product, and achieve early traction.  

### What Happens at This Stage?  
✔ Refining the Business Model: Determine revenue streams (e.g., SaaS subscriptions, e-commerce sales).  
✔ Scaling MVP to a Functional Product: Improve UX and features.  
✔ Gaining Early Customers & Revenue: Start generating initial earnings.  
✔ Raising a Seed Round: Secure funding to scale operations.  

Funding Options at This Stage:  
✅ Venture Capitalists (VCs): Seed investors provide $500K–$2M for equity.  
✅ Angel Investors: Individuals investing in early-stage startups.  
✅ Crowdfunding: Platforms like Kickstarter, Indiegogo.  
✅ Revenue-Based Financing: Funds based on projected revenue.  

Valuation:  
- Valuations at the seed stage are often based on founder experience, market potential, and early traction (not profits).  
- Investors use SAFE Notes (Simple Agreement for Future Equity) or convertible notes to delay valuation discussions.  

---

## 3️⃣ Series A (Scaling & Revenue Growth)  
📌 Goal: Prove repeatable revenue and scale operations.  

### What Happens at This Stage?  
✔ Expanding Customer Base: Growth marketing, sales teams.  
✔ Refining Monetization Strategy: Optimizing pricing, CAC vs. LTV.  
✔ Hiring Key Talent: Bringing in executives (e.g., CTO, CMO, CFO).  
✔ Expanding to New Markets or Products.  

Funding Options at This Stage:  
✅ Series A Venture Capitalists: Invest $5M–$20M in exchange for equity.  
✅ Strategic Investors: Large companies looking for partnerships.  

Valuation Methods Used:  
🔹 Revenue Multiples: If a SaaS startup is making $5M ARR, VCs may value it at 5–10x revenue, meaning a $25M–$50M valuation.  
🔹 Comparable Company Analysis (CCA): Comparing similar startups' valuations.  

---

## 4️⃣ Series B & Beyond (Scaling to a Large Market)  
📌 Goal: Expand globally, improve profitability, prepare for an IPO or acquisition.  

### What Happens at This Stage?  
✔ Aggressive Expansion: Hiring, partnerships, international growth.  
✔ Market Domination: Competing with industry leaders.  
✔ Profitability & Unit Economics: Improving margins.  

Funding Options at This Stage:  
✅ Series B/C/D Rounds: VCs invest $20M+ for rapid scaling.  
✅ Debt Financing: Borrowing instead of selling equity.  
✅ Strategic Acquisitions: Buying smaller competitors.  

Valuation Methods Used:  
🔹 Discounted Cash Flow (DCF): Future revenue projections discounted to present value.  
🔹 EBITDA Multiples: Valuing based on profitability.  
🔹 Market Comparisons: Benchmarking against competitors.  

---

## 5️⃣ Exit Strategy: IPO, Acquisition, or Staying Private  
📌 Goal: Allow investors and founders to cash out.  

### Options for an Exit:  
✔ Initial Public Offering (IPO): Selling shares on the stock market.  
✔ Acquisition: Selling the company to a larger firm.  
✔ Staying Private & Profitable: Becoming a long-term private business.  

Earnings & Valuation Metrics at Exit:  
📊 Earnings Before Interest, Taxes, Depreciation, and Amortization (EBITDA) → Measures profitability.  
📊 Revenue Growth Rate → Key for high-growth tech startups.  
📊 Public Market Comparables → If IPO, valuation is based on peers like Snowflake, Shopify, etc.  

---

## Final Thoughts 💡  
- Early-stage startups (Pre-seed, Seed, Series A) focus on growth, product-market fit, and user acquisition rather than profits.  
- Late-stage startups (Series B and beyond) focus on scaling revenue and optimizing profitability.  
- Valuation methods evolve from potential-based (Seed) to revenue-based (Series A/B) to EBITDA-based (IPO).  
