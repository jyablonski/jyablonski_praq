# Ticketing Systems

Event ticketing systems sell, distribute, transfer, resell, and validate admission to live events. For sports teams, they also provide valuable fan data.

The main business questions are who controls access, who gets paid, who can identify and contact fans, and whether those relationships survive a change of provider.

## Overview

A team's platform manages seat inventory, onsales, season-ticket renewals, payment plans, group and premium sales, delivery, refunds, entry scans, and settlement reports. Tickets are perishable: an unsold seat loses its admission value once the event passes.

One company can perform several roles:

| Participant | Role and economic interest |
| --- | --- |
| Team, artist, or organizer | Supplies the event and sets inventory and pricing, subject to agreements. |
| Promoter | Books and markets events, negotiates with artists and venues, and may guarantee artist payments. |
| Venue owner or operator | Runs the building; may choose the ticketing provider and receive facility charges or shared fees. |
| Primary ticketing provider | Sells original tickets and provides inventory, box-office, and entry systems. |
| Resale marketplace | Connects ticket holders with buyers and usually charges fees. May also sell primary tickets. |
| Fan | Buys, receives, resells, or uses a ticket; these actions may involve different people. |

A **primary sale** is the original purchase. A **resale** is another paid transaction. A **transfer** can be a gift or delivery without a sale. Each reveals different information about revenue and fan identity.

Fans pay face value, service fees, facility charges, and taxes. Organizers generally set primary prices; resale sellers set asking prices. Service fees can be shared among several parties, so fees displayed on Ticketmaster do not all belong to Ticketmaster. [Ticketmaster on prices and fees](https://help.ticketmaster.com/hc/en-us/articles/9663528775313-How-are-ticket-prices-and-fees-determined).

Contracts often combine several years of exclusivity with advances, guarantees, or fee sharing. Switching requires migrating accounts and seat histories, replacing integrations, training staff, and coordinating payment plans and future events. Upfront payments can also make restrictive terms attractive to venues. [New York's 2016 ticketing investigation](https://ag.ny.gov/sites/default/files/reports/Ticket_Sales_Report.pdf).

Ticketing records tickets and entry activity. A customer relationship management system (CRM) manages sales and service, accounting maintains financial books, and a warehouse or customer data platform combines their records. Ticketing alone does not provide a complete fan database.

## History: Public Benefit and Commercial Entertainment

Events have long mixed civic, religious, political, social, and commercial goals. Modern sports and touring entertainment have expanded monetization, but paid entertainment predates ticketing companies, and public and nonprofit events continue.

### Civic Spectacles and Paid Admission

Ancient Athenian theater formed part of a religious festival and provided a setting for public discussion. At Rome's Colosseum, admission was free, but seating followed social rank. Admission tokens directed spectators to their places: ticketing organized access even when nobody paid to enter. Free admission did not mean equal access or purely charitable motives. [Metropolitan Museum on Greek theater](https://www.metmuseum.org/essays/theater-in-ancient-greece), [Colosseum admission and seating](https://colosseo.it/en/marvels/the-cavea-of-the-colosseum-and-the-belvedere-terrace/).

Around 1600, London's open-air theaters charged one penny for standing room and more for seats and comfort. Selling different experiences at different prices was already established. [Shakespeare's Globe on audiences](https://www.shakespearesglobe.com/discover/shakespeares-world/audiences/).

### From Sports Clubs to Spectator Businesses

Early American baseball clubs were member-supported social organizations. Professional clubs increasingly paid players and relied on gate receipts. Chicago's club adopted a joint-stock structure for its 1870 debut, a model that spread among leading teams. Civic pride and commercial incentives grew together. [SABR on early professional baseball](https://sabr.org/journal/article/chicagos-role-in-early-professional-baseball/).

### From Paper Tickets to Digital Accounts

Local box offices sold directly, but ordinary paper tickets revealed little about their users. Season-ticket records identified regular buyers; ticket stubs lacked today's account and transfer history.

Computerized systems connected sales channels to shared inventory and expanded distribution beyond the box office. Ticketmaster was founded in 1976 and ticketed its first concert in 1977. Its service combined distribution and operating infrastructure, funded through fees. [Ticketmaster history](https://business.ticketmaster.com/why-ticketmaster/our-story/).

Internet sales expanded reach. Mobile accounts connected purchases, transfers, resale, and entry scans, allowing relationships to continue across events. AXS describes tracking tickets through this lifecycle. [AEG on AXS](https://aegworldwide.com/press-center/press-releases/aeg-purchases-all-outstanding-shares-axs).

### Today's Commercial and Public Interests

Operators earn from admission, premium experiences, sponsorship, concessions, parking, merchandise, service fees, and resale. Digital systems let them adjust prices and offers as demand changes. Maximizing immediate revenue can conflict with affordable access and lasting loyalty.

Even free events need funding from governments, patrons, sponsors, or donors; the key difference is who pays and whose goals guide the event.

Public money can still fund venues used by private businesses. Public financing, building ownership, operating control, and affordable admission are separate issues. Community and nonprofit events also remain part of live entertainment. [Brookings on stadium subsidies](https://www.brookings.edu/articles/why-the-federal-government-should-stop-spending-billions-on-private-sports-stadiums/).

## How Venue Ownership Changes Things

Team ownership, building ownership, venue operations, and event rights are separate. A lease can give a team broad commercial control over a public stadium; a tenant may have little say in ticketing.

**The decisive question is which rights the team controls through ownership and contracts.**

| Arrangement | Ticketing and data implications |
| --- | --- |
| Team owns and operates the venue | Can often negotiate across the event calendar and coordinate tickets, suites, parking, and concessions, within existing agreements. |
| Team operates a public venue under a lease | Commercial control depends on the lease, rather than public title alone. |
| Team rents an independently operated venue | May inherit its provider and need separate access agreements for entry and spending data. |
| Several teams or promoters share a building | Rights may differ by event, inventory, or entity; the building need not have one customer database. |

Venue control can strengthen bargaining power by bringing more events to a contract. It can also let the team retain ancillary revenue and coordinate the visit through a shared account or loyalty program.

For example, discounting a seat may make sense if it attracts a new attendee who buys parking and food. That depends on actual margins and revenue rights: concession sales are not all profit, and a tenant may receive no parking income.

Ownership brings construction and maintenance costs, staffing, insurance, and the risk of an underused calendar. Those fixed costs can make a ticketing guarantee appealing.

Owning the arena does not automatically allow the team to market to concertgoers. Artists, promoters, leagues, operators, and providers may have different data rights. Moving concert purchasers into team marketing still requires a contractual and privacy basis.

## Who Owns the Data?

Neither the provider nor the team automatically owns every record. "Ownership" covers five questions:

1. **Custody:** Who stores records and runs accounts?
1. **Rights:** Who can access, export, retain, combine, and use each dataset?
1. **Privacy responsibility:** Who decides how information is used, and who processes it for someone else?
1. **Access:** Are detailed records available through feeds or only limited reports?
1. **Portability:** Can the team keep and use permitted history after switching?

A provider can process data for an organizer while independently using other data for its platform. Eventbrite's agreement explicitly separates these roles; another provider's contract may differ. [Eventbrite's data-processing agreement](https://www.eventbrite.com/help/en-us/articles/429030/).

### What Each Record Reveals

| Record | What it shows | Limitation |
| --- | --- | --- |
| Primary order | Buyer, payment, event, and seats | One buyer can represent a group. |
| Assignment or transfer | Accounts associated with tickets | Account holder and attendee can differ. |
| Resale | Seller, buyer, price, and marketplace | Outside marketplaces may withhold transaction details. |
| Entry scan | Credential used, entry time, and gate | Validates the ticket, not the person's identity. |
| Provider-wide activity | Interests across the provider's network | Team access does not automatically extend to unrelated events. |
| Team CRM, app, merchandise, or loyalty | Interactions beyond ticketing | Requires integration and identity matching. |

Alice buys four tickets, transfers one to Bob, and enters with two guests whose tickets remain in her account. The system may record Alice, Bob, and four scans. It has not identified the guests or independently verified who used each ticket.

Official resale improves transaction visibility but does not identify every attendee or grant marketing permission. Outside resale may still produce an identifiable transfer through the primary platform. Resale fee sharing and price restrictions depend on contracts and applicable rules.

### What Useful Access Requires

Evaluate identities, orders, refunds, ticket status, transfers, resale, scans, and communication preferences. A promise of "your data" means little if exports omit stable identifiers or ticket history.

Specify fields, update frequency, historical backfills, corrections, access costs, and permission to combine systems. Exit terms should cover export formats, retention, migration support, and fees. Also clarify the provider's own marketing and cross-client analytics rights.

An API alone proves little: Ticketmaster's public Discovery API lists events, while restricted partner and enterprise services serve other purposes. Event discovery is not purchaser-data access. [Ticketmaster API overview](https://developer.ticketmaster.com/products-and-docs/apis/getting-started/).

Fans retain applicable privacy rights. California's CCPA gives rights including access, correction, deletion, and opting out of sale or sharing, subject to its scope and exceptions. Connected systems must honor applicable requests and preferences. [CCPA guidance](https://oag.ca.gov/privacy/ccpa).

## Ticketmaster Versus a Smaller Provider

Compare the entire business relationship: distribution, reliability, money, flexibility, data, and switching costs. Size alone does not determine the outcome.

| Dimension | Potential incumbent advantage | Alternative's opportunity or risk |
| --- | --- | --- |
| Distribution | Familiar accounts and broad marketplace reach | More team-branded or flexible channels, but possibly more demand generation for the team. |
| Operations | Experience with major onsales, inventory, box offices, and entry | Better workflow fit; require proof of capacity and event-day support. |
| Commercial terms | Advances, guarantees, and fee sharing | Better pricing or terms may come with fewer financial incentives. |
| Data | Established enterprise feeds and integration partners | Clearer export rights or easier access; verify fields and cost. |
| Flexibility | Existing products reduce implementation work | Custom experiences and more sales channels may require more team effort. |
| Switching | A proven deployment reduces uncertainty | Better portability if negotiated; alternatives can also require exclusivity. |
| Continuity | Extensive staffing and infrastructure | Check financial stability, security, support, and recovery regardless of size. |

Ticketmaster offers enterprise APIs, certified integrations, distribution, and analytics. Teams can build their own warehouses within its ecosystem; access still depends on their agreements. [Ticketmaster integrations](https://business.ticketmaster.com/solutions/expert-partnership/).

SeatGeek promotes Ringside for access to platform data. SECUTIX markets customer and transaction data ownership, provides warehouse feeds, and offers broader analysis through a paid Datamart. Ownership, available fields, freshness, and cost remain separate questions. These are vendor offerings to verify in the contract. [SeatGeek solutions](https://seatgeek.com/enterprise/solutions), [SECUTIX services](https://www.secutix.com/secutix-business-services), [SECUTIX analytics](https://developers.secutix.com/docs/use_cases/data-analytics/data-analytics-integration).

Alternatives are not necessarily small or independent: SeatGeek serves major teams, and AXS belongs to entertainment and venue operator AEG. Eventbrite's organizer model explains data rights but is not evidence that it meets every professional sports requirement. [SeatGeek enterprise](https://seatgeek.com/enterprise), [AEG's AXS acquisition](https://aegworldwide.com/press-center/press-releases/aeg-purchases-all-outstanding-shares-axs).

A team with strong demand and experienced data staff may prioritize flexibility and portability. One relying on marketplace discovery or outside operating support may value those services more. Compare guarantees and distribution benefits against fees, revenue shares, implementation, staffing, and expected retention gains. Accessible data creates value only when the team uses it.

## What a Unified Fan Profile Enables

A unified profile connects known interactions across tickets, CRM, apps, merchandise, parking, concessions, loyalty, and service. It includes communication preferences and distinguishes buyers, recipients, and scanned tickets. Fans who never attend can still appear through other interactions.

Store where each fact came from so staff can distinguish verified purchases from assumptions about attendance or spending.

A warehouse or customer data platform combines records and matches identities; CRM and marketing integrations turn them into action. Stable account links are better evidence than matching surnames or addresses. Keep household and corporate accounts connected to their members without merging everyone into one person.

| Capability | Example |
| --- | --- |
| Retention | Address unused season tickets, declining attendance, or service problems before renewal. |
| Larger plans | Offer repeat single-game buyers a suitable partial-season package. |
| New fan relationships | Contact identified transfer or resale recipients when permitted. |
| Relevant offers | Suggest parking or merchandise and suppress products already owned. |
| Better service | Give staff purchase, refund, and support history. |
| Operations | Plan gate staffing using entry patterns and improve operations using aggregate attendance and spending. |
| Sponsorship | Measure eligible campaign participation and purchases with appropriate permissions or aggregation. |
| Revenue planning | Estimate lifetime value across seasons and products to guide acquisition and retention budgets. |

Bob receives tickets to several games, buys a jersey, and opts into team communications. Connecting those records lets the team recognize his interest and offer a small ticket package. Otherwise, Alice remains the known ticket buyer and Bob's merchandise purchases sit elsewhere.

Ticketmaster case studies describe KSE combining APIs and feeds with KORE's warehouse across teams and venues, and the Vikings connecting fan interactions and using entry data for staffing. They show the integration pattern; vendor-reported results are not guarantees. [KSE case study](https://business.ticketmaster.com/kroenke-sports-entertainment-tackles-disparate-data-sources-with-ticketmaster-and-kore-software/), [Vikings case study](https://business.ticketmaster.com/minnesota-vikings-increase-fan-engagement-with-ticketmaster-and-ssb-central-intelligence/).

Some activity stays anonymous, including cash purchases and unnamed group members. Preserve those gaps rather than inventing identity links.

Measure identified ticket holders, permitted contactability, match quality, data freshness, attendance versus distribution, repeat purchase, renewal, and incremental margin. Lifetime value should estimate future margins after servicing costs. Campaign holdouts help separate additional sales from purchases fans would have made anyway; profile counts and email opens alone show little.

Data also enables aggressive targeting and pricing. Teams must decide how to balance immediate revenue with loyalty, access, and service.

## Live Nation–Ticketmaster Antitrust Case in 2026

### Background

Live Nation combines promotion and venue interests with Ticketmaster. The DOJ allowed their 2010 merger with conditions covering software licensing, divestitures, and retaliation. In January 2020, a court strengthened and extended the consent decree following alleged violations. [2010 merger conditions](https://www.justice.gov/archives/opa/pr/justice-department-requires-ticketmaster-entertainment-inc-make-significant-changes-its), [2020 decree](https://www.justice.gov/archives/opa/pr/court-enters-judgment-significantly-modifies-and-extends-consent-decree-live).

The DOJ and states filed a civil antitrust case on May 23, 2024, in federal court in New York. They alleged exclusive contracts, retaliation against venues using rivals, restrictions linking amphitheater access to promotion, and exclusion of competitors. Requested relief included separating Ticketmaster from Live Nation. [DOJ lawsuit announcement](https://www.justice.gov/archives/opa/pr/justice-department-sues-live-nation-ticketmaster-monopolizing-markets-across-live-concert).

The competitive concern extends beyond software: a venue may hesitate to choose another ticketer if doing so jeopardizes access to shows. Promotion, venue control, and exclusivity can reinforce each other. [DOJ complaint](https://www.justice.gov/atr/media/1353101/dl).

### This Year's Developments

| Date | Development |
| --- | --- |
| March 2, 2026 | Trial began in the Southern District of New York. |
| March 9 | DOJ announced a settlement; most states rejected it and continued the trial. |
| April 15 | The jury found Live Nation and Ticketmaster liable on the remaining antitrust claims. |
| June 12 | The proposed federal judgment was filed; DOJ later published its explanation of the relief. |
| July 30 | Live Nation's quarterly filing described unresolved settlement approval and post-verdict proceedings, with an intention to appeal as needed. |
| September–October | Reporting described continuing settlement review and an October 2 dispute over settlement-related disclosures. |

Sources: [California AG on the trial and verdict](https://oag.ca.gov/node/621782), [DOJ filings](https://www.justice.gov/atr/case/us-and-plaintiff-states-v-live-nation-entertainment-inc-and-ticketmaster-llc), [Live Nation's July filing, Note 6](https://investors.livenationentertainment.com/sec-filings/all-sec-filings/content/0001335258-26-000035/0001335258-26-000035.pdf), [Pollstar, September 15](https://news.pollstar.com/2026/09/15/the-biz-objections-roll-in-as-judge-reviews-ln-settlement-umg-wraps-buyback/), [Law360, October 2](https://www.law360.com/compliance/articles/2533293).

The DOJ settlement and states' verdict are separate outcomes. Liability does not itself establish a breakup, and the federal proposal does not resolve every state claim. Sources checked for this note do not establish final approval of the settlement or an order compelling Ticketmaster's divestiture.

### Proposed Federal Settlement

The proposal has defined venue categories, conditions, and implementation periods:

- **Marketplace choice:** Let covered major concert venues use eligible third-party marketplaces with Ticketmaster's back end, offered separately.
- **Less exclusivity:** Allow specified alternatives under existing contracts, including up to 20% of primary inventory with proportional adjustments to exclusivity payments. Cap future fully exclusive contracts for covered major concert venues at four years.
- **Amphitheaters:** Allow eligible alternatives to sell up to 50% of tickets and cap Ticketmaster service fees at 15% of face value at covered Live Nation amphitheaters. The cap does not cover every Ticketmaster event.

[DOJ's competitive impact statement](https://www.justice.gov/atr/media/1450496/dl?inline=) explains these provisions.

Other terms require relinquishing control over specified amphitheaters, restrict retaliation and exclusive booking, impose information firewalls, and address Oak View Group ticketing incentives. Artists could request specified purchaser and sales data for their events, subject to privacy and other protections. This does not grant teams access to Ticketmaster's entire database. [Proposed judgment, Sections V–IX](https://www.justice.gov/atr/media/1446036/dl).

The federal proposal preserves Live Nation's ownership of Ticketmaster. Further relief from the states' verdict is a separate question.

### Implications for Teams and Fans

Separating the back end from the marketplace could let venues test distribution competitors without replacing all operating systems. This is a business inference, not a guaranteed result. Better portability still requires usable identity, transfer, scan, and data-use agreements.

Venues weigh access to shows, financial incentives, operational dependence, exclusivity, and data together. Remedies for major concert venues do not necessarily apply identically to sports contracts.

Price transparency is separate. The FTC's fee-disclosure rule took effect May 12, 2025 and requires covered prices to include mandatory fees, with exceptions such as government charges. It does not generally ban or cap fees. Transparent prices, competition, and fan-data access solve different problems. [FTC fee guidance](https://www.ftc.gov/business-guidance/resources/rule-unfair-or-deceptive-fees-frequently-asked-questions).
