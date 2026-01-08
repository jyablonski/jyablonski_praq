# Ad Selling

Ad Selling for Software Apps (mobile, web etc) generally works through either direct deals or using dedicated ad platforms

For Direct deals, you work directly with B2B companies who want to run advertising on your app.

- You get better margins but have to source the ad deals yourself, figure out terms w/ the B2B you're partnering with etc
- But, you control the ad content and who's it's from, which means better targeting, user trust, and often higher revenue
- Higher barrier to entry

Or you can use an Ad Platform that sources advertisements from companies for you, and all you have to worry about is creating Ad Units to serve those slots in your application

- Lower margins for you, but you don't have to source B2B Ad Deals yourself, or hire staff to handle that, or maintain those business relationships
- Often more "random" ads, not related to the user content you're serving
- Same # of impressions as direct, but lower CTR and lower CPM (effective cost per mille)
- Lower barrier to entry

## High-Level Flow

1. You (the developer) integrate ad slots or placements into your app.

1. These slots are filled by:

   - A platform/marketplace like Google AdMob, Meta Audience Network, etc.
   - Or, direct deals with businesses or agencies.

1. When users interact with your app and see or click on ads, you get paid (based on impressions, clicks, conversions, etc.).

______________________________________________________________________

## Two Main Ways to Sell Ads

### 1. Via Ad Networks (Most Common)

You integrate with a platform that handles everything for you.

#### Examples:

- Google AdMob
- Meta Audience Network
- Unity Ads
- AppLovin, IronSource, MoPub (now part of AppLovin)

#### How It Works:

- You create an account and define ad units (specific spots in your app like banners, interstitials, rewarded videos).
- You get an SDK or JavaScript snippet to integrate.
- Advertisers bid on showing their ads to your users via real-time auctions.
- You earn money per impression (CPM), per click (CPC), or per install/conversion (CPA).

* As part of these SDKs, you can pass user info like location, demographics, interests etc as long as its within privacy and policy limits
  - Many platforms require you to get explicit user consent (e.g., GDPR in EU, CCPA in California) before collecting or passing personal data.
  - You cannot pass personally identifiable information (PII) like name, email, or exact location unless you comply with strict privacy rules.
* The SDK then passes that info along to the ad network to potentially serve more relevant ads. For example, users in NYC might see different ads than users in Paris.
* The Ad Platform wants to serve the best matching ad creative it can, and they use proprietary algorithms under the hood to do that
* This potentially could impact app performance as this all happens at runtime, but there are performance improvements to be made here (show loading indicators, lazy load ads, cache them etc)

```js
AdRequest adRequest = new AdRequest.Builder()
    .addKeyword("fitness")
    .setGender(AdRequest.GENDER_MALE)
    .build();

AdView adView = findViewById(R.id.adView);
adView.loadAd(adRequest);
```

#### Key Terms:

- CPM (Cost Per Mille): You earn money per 1,000 impressions.
- CPC (Cost Per Click): You earn when users click an ad.
- Fill Rate: The % of ad requests that are actually served with ads.
- eCPM: Effective CPM — a blended revenue-per-thousand value based on clicks, views, installs, etc.

______________________________________________________________________

### 2. Direct Deals

You bypass the middleman and sell ad space directly to businesses or agencies.

#### How It Works:

- You identify potential advertisers (brands, local businesses, partners).
- Negotiate a deal: fixed fee, CPM, CPC, etc.
- You either serve the ad manually or use an in-house system or basic ad server.

#### Pros:

- You keep 100% of the revenue
- Full control over pricing, content, and terms

#### Cons:

- Much more effort to find advertisers
- Need to handle contracts, billing, ad serving, etc.
- Not scalable unless you have a large user base

______________________________________________________________________

## How You Get Paid

- Through the ad network's revenue dashboard
- Usually monthly payouts, via bank transfer or PayPal
- Must hit a minimum threshold (e.g. $100)

______________________________________________________________________

## How to Get Started

1. Pick an Ad Network (e.g. Google AdMob)
1. Register your app and create ad units
1. Integrate the SDK into your app
1. Place ad units in your app UI
1. Test and publish

______________________________________________________________________

## Gotchas to Watch For

- User experience: Too many ads -> bad UX, they may delete the app, leave bad reviews, unsubscribe etc
- Policy violations: Misleading ad placements or accidental clicks can get you banned from the ad platform
- Ad blockers: Users can block ads
- Fill rate drops in niche or low-demand markets

______________________________________________________________________

## Advanced: Mediation and Header Bidding

- Mediation tools (e.g. AdMob Mediation, IronSource) let you combine multiple networks and choose the highest-bidding one.
- Header bidding (used in web more than mobile) is a real-time auction where multiple buyers compete before a page loads.

______________________________________________________________________

# Types of Ads

## 1. Banner Ads

What: Small, usually fixed strips at the top or bottom of the screen.

### Implications:

- Impressions: Very high — banners are shown continuously while the user is on a screen.
- CTR: Usually low (0.1%–0.5%) because banners are easy to ignore (“banner blindness”).
- CPM: Typically lowest among ad formats (e.g., $0.5 - $3).
- User Experience: Least intrusive; users can continue interacting without interruption.
- Best for: Apps that want steady, passive revenue without annoying users.

______________________________________________________________________

## 2. Interstitial Ads

What: Full-screen ads shown during natural breaks (e.g., between game levels or screen transitions).

### Implications:

- Impressions: Lower than banners since they appear less frequently.
- CTR: Higher than banners (1–3%) because they take over the screen.
- CPM: Higher than banners, often $3–$10 or more.
- User Experience: Can be disruptive if overused — risks annoying users and causing churn.
- Best for: Apps with clear transition points; games or content apps where natural pauses exist.

______________________________________________________________________

## 3. Rewarded Ads

What: Users voluntarily watch a video or interactive ad in exchange for in-app rewards (coins, lives, premium content).

### Implications:

- Impressions: Limited by how often users want to claim rewards.
- CTR: Very high because users choose to watch.
- CPM: Highest among typical formats (can be $10+).
- User Experience: Positive, since ads provide value to users.
- Best for: Games and apps with virtual economies; great for engagement and revenue.

______________________________________________________________________

## 4. Native Ads

What: Ads designed to blend seamlessly with app content (e.g., recommended articles, product listings).

- Native ads must be clearly labeled (e.g., “Sponsored,” “Ad”) to avoid misleading users for both legal reasons and UX
- They should match the app’s UI style without disrupting usability or trust.

### Implications:

- Impressions: Similar to banners, but depends on placement.
- CTR: Generally higher than banners because they feel less like ads (0.5–2%).
- CPM: Mid-range, often better than banners.
- User Experience: Can feel more natural, but must be clearly labeled to avoid misleading users.
- Best for: Content apps, news, social media — where blending ads into content works well.

### Examples

1. Instgram Sponsored Posts
1. Google Sponsored Content appears at the top of the Search
1. Recommended Amazon Products appear at the top of the Search labeled "Sponsored Products"

______________________________________________________________________

## 5. Playable Ads

What: Interactive mini-ads that let users try a game or app before installing.

### Implications:

- Impressions: Lower, since these ads tend to be shown selectively.
- CTR: Very high engagement because users interact directly.
- CPM: Very high, often among the top-performing formats.
- User Experience: Engaging and immersive but can be longer than typical ads.
- Best for: Gaming apps looking to promote installs of other games or interactive content.

______________________________________________________________________

# Summary Table

| Ad Type | Impressions | CTR | CPM | User Experience | Best Use Case |
| ------------ | ----------- | -------------- | --------------- | ------------------------- | -------------------------------- |
| Banner | Very High | Low (0.1-0.5%) | Low ($0.5-$3) | Least intrusive | Passive revenue |
| Interstitial | Medium | Medium (1-3%) | Medium ($3-$10) | Disruptive if overused | Between natural breaks |
| Rewarded | Limited | Very High | High ($10+) | Positive (user opt-in) | Games, apps with virtual rewards |
| Native | High | Medium-High | Medium-High | Natural feel if done well | Content-driven apps |
| Playable | Low | Very High | Very High | Engaging, immersive | Game install promos |

______________________________________________________________________

## Implications for Monetization Strategy

- If you want steady baseline revenue without annoying users: use banners + native ads.
- If you want to maximize revenue per user and have natural pause points: add interstitials but use sparingly.
- If your app has virtual goods or rewards, prioritize rewarded ads - great for engagement and $$$.
- If you’re a gaming app targeting installs of other games, playable ads can outperform everything else but might be harder to implement.

______________________________________________________________________

# How Advertisers Assess Ad Performance

Advertisers assess ad performance by tracking specific metrics and KPIs that measure how well their ads meet their campaign goals.

______________________________________________________________________

## 1. Define Campaign Objectives

Before running ads, advertisers set clear goals, such as:

- Brand awareness (getting their name seen)
- Clicks (drive traffic to a website or app)
- Conversions (sales, sign-ups, installs)
- Engagement (likes, shares, video views)

For example:

- Campaign objective could be to generate profit by spending maybe $100k on advertising in order to sell $500k worth of product that took $300k to build?
  - 1000 customers bought a $500 product each -> $500k in revenue
- Return on Ad Spend (ROAS) would be $500k / $100k = 5 in this case. For every $1 you spent on ads, you get $5 in revenue
- Cost per Acquisition (CPA) for those 1000 customers is Ad spend / conversions, so $100k / 1000 = $100 per customer
- There's also some Customer LTV to be calculated here - maybe 25 of those 1000 customers were first-timers who just got introduced to your product.
- follow up questions: can ad spend scale profitably here (if we spent $200k on advertising instead, does net profit turn into $200k here?)
- Also have to factor in other costs like support, fulfillment

______________________________________________________________________

## 2. Track Basic Metrics

### Impressions

- Number of times the ad was shown to users.
- Measures reach and exposure.

### Clicks

- Number of times users clicked the ad.
- Measures interest and engagement.

### CTR (Click-Through Rate)

- Clicks ÷ Impressions.
- Indicates ad relevance and appeal.

* This typically ranges a lot based on type of ad (banner ad, interstitial ad, search ad etc) and industry
* Well-targeted ads (right interests, demographics, behavior) get much higher CTR than broad targeting.
* Targeting ads to where users are already searching or expressing intent is one of the most powerful strategies in digital advertising. It’s often called “intent-based marketing” or “search intent targeting.”
  - Search Engines Ads
  - Shopping Ads

______________________________________________________________________

## 3. Measure Conversion Metrics

If the goal is to get users to take a specific action (purchase, install, sign-up), advertisers track:

### Conversions

- Number of users who completed the desired action.

### Conversion Rate

- Conversions ÷ Clicks (or sometimes Impressions).
- Shows how effective the ad is at driving actions.

### CPA (Cost Per Acquisition)

- Total campaign cost / Conversions.
- Measures how much each conversion costs.

______________________________________________________________________

## 4. Track Revenue & ROI

Advertisers calculate:

### ROAS (Return on Ad Spend)

- Revenue generated ÷ Ad spend.
- Shows how profitable the campaign is.

### Lifetime Value (LTV)

- Predicts how much revenue a converted user will generate over time.
- Helps justify higher CPA if LTV is good.

______________________________________________________________________

## 5. Analyze Engagement & Quality Metrics

Advertisers also look at:

- Bounce rate on landing pages.
- Session duration if sending traffic to a website.
- Video watch rates for video ads.
- Viewability (whether the ad was actually seen).

______________________________________________________________________

## 6. Use Attribution Models

They use attribution tools to understand which ads or channels contributed most to conversions:

- Last-click attribution: gives credit to the last ad clicked.
- Multi-touch attribution: credits multiple touchpoints along the user journey.

______________________________________________________________________

## 7. Optimize & Iterate

Based on performance, advertisers:

- Adjust targeting (demographics, interests).
- Change creatives (images, copy).
- Test different ad formats.
- Reallocate budget to best-performing campaigns.

______________________________________________________________________

## Tools Advertisers Use

- Google Ads Manager
- Facebook Ads Manager
- Appsflyer, Adjust, Branch (for mobile attribution)
- Google Analytics
- DSP dashboards (Demand-Side Platforms)

## Attribution: Tracking Where Users Come From

Attribution is the process of identifying which marketing channels, campaigns, or touchpoints led a user to take a specific action (install, purchase, sign-up, etc.). In the context of ad selling and monetization, attribution matters because it tells you why users are in your app in the first place, and helps you understand the quality and behavior of users from different sources.

### Why Attribution Matters for App Monetization

When you're monetizing through ads, not all users are equal. Users acquired from different channels behave differently:

- Users from organic search might have higher intent and engage more deeply
- Users from paid social campaigns might churn faster but convert on ads at higher rates
- Users from influencer partnerships might have specific interests that affect which ads perform well

Understanding attribution helps you optimize both your acquisition spend and your ad monetization strategy. If users from TikTok ads have 3x higher ad engagement than users from Google UAC, that changes how you allocate budget and potentially how you segment your ad inventory.

### Source and Medium

Source refers to where the traffic came from (Google, Facebook, a specific website, an email campaign). Medium describes how they got there (organic search, paid CPC, referral link, email).

Common source/medium combinations:

- `google / organic` — user searched on Google and clicked a non-ad result
- `facebook / cpc` — user clicked a paid Facebook ad
- `newsletter / email` — user clicked a link in your email campaign
- `partner_site / referral` — user came from a link on another website

This data flows into your analytics and can be joined with ad performance data to answer questions like "do users from paid Instagram campaigns watch more rewarded ads than organic users?"

### The Direct Traffic Black Box

Direct traffic (`direct / none`) is one of the trickiest categories. It means the analytics system couldn't determine where the user came from. This happens when:

- User typed your URL directly into the browser
- User clicked a link in a native mobile app that doesn't pass referrer data
- User clicked a link in an email client that strips tracking parameters
- User came from HTTPS to HTTP (referrer gets dropped for security)
- User had a bookmark
- UTM parameters were missing or malformed on a campaign link

The problem is that "direct" becomes a catch-all bucket that mixes genuinely direct visitors (who already know your brand) with traffic from campaigns you thought you were tracking but aren't. This makes it hard to measure true campaign performance and can hide attribution gaps.

Best practices to minimize the black box:

- Always use UTM parameters on links you control (emails, social posts, partner links)
- Use deep linking SDKs for mobile that preserve attribution through app installs
- Implement server-side tracking where possible to reduce client-side tracking failures

### Attribution Models

Since users often interact with multiple touchpoints before converting, you need a model to decide which touchpoints get credit:

| Model | How It Works | Pros | Cons |
| ----------- | ------------------------------------------------- | ---------------------------------- | --------------------------------------- |
| Last-Click | 100% credit to final touchpoint before conversion | Simple, easy to implement | Ignores everything that built awareness |
| First-Click | 100% credit to first touchpoint | Shows what drove initial discovery | Ignores nurturing/closing touchpoints |
| Linear | Equal credit to all touchpoints | Acknowledges full journey | Doesn't distinguish high-impact touches |
| Time Decay | More credit to touchpoints closer to conversion | Balances journey with recency | Arbitrary decay curves |
| Data-Driven | ML model assigns credit based on actual impact | Most accurate if you have data | Requires significant volume, black box |

For most apps, last-click is the default but increasingly misleading as user journeys get more complex across devices and channels.

### Mobile Attribution Challenges

Mobile adds extra complexity because:

- Users switch between web and app
- App installs break the tracking chain (you lose referrer data when someone goes to the App Store)
- Privacy changes (iOS ATT, Android Privacy Sandbox) limit cross-app tracking
- Deterministic matching (device IDs) is becoming restricted, pushing toward probabilistic fingerprinting which is less accurate

This is why mobile attribution platforms (Appsflyer, Adjust, Branch, Singular) exist — they specialize in stitching together the install journey using deep links, deferred deep links, and probabilistic matching where deterministic fails.

### Connecting Attribution to Ad Monetization

Once you have attribution data, you can segment your ad monetization analysis:

- Compare eCPM and fill rates across user cohorts by acquisition source
- Identify which channels bring users with higher ad engagement
- Calculate true ROI by factoring in both acquisition cost and ad revenue LTV by source
- Detect fraud (if a paid channel is sending users who never engage with ads, something's wrong)

Without attribution, you're optimizing blind — you might be spending heavily to acquire users who generate almost no ad revenue, while underinvesting in channels that bring your most valuable users.

______________________________________________________________________

# How Ad Blockers Work

Ad blockers work prevent ads from being loaded or displayed in your app or browser by intercepting the key parts of the ad delivery process.

- They identify known Ad Server Domains (doubleclick.net, admob.com) and block or filter out network requests to those servers, so no ad data or creatives ever reach your app.
- They detect DOM elements or UI components with common ad-related class names or IDs, and injectg custom CSS or JS Scripts to hide these elements
- They monitor and watch for Ad Platform SDK code and prevent it from being executed
- Ad Blockers maintain lists of new ad servers, formats, or behaviors to block and update them frequently

This typically causes no impression events, and obviously no conversion events

- SDK callbacks for clicks, video views, completions, or other engagements never happen.

______________________________________________________________________

# Customer Lifetime Value

LTV (Lifetime Value) estimates the total revenue or profit a business expects to earn from a customer over the entire period they remain active. Calculating LTV helps companies decide how much they can spend to acquire customers and guides long-term strategy.

______________________________________________________________________

## How Companies Calculate LTV

### 1. Define the Time Period

- Decide the timeframe you want to measure (e.g., 12 months, customer lifespan, or average subscription duration).

______________________________________________________________________

### 2. Gather Key Metrics

| Metric | Description |
| ------------------------------- | ----------------------------------------------------------- |
| ARPU (Average Revenue Per User) | Average revenue generated per user per period (e.g., month) |
| Gross Margin | Revenue minus direct costs, expressed as a percentage |
| Churn Rate | % of customers lost per period |
| Retention Rate | % of customers retained per period (= 1 – churn rate) |
| Average Customer Lifespan | How long a customer stays active (often 1 ÷ churn rate) |

______________________________________________________________________

### 3. Basic LTV Formula (Simplified)

$$
\\text{LTV} = \\text{ARPU} \\times \\text{Average Customer Lifespan}
$$

Example:
If ARPU = $20/month and Average Lifespan = 12 months, then LTV = $240

______________________________________________________________________

### 4. Margin-Adjusted LTV

$$
\\text{LTV} = (\\text{ARPU} \\times \\text{Gross Margin}) \\times \\text{Average Customer Lifespan}
$$

This accounts for costs of goods/services sold.

______________________________________________________________________

### 5. Using Churn to Estimate Lifespan

$$
\\text{Average Customer Lifespan} = \\frac{1}{\\text{Churn Rate}}
$$

If monthly churn is 5%, lifespan is 1 ÷ 0.05 = 20 months.

______________________________________________________________________

### 6. More Advanced Methods

- Cohort Analysis: Track groups of customers who started at the same time to measure retention and spending over time.
- Discounted Cash Flow (DCF): Apply a discount rate to future revenues to account for the time value of money.
- Predictive Models: Use machine learning to forecast future customer behavior and spending.

______________________________________________________________________

### Summary Example:

| Metric | Value |
| ------------------- | --------------------- |
| ARPU (monthly) | $30 |
| Gross Margin | 70% |
| Monthly Churn | 4% |
| Average Lifespan | 1 / 0.04 = 25 months |
| Margin-Adjusted LTV | $30 * 0.7 * 25 = $525 |

______________________________________________________________________

### Why LTV Matters

- Helps determine maximum Customer Acquisition Cost (CAC).
- Guides marketing budget allocation.
- Supports product and retention strategies.

### GAM Quick Reference Summary

### Ad Units

- What: Designated ad spaces/placements on your site (e.g., Header, Sidebar, Footer)
- Key point: Reusable templates across your entire site. If you setup 3 spots for ads on your site across all article pages, there will be 3 ad units in total when you pull data from GAM

### Line Items

- What: Specific ad campaigns with delivery instructions
- Contains: Which ads, where to show them, targeting rules, pricing, date range
- Think of it as: The "campaign order" that tells GAM what to deliver

### Deal Types (Line Item Types)

Direct Deals (You negotiate):

- Sponsorship: Advertiser gets % of impressions, premium placement
- Standard: Advertiser gets specific # of impressions, guaranteed delivery

Programmatic (Google manages):

- Price Priority: Auction-based, highest bid wins
- Network: Google Ad Exchange/AdSense fills unsold inventory at market rates

Your Own:

- House: Your promotional ads, free, lowest priority fallback

### Getting Your Data Out

Data Transfer Files (DTF):

- Raw, granular exports to BigQuery/Cloud Storage
- Impression-level data with all dimensions (ad unit, line item, device, geo, time, etc.)
- Best for: Custom analysis, dashboards, historical trends, no UI limits

GAM API:

- Programmatic access to pull reports/data on-demand
- Best for: Real-time integrations, custom tools, automated workflows

Standard GAM UI Reports:

- Point-and-click reporting
- Best for: Quick insights, less technical users
- Limited: Row limits, less granular
