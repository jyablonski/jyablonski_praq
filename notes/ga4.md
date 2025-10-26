# GA4 Overview

GA4 is Google's latest analytics platform that tracks user interactions across websites and apps. It replaced Universal Analytics in 2023 and uses an event-based data model rather than the older session-based approach.

GA4 tracks user behavior by collecting data about interactions (events) on your site - things like page views, clicks, scrolls, video plays, purchases, etc. It then processes this data to give you insights about:

- Who your users are (demographics, interests, location)
- How they found you
- What they do on your site
- Whether they convert (purchases, sign ups etc)

The key philosophical shift from Universal Analytics is that everything is an event. Even a page view is just an event called "page_view."

## Setup

Basic setup involves:

1. Creating a GA4 Propety in your Google Analytics Account
2. Add your measurement ID to your website by either:
   - Installing gtag.js snippet in your `<head>` section
   - Using Google Tag Manager (recommended)

```html
<!-- Google tag (gtag.js) -->
<script
  async
  src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"
></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag() {
    dataLayer.push(arguments);
  }
  gtag("js", new Date());
  gtag("config", "G-XXXXXXXXXX");
</script>
`
```

## Google Tag Manager

Google Tag Manager (GTM) is a tag management system that acts as a middleman between your website and analytics tools. The relationship works like this:

- Without GTM: Your site -> GA4 tracking code -> Google's servers
- With GTM: Your site -> GTM container -> GA4 tag -> Google's servers

GTM enables:

- No code changes, marketers can add or modify tracking without developers
- One container for multiple tools: GA4, Facebook Pixel, LinkedIn tags etc
- Advanced tracking for button clicks, form submissions, scroll depth
- Testing Environment to enable you to preview changes before publishing

It is setup on your site with a single container snippet in the `<head>` and `<body>`

Then in GTM, create a new tag:

- Tag Type: GA4 Configuration
- Add your measurement ID
- Set trigger on all pages
- Publish the container
- Add additional tags for specific events like button clicks, video plays etc

GTM uses 3 key concepts:

- Tags are code snippets that fire, like GA4 tracking
- Triggers are conditions that determine when tags are fired (page load, click etc)
- Variables are dynamic values used by tags and triggers (page url, click text etc)

## Use Cases

1. E-commerce
   - Track product views, add-to-carts, purchases
   - Analyze shopping behavior and cart abandonment
   - Measure Revenue and ROI by traffic source
2. Lead Generation
   - Track form submissions and button clicks
   - Measure conversion rates by landing page
   - Setup conversion funnels (visit -> form view -> submission)
3. Content Sites
   - Measure scroll depth to see if people read full articles
   - Track video engagement
   - Analyze navigation patterns and popular content
   - Measure user engagement time
   - Analyze where users drop off

## Key Features

GA4 automatically collects events like page views, scrolls, outbound clicks, site search, video engagement, and file downloads, but also includes features to enable customization of the platform for your app or service.

- You can track anything custom to your business via custom events.
- Mark important events as conversions to measure goal completion
- Create segments or cohorts based on behavior to use in reporting

## How It Works

GA4 works by sending HTTP requests as events happen to Google's Servers. This works everywhere JavaScript can run and the tracking is entirely client-side. The actual flow looks like:

1. JavaScript loads on the page (gtag.js or GTM container)
2. Events occur (page view, click)
3. Data gets queued in the `dataLayer` array (a JS object)
4. HTTP requests fire to Google's collection endpoints
5. Google processes and stores the data

These are typically:

- GET or POST requests with URL-encoded or JSON payload
- Batched when possible (multiple events in one request for efficiency)
- Sent asynchronously so they don't block page rendering

The payload includes:

- Your Measurement ID
- Client ID (anonymous user identifier stored in cookies)
- Event name and parameters
- Page URL, referrer, screen resolution
- Timestamp
- Session information

## Cookies

Cookies are small text files stored in your browser by websites you visit. They're a way for websites to remember information about you across page loads and visits. A cookie is just a key-value pair with some metadata.

GA4 primarily uses first-party cookies to identify users across sessions. GA4 collects a Client ID - the anonymous identifier that GA4 uses to recognize the same user across visits.

```text
1. You visit example.com
2. Server responds with:
   HTTP/1.1 200 OK
   Set-Cookie: user_id=abc123; Expires=Wed, 21 Oct 2026 07:28:00 GMT

3. Browser saves: user_id=abc123
4. Next request to example.com includes:
   Cookie: user_id=abc123

5. Server recognizes you!
```

First-party cookies:

- Set by the domain you visit
- Can be read by that site

Third-party cookies:

- Set by a different domain than the one you're on
- Used for cross-site tracking
- Slowly being phased out

Session cookies

- Deleted when browser closes
- Used for temporary state

Google typically tracks:

- A Session Cookie for every session
- A Client ID cookie for every user to identify the same user across sessions

## CDNs & Cached Content

CDNs and caching actually don't affect GA4 tracking at all. The Cached content includes HTML which already has the JS needed for GTM & GA4 to work.

1. Tracking happens client-side, not server-side

   - Even if your HTML is cached on a CDN edge server
   - The JavaScript still executes fresh in each user's browser
   - Each user gets their own Client ID cookie
   - Each page view still fires a request to Google's servers

2. Example flow with CDN:

```
   User -> CDN (cached HTML) -> User's Browser
   ↓ (HTML contains GA4/GTM script)
   User's Browser runs JavaScript
   ↓ (tracking code executes)
   HTTP request -> Google Analytics servers (NOT cached)
```

## PII Compliance

You need consent BEFORE setting cookies or collecting personal data (with limited exceptions). GDPR requires:

- Explicit opt-in for non-essential cookies
- Granular consent (can't bundle analytics with necessary cookies)
- Easy withdrawal of consent
- No cookie walls (can't block access for refusing)

```js
// WRONG - fires immediately on page load
gtag("config", "G-XXXXXXXXXX");

// RIGHT - only fires after consent
if (userHasConsented) {
  gtag("config", "G-XXXXXXXXXX");
}
```

CCPA is less strict, it opt-out rather than opt-in, which is a key difference from GDPR. But still requires:

- Notice at collection (privacy policy, cookie banner)
- Opt-out mechanism (do not sell my personal information link)
- Right to delete collected data
- Right to know what data was collected

Consent Management Platforms help manage this.

### Google Consent Mode v2

Google Consent Mode is Google's recommended approach for handling consent. It is NOT a CMP, but it allows you to tell Google tags whether they have permission to use cookies and collect data. It has two parameters:

```js
// Before user consents - default denied
gtag("consent", "default", {
  analytics_storage: "denied",
  ad_storage: "denied",
});

// After user consents
gtag("consent", "update", {
  analytics_storage: "granted",
  ad_storage: "granted",
});
```

With consent granted:

- Full tracking with cookies
- Client ID stored
- Full behavioral data collected

With consent denied:

- Cookieless pings sent to Google
- No Client ID stored
- Aggregate data only (modeled/estimated traffic)
- Can still see approximate traffic volumes
- No user-level data
- No remarketing audiences

This is better than nothing, but your data quality suffers significantly without consent. The reality is:

- Consent compliance is hard, and many companies don't comply properly
- Enforcement is inconsistent
- Fines can be substantial
- No perfect solution exists (yet)

### Consent Workflow

```js
// 1. Default to denied
gtag("consent", "default", {
  analytics_storage: "denied",
  ad_storage: "denied",
  wait_for_update: 500,
});

// 2. Load GA4 config (won't set cookies yet)
gtag("config", "G-XXXXXXXXXX");

// 3. Show banner, wait for user choice

// 4a. If user accepts
gtag("consent", "update", {
  analytics_storage: "granted",
  ad_storage: "granted",
});

// 4b. If user rejects - do nothing, stays denied
```
