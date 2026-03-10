# Payment Processing

## 1. Cash Transactions

The simplest form of payment. No intermediaries, no fees, no technology required.

**How it works:**

- Buyer hands physical currency to seller
- Seller verifies the amount (and optionally checks for counterfeits)
- Transaction is complete immediately — settlement is instant
- Seller provides a receipt (optional, but standard in retail)

**Key characteristics:**

- No third parties involved
- No transaction fees
- Immediate finality — once cash changes hands, it's done
- Anonymous by nature
- Risk sits with whoever holds the cash (theft, loss, counterfeiting)
- No chargeback mechanism — the buyer has no recourse once they hand over the money

**Limitations that drove the need for alternatives:**

- Requires physical proximity between buyer and seller
- Doesn't scale for large amounts (impractical to carry/store)
- No audit trail unless manually recorded
- Can't be used for remote or online transactions
- Security risk of holding large amounts of physical currency

______________________________________________________________________

## 2. Debit Cards (Physical / In-Person)

Debit cards are essentially an electronic interface to your bank checking account. When you swipe or tap, the money comes directly from your existing balance.

### 2.1 The Players Involved

- **Cardholder** — the person paying (you)
- **Issuing bank** — the bank that gave you the debit card and holds your checking account (e.g., Chase, Wells Fargo)
- **Card network** — Visa, Mastercard, or a PIN-based network like Interlink, STAR, NYCE, Pulse
- **Acquiring bank (merchant's bank)** — the bank that receives funds on behalf of the merchant
- **Merchant** — the business accepting payment

### 2.2 Two Processing Paths

Debit cards can be processed two different ways, and the path determines who takes a cut and how much:

**PIN debit (online debit):**

- You enter your PIN at the terminal
- Transaction routes through a PIN debit network (STAR, Pulse, NYCE, etc.)
- Funds are pulled directly from your checking account in near-real-time
- Lower fees for the merchant (often a flat fee like $0.20–$0.30 per transaction)
- The PIN network handles authentication — they know it's you because you entered your PIN

**Signature debit (offline debit):**

- You sign or just tap/swipe without a PIN
- Transaction routes through Visa or Mastercard's network, just like a credit card
- Processed as a "signature" transaction even if no actual signature is collected
- Higher fees for the merchant (percentage-based, similar to credit card interchange)
- Settlement may take 1-2 days rather than being near-instant
- The card network handles fraud risk since there's no PIN verification

### 2.3 The Transaction Flow (PIN Debit)

1. You insert/tap your card and enter your PIN
1. The POS terminal encrypts the card data and PIN, sends it to the merchant's payment processor
1. The processor routes the transaction through the appropriate PIN debit network
1. The network forwards an authorization request to your issuing bank
1. Your bank checks: Is the PIN correct? Is there sufficient balance? Any fraud flags?
1. Bank responds with approve or decline
1. If approved, a hold is placed on the funds in your account
1. Settlement happens later (usually same day) — funds transfer from your bank to the merchant's bank through the network

### 2.4 Fee Structure

- **PIN debit:** Regulated by the Durbin Amendment (for banks with >$10B in assets) — capped at roughly $0.21 + 0.05% per transaction. Smaller banks are exempt and can charge more.
- **Signature debit:** Interchange fees similar to credit cards, typically 0.5–1.5% of the transaction
- **Network assessment fee:** Small fee to Visa/Mastercard (fractions of a percent)

### 2.5 Key Differences from Cash

- Money is still "yours" in your bank account — the card is just an access mechanism
- There's now a paper trail (bank statement)
- A hold may briefly reduce your available balance before final settlement
- Overdraft is possible if your bank allows it (and charges fees for it)
- You have some dispute/fraud protection through your bank

______________________________________________________________________

## 3. Credit Cards (Physical / In-Person)

Credit cards introduce a critical difference from debit: you're spending the bank's money, not yours. The issuing bank is extending you a line of credit and taking on the risk that you'll pay them back.

### 3.1 The Players Involved

Same cast as debit, but with shifted risk dynamics:

- **Cardholder** — you, now a borrower
- **Issuing bank** — extends credit to you, takes on default risk (Chase, Capital One, Amex, etc.)
- **Card network** — Visa, Mastercard, Amex, Discover (routes transactions, sets rules)
- **Acquiring bank / processor** — receives authorization requests from the merchant
- **Merchant** — accepts payment, receives funds minus fees

**Note on Amex and Discover:** These operate as both the card network AND the issuer in many cases (closed-loop networks), which is why they can charge higher merchant fees — they control more of the chain.

### 3.2 The Transaction Flow

1. You tap/insert/swipe your card at the terminal
1. The POS terminal reads card data and sends an authorization request through the merchant's processor
1. The processor sends it to the card network (Visa, MC, etc.)
1. The card network routes it to your issuing bank
1. Your issuing bank checks: Is the card valid? Is there available credit? Any fraud signals? Does this transaction pattern look normal?
1. Bank responds: approved (with authorization code) or declined
1. **Authorization ≠ settlement.** At this point, no money has moved. A hold is placed on your credit line.
1. At end of day (or in batches), the merchant submits a batch of authorized transactions for settlement
1. The card network orchestrates the actual money movement: issuing bank → card network → acquiring bank → merchant's account
1. Settlement typically takes 1-3 business days

### 3.3 The Fee Breakdown (on a $100 purchase)

The merchant pays roughly $2.50–$3.50 total, broken down as:

- **Interchange fee (~1.5–2.5%)** → goes to the issuing bank. This is the biggest piece. Premium/rewards cards have higher interchange because the bank uses this to fund your cashback and points.
- **Network assessment fee (~0.13–0.15%)** → goes to Visa/Mastercard. This is the "toll" for using the rails. Small percentage, but massive volume.
- **Acquirer/processor markup (~0.2–0.5%)** → goes to the merchant's bank and payment processor for their services.

### 3.4 Why Interchange Funds Your Rewards

Your 2% cashback card has a higher interchange rate (~2.1%) than a basic card (~1.5%). The issuing bank collects the higher interchange from the merchant and passes a portion back to you as rewards. The merchant is effectively subsidizing your points — which is why some merchants push you toward debit or offer cash discounts.

### 3.5 Chargebacks

A major feature of credit cards: the cardholder can dispute a charge. The issuing bank can reverse the transaction, pulling money back from the merchant. This shifts fraud risk heavily toward merchants — they lose both the product and the payment if a chargeback is successful. This dispute mechanism doesn't exist with cash and is weaker with debit.

### 3.6 Key Differences from Debit

- You're borrowing money, not spending your own
- Interest accrues if you don't pay in full each billing cycle (15–30% APR)
- Stronger fraud protection and dispute rights (Fair Credit Billing Act)
- Higher merchant fees (especially for rewards cards)
- Authorization and settlement are decoupled — auth is instant, money moves later
- Credit utilization affects your credit score

______________________________________________________________________

## 4. Electronic / Online Transactions

Moving from physical card-present transactions to card-not-present (CNP) transactions introduces new challenges around trust, security, and fraud.

It's important to note Stripe in this case acts as a Payment Processor + Gateway + Merchant Account (PayFac model), so the flow is simplified for the merchant but still involves all the same underlying components.

### 4.1 The Core Problem

In a physical transaction, the card is present, you can verify the cardholder, and the terminal reads the chip (which contains a cryptographic key). Online, none of that exists. The merchant never sees the card or the person. This makes CNP transactions significantly higher risk for fraud, which is why online transaction fees are higher.

### 4.2 How a Basic Online Payment Works

1. Customer enters card number, expiration, CVV, and billing address on the merchant's website
1. The merchant's server sends this data to their payment processor
1. The processor routes it through the card network to the issuing bank (same as physical)
1. The issuing bank runs additional checks: CVV match, AVS (address verification), 3D Secure challenge if enrolled, fraud scoring
1. Approve or decline response flows back
1. Settlement follows the same batch process as physical transactions

### 4.3 Security Layers for Online Payments

**PCI DSS (Payment Card Industry Data Security Standard):**

- Any entity that stores, processes, or transmits cardholder data must comply
- 4 levels based on transaction volume, with Level 1 being the most rigorous (on-site audit)
- This is why most businesses don't want raw card data touching their servers — the compliance burden is enormous

**Tokenization:**

- Raw card numbers are replaced with a token (a random string) that's useless if stolen
- The payment processor/gateway stores the actual card number in their secure vault
- The merchant only ever sees and stores the token
- This is how "save my card for next time" works without the merchant holding your actual card number

**3D Secure (3DS) / Verified by Visa / Mastercard SecureCode:**

- An additional authentication step where the issuing bank challenges you (password, OTP to your phone, biometric)
- Shifts fraud liability from the merchant to the issuing bank if the cardholder authenticates successfully
- 3DS2 (current version) is less intrusive — often runs a risk assessment silently and only challenges suspicious transactions

**CVV / CVC:**

- The 3-4 digit code on the card that proves you physically have (or had) the card
- Not stored in the magnetic stripe or chip, so it can't be skimmed from physical transactions
- Merchants are prohibited from storing CVVs after authorization

**AVS (Address Verification Service):**

- Compares the billing address provided with the address on file at the issuing bank
- Returns a match/partial match/no match code
- Merchants use this as one signal in their fraud decision

### 4.4 Card-Not-Present Fraud Economics

CNP fraud rates are significantly higher than card-present (~0.1% vs ~0.01%). This is why:

- Online interchange rates are higher than in-store
- Merchants invest heavily in fraud detection
- Chargebacks are more common online
- 3DS and additional verification steps exist

______________________________________________________________________

## 5. Payment Gateways and Payment Processors

These are the intermediary services that sit between the merchant and the card networks / banking system. They're often confused with each other, but they serve different functions.

### 5.1 Payment Gateway

**What it does:** The gateway is the front door. It securely collects and transmits payment data from the customer to the processor. Think of it as the online equivalent of the physical card terminal.

**Responsibilities:**

- Encrypts card data at the point of entry (in the browser or app)
- Transmits the encrypted data to the payment processor
- Returns the authorization response to the merchant
- Handles tokenization (replacing card numbers with tokens for storage)
- Provides the merchant-facing API or checkout interface

**Examples:** Authorize.net, Braintree (gateway layer), NMI, PayPal Payments Pro

### 5.2 Payment Processor

**What it does:** The processor handles the actual transaction routing and money movement. It sits between the gateway and the card networks/banks.

**Responsibilities:**

- Routes authorization requests to the correct card network
- Handles settlement — batching transactions and facilitating fund transfers
- Manages communication with acquiring banks
- Performs fraud screening and risk assessment
- Handles compliance and reporting

**Examples:** First Data (now Fiserv), Worldpay, Chase Paymentech, Adyen (processor layer)

### 5.3 How They Work Together

```
Customer → [Gateway] → [Processor] → [Card Network] → [Issuing Bank]
   ↑                                                          |
   └──────────── authorization response ───────────────────────┘
```

The gateway captures the data and encrypts it. The processor routes it and handles the financial plumbing. In many modern setups, a single company provides both (Adyen, for example, is both gateway and processor).

### 5.4 Acquiring Bank (Merchant Account)

The merchant also needs a relationship with an acquiring bank — this is the bank that receives settlement funds on behalf of the merchant. Traditionally, you'd need to apply for a "merchant account" through an acquiring bank, which involves underwriting (they assess your business risk, chargeback rates, industry type, etc.).

This merchant account setup is:

- Time-consuming (days to weeks for approval)
- Involves credit checks and business documentation
- Has negotiated rates based on your volume and risk profile
- Can be terminated if your chargeback rate gets too high

This is the layer that managed providers like Stripe abstract away.

______________________________________________________________________

## 6. Managed Providers (Stripe, Square, etc.)

Managed payment providers bundle everything from the previous sections into a single integration. They are the reason a solo developer can start accepting payments in an afternoon instead of spending weeks setting up merchant accounts, gateway contracts, and processor relationships.

### 6.1 What Stripe Actually Does

Stripe acts as a **payment facilitator (PayFac)**. Instead of each merchant having their own merchant account with an acquiring bank, Stripe has a master merchant account. Your business operates as a sub-merchant under Stripe's umbrella.

**What this means in practice:**

- No merchant account application or underwriting process
- Instant onboarding — sign up, add your bank account, start accepting payments
- Stripe handles PCI compliance, fraud detection, tokenization, gateway, and processing
- You interact with a single API, Stripe handles everything downstream
- Stripe settles funds to your bank account on a rolling basis (typically T+2)

### 6.2 The Stripe Transaction Flow

1. Customer enters payment info using Stripe Elements (client-side JS library) or Stripe Checkout (hosted page)
1. Card data goes directly from the customer's browser to Stripe's servers — never touches your server
1. Stripe tokenizes the card data and returns a token to your backend
1. Your backend creates a PaymentIntent or Charge using the token via the Stripe API
1. Stripe routes the transaction through their processor/acquiring bank to the card network and issuing bank
1. Authorization response comes back to Stripe, then to your backend via API response
1. Stripe handles settlement, depositing funds to your bank minus their fee

**What you as the developer handle:**

- Integrating Stripe's SDK/API into your frontend and backend
- Creating checkout flows (what products, how much, what currency)
- Listening for webhooks to confirm payment events (payment succeeded, failed, disputed)
- Managing subscription lifecycle if applicable (plan changes, cancellations, dunning)
- Fulfilling orders (granting access, shipping products, etc.)

### 6.3 Subscription Management

For recurring billing, Stripe (and similar providers) manage:

- **Plan/price creation** — you define products with recurring prices (e.g., $10/month, $100/year)
- **Customer creation** — Stripe stores the customer's payment method securely
- **Automatic billing** — Stripe charges the customer on the schedule you define
- **Dunning / retry logic** — if a payment fails (expired card, insufficient funds), Stripe automatically retries on a configurable schedule
- **Proration** — if a customer upgrades mid-cycle, Stripe calculates and charges the difference
- **Webhooks for lifecycle events:**
  - `invoice.paid` — payment succeeded, grant/maintain access
  - `invoice.payment_failed` — payment failed, maybe notify user to update card
  - `customer.subscription.updated` — plan change
  - `customer.subscription.deleted` — cancellation, revoke access

### 6.4 Fee Structure

Stripe's standard pricing:

- **2.9% + $0.30** per successful card charge (US domestic)
- **+1.5%** for international cards
- **+0.5%** for manually entered cards
- No monthly fees, no setup fees, no minimum volume

Where that 2.9% goes (approximately):

- ~1.8% to the issuing bank (interchange — Stripe passes this through)
- ~0.13% to the card network (assessment)
- ~1% to Stripe (their margin, covering gateway, processing, fraud tools, support, infrastructure)

### 6.5 PCI Compliance Simplification

This is one of the biggest value props. By using Stripe Elements or Checkout:

- Card data never touches your server
- You qualify for **SAQ-A** — the simplest PCI self-assessment (about 20 questions)
- Compare this to handling card data yourself, which requires **SAQ-D** (300+ requirements) or a full on-site audit at the highest volume levels
- Stripe maintains their own PCI Level 1 certification (the most stringent)

### 6.6 Comparison: DIY Stack vs. Managed Provider

| Concern | DIY (Gateway + Processor + Merchant Account) | Managed (Stripe) |
| ----------------------- | -------------------------------------------- | ---------------------------------------- |
| Setup time | Days to weeks | Minutes to hours |
| Merchant account | Required, involves underwriting | Not needed (Stripe is the PayFac) |
| PCI burden | High (SAQ-D or on-site audit) | Low (SAQ-A) |
| Fraud detection | You build or buy separately | Built-in (Stripe Radar) |
| Transaction fees | Negotiable, can be lower at volume | Fixed 2.9% + $0.30 |
| Subscription billing | Build yourself or add another vendor | Built-in (Stripe Billing) |
| Control / customization | Full control | Some constraints (Stripe's rules/limits) |
| Payouts | Direct from acquiring bank | Stripe batches and deposits (T+2) |

### 6.7 Mobile App Considerations

For digital goods sold through iOS or Android apps:

- **Apple App Store and Google Play require their in-app purchase (IAP) systems** for digital products and subscriptions
- They take a 15–30% commission (15% for small businesses or after the first year of a subscription)
- You cannot use Stripe/direct payment for digital goods inside mobile apps — this violates store policies
- Physical goods and real-world services are exempt (Uber, DoorDash, etc. can use Stripe)
- Some apps work around this by directing users to their website for subscription signup

### 6.8 Other Managed Providers

- **Square** — stronger in physical/POS, also does online. Owns the hardware + software stack.
- **Braintree** — PayPal-owned, supports PayPal/Venmo natively, similar developer experience to Stripe
- **Paddle / Lemon Squeezy** — "merchant of record" model, meaning they handle sales tax, VAT, and act as the legal seller. You're essentially a supplier to them. Simpler for global SaaS.
- **Adyen** — enterprise-focused, acts as gateway + processor + acquirer. Lower fees at scale but more complex setup.

______________________________________________________________________

## 7. The Full Picture: How It All Connects

```
Layer 0: Cash
  Buyer → Seller (direct, no intermediaries)

Layer 1: Debit Card (Physical)
  Buyer → POS Terminal → Processor → PIN Network or Card Network → Issuing Bank
                                                                        ↓
  Seller ← Acquiring Bank ← ──────────────── Settlement ───────────────┘

Layer 2: Credit Card (Physical)
  Buyer → POS Terminal → Processor → Card Network → Issuing Bank
                                                         ↓ (auth)
  Merchant ← Acquiring Bank ← ─── Settlement (T+1 to T+3) ┘
  (Interchange + network + processor fees deducted)

Layer 3: Online Payment (Direct Integration)
  Buyer's Browser → Payment Gateway → Payment Processor → Card Network → Issuing Bank
                         ↓ (tokenization, PCI)                               ↓
  Merchant Server ← ─── Authorization Response ──────────────────────────────┘
  (Merchant manages gateway, processor, merchant account separately)

Layer 4: Managed Provider (Stripe, etc.)
  Buyer's Browser → Stripe.js/Elements → Stripe (gateway + processor + merchant account)
                                              ↓
                                         Card Network → Issuing Bank
                                              ↓
  Merchant Server ← Webhook ← Stripe ← Settlement
  (Stripe handles everything; merchant just integrates the API)
```

Each layer adds abstraction, reducing complexity for the merchant at the cost of fees. The tradeoff is always: control and cost savings vs. convenience and reduced operational burden.

______________________________________________________________________
