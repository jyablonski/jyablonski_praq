# Email Deliverability & Sender Reputation

## How Spam Reporting Works

When a user clicks "Report Spam" in their email client, the message moves to their spam folder and a copy is sent to the mailbox provider (Google, Microsoft, Yahoo) to train their spam filters. This is distinct from blocking (all future emails from that sender go to spam) and unsubscribing (removal from the sender's list). Critically, reporting as spam does not automatically stop future emails from being delivered to that user. Unless they also block the sender, they may continue receiving emails, continue reporting them, and continue damaging the sender's reputation with every complaint.

Bots create a related but upstream problem. Automated signups pollute lists with fake or harvested addresses. Sending to these addresses generates bounces and spam trap hits, degrading domain reputation even without a human clicking "report spam."

## Thresholds That Matter

As of February 2024, Google and Yahoo enforce strict spam complaint rate thresholds for bulk senders (5,000+ emails/day). Microsoft adopted similar standards on May 5, 2025.

- **0.1%**: The recommended target. Google considers this the "green zone" in Postmaster Tools. Staying below this is ideal.
- **0.3%**: The hard ceiling. Exceeding this triggers active filtering, throttling, or outright blocking. This is not a suggestion.
- **0.5%+**: ESPs may suspend your account entirely at this level.

Gmail monitors complaint rates over a rolling 30 to 60 day period, so a single bad campaign can hurt your reputation for weeks. The threshold applies per-campaign, not as a monthly average, meaning one bad send can trigger filtering immediately.

Important nuance: Gmail calculates complaint rate using inbox recipients as the denominator, not total sent. If Gmail is already routing half your email to spam, those recipients can't complain because they never saw the message. Your visible complaint rate can understate the actual problem.

## Google Postmaster Tools

Google Postmaster Tools surfaces your spam complaint rate, authentication pass rates, and domain/IP reputation. The V2 dashboard now displays threshold lines directly alongside the daily rate, making it easier to see when you're approaching danger.

Key limitations to understand:

- Data lags 24 to 48 hours. A bad campaign today won't show until tomorrow or the day after.
- A 0% complaint rate isn't always good news. It might mean your emails are already being filtered to spam, preventing recipients from seeing them to report them.
- Low send volume can suppress data for privacy reasons, and small denominators make single complaints create sharp spikes.
- The Feedback-ID header (containing campaign/customer/sender identifiers) enables campaign-level complaint attribution in Postmaster, but not individual user identification.

## Feedback Loops (FBLs)

FBLs are how mailbox providers notify senders about spam complaints. The data you get varies dramatically by provider.

**Yahoo (covers Yahoo Mail + AOL Mail):** Domain-based FBL. Sends individual complaint reports in ARF (Abuse Reporting Format) that include the original recipient's email address. Requires DKIM authentication and a postmaster@ mailbox on your sending domain. Register at senders.yahooinc.com under Sender Hub > Feedback Loop.

**Microsoft (Outlook, Hotmail, Live):** IP-based FBL via two programs. SNDS (Smart Network Data Services) provides reputation data per sending IP. JMRP (Junk Mail Reporting Program) sends individual complaint reports including the recipient address. Microsoft also offers "not junk" notifications when a recipient rescues your email from spam.

**Gmail:** Does not offer a traditional FBL. You cannot identify individual Gmail users who reported you as spam. Gmail only exposes aggregate complaint data through Postmaster Tools, segmented by Feedback-ID identifiers. This is the biggest blind spot for most senders because Gmail is typically their largest recipient segment.

Most major ESPs (SendGrid, Mailgun, Klaviyo, Marketo, etc.) register for the Yahoo and Microsoft FBLs on your behalf and auto-suppress complainers as part of the service. If you run your own sending infrastructure, you need to register with each provider directly and handle suppression yourself.

## ESP Handling

ESPs care deeply about spam complaints because they share sending infrastructure across many customers. One sender with high complaints can damage deliverability for everyone on that infrastructure.

ESPs automatically suppress hard bounces, spam complaints, and unsubscribes by adding them to account-level suppression lists. When you hit send, your ESP checks every recipient against this list and skips anyone on it. No delivery attempt, no bounce recorded, clean metrics.

Some ESPs issue warnings at complaint rates around 0.2% and will suspend accounts if rates climb above 0.5%.

## Consequences of Degraded Reputation

Reputation damage escalates in severity and compounds over time:

1. **Reduced visibility.** Emails land in Promotions tab instead of Primary. Open rates and click-through rates quietly decline. This stage is often invisible.
1. **Spam folder placement.** Inbox placement can drop from 95%+ to below 70% within days. Emails are technically "delivered" but sitting unseen in spam.
1. **Throttling.** ISPs slow down how fast they accept your email. Time-sensitive content arrives hours late.
1. **Blocking and rejection.** Receiving servers actively refuse your emails. They bounce back. Your ESP may suspend your account.
1. **Blocklisting.** Your domain or IP gets added to third-party blocklists (Spamhaus, Barracuda, etc.), affecting deliverability across all providers simultaneously.

Recovery timelines are asymmetric. Mild damage from a single bad campaign takes 2 to 4 weeks. Moderate damage with blocklist appearance takes 4 to 8 weeks. Severe domain reputation collapse takes 8 to 16 weeks, and sometimes standing up a fresh subdomain is faster than recovering the old one.

Modern mailbox providers (particularly Gmail) weight domain reputation more heavily than IP reputation. You can't escape a bad reputation by switching ESPs or getting a new IP. The domain follows you.

## Attack Vectors

**List bombing / subscription bombing.** Bots submit real people's email addresses into your signup forms at scale. Those people receive your emails without having asked for them and report you as spam. First documented by Spamhaus in 2016 when a single ESP recorded 22,000+ fraudulent signups across 3,000 customer domains. The attacker doesn't need to control any inboxes. They just need access to your unprotected forms.

**Coordinated complaint attacks.** A group of recipients (e.g., a competitor's employees) systematically report every email they receive from you. Harder to execute because the attacker needs mailboxes already on your list, but effective because false reports are indistinguishable from legitimate ones in the reputation system.

**Domain spoofing.** Attackers forge your domain in "From" headers to send spam, damaging your domain reputation. Proper SPF, DKIM, and DMARC configuration (with enforcement policy) prevents this.

## Mitigation Strategies

**Make unsubscribing dead simple.** One-click unsubscribe headers (List-Unsubscribe and List-Unsubscribe-Post) are now required by Google and Yahoo for bulk senders. An unsubscribe loses you a subscriber. A spam complaint damages your reputation with the mailbox provider. Make it easy for people to choose the less damaging option.

**Engagement-based suppression.** Proactively suppress users who haven't opened or clicked in 90 to 120 days. This is especially important for Gmail where you can't identify individual complainers through FBLs. Sunset flows (a re-engagement sequence followed by automatic suppression if they don't respond) are more sophisticated than hard date cutoffs.

**Soft bounce suppression.** Profiles with sustained high soft bounce rates (99%+) over a rolling window are almost certainly dead addresses. Suppressing them removes addresses that can't receive your content and are only hurting your reputation metrics.

**Double opt-in.** Requires users to confirm their subscription via a confirmation email link. Blocks list bombing because bots can't click the confirmation link in an inbox they don't control. The tradeoff is reduced signup conversion rates. Can be applied selectively (only on suspicious-looking signups) rather than universally to balance protection with growth.

**Form-level defenses.** CAPTCHA/reCAPTCHA, honeypot fields (hidden fields only bots fill out), rate limiting per IP, and real-time email address verification at the point of signup.

**Subdomain isolation.** Separate marketing, transactional, and newsletter sends onto different subdomains. A reputation hit on newsletter sends won't bleed into transactional email delivery (password resets, account confirmations).

**Monitor Postmaster Tools daily.** The 24 to 48 hour data lag means daily monitoring is the minimum. Track your own first-party engagement signals (open rates, click rates, bounce rates) in near real-time from your ESP, because those will surface problems hours before Postmaster does.

**Authentication.** SPF, DKIM, and DMARC are table stakes. Required by Google, Yahoo, and Microsoft for bulk senders. Protects against domain spoofing and is a prerequisite for FBL participation.

## Key Metrics to Watch

- **Spam complaint rate:** Stay under 0.1%, never exceed 0.3%.
- **Bounce rate:** Under 2% is safe. Above 5% is critical and triggers immediate reputation damage.
- **Open/click rates:** Declining trends are often the earliest signal of reputation degradation (emails landing in spam).
- **List decay:** Email lists degrade by roughly 22 to 28% annually. Regular cleaning is not optional.
- **0% complaint rate:** Counterintuitively, this can indicate your emails are already in spam. Investigate rather than celebrate.
