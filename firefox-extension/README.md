# Daily Internet Usage Tracker

This Firefox extension tracks daily browsing activity in four buckets:

- Reddit post views for `reddit.com` or `www.reddit.com` URLs matching `/r/*/comments/*`
- YouTube video views for `www.youtube.com/watch?v=...`
- YouTube active watch time in hours
- Other page views for normal `http` and `https` pages that are not tracked Reddit or YouTube pages

## Use Case

The goal is lightweight personal usage tracking without external services, accounts, or analytics vendors.
All counts are stored locally in `browser.storage.local` and partitioned by date using keys like:

- `YYYY-MM-DD:reddit`
- `YYYY-MM-DD:youtube`
- `YYYY-MM-DD:youtube_seconds`
- `YYYY-MM-DD:other`

This makes it useful for answering simple questions like:

- How many Reddit threads did I open today?
- How many YouTube videos did I watch today?
- Roughly how much actual YouTube watch time did I log?
- How much of my browsing was "everything else"?

## What Was Built

- `manifest.json`: Firefox Manifest V2 extension config, permissions, popup, and Gecko metadata
- `background.js`: counts page views and stores daily totals
- `content.js`: tracks YouTube active play time and YouTube SPA video changes
- `reddit-content.js`: tracks Reddit post views on Reddit SPA navigation
- `popup.html` + `popup.js`: show today's stats in the toolbar popup

## Package Command

From this directory:

```bash
zip -r daily-usage-tracker.xpi manifest.json background.js content.js reddit-content.js popup.html popup.js
```

## Mozilla Add-ons Upload Notes

This add-on was submitted through the self-distribution/unlisted flow so it can be used privately in Firefox without a public AMO listing.

1. Creating an `.xpi` package from the source files above.
1. Adding `browser_specific_settings.gecko.id` to `manifest.json`.
1. Adding `data_collection_permissions.required: ["none"]` because data stays local and is not transmitted anywhere.
1. Uploading the `.xpi` through the Mozilla Add-ons Developer Hub using the private/self-distributed option.
1. Answering that no bundler, minifier, code generator, or template engine was used because the submitted files are the original source.
1. Waiting for Mozilla automated signing and validation.
1. Installing the signed `.xpi` in Firefox from file for permanent local use.

Current status:

- Approved version: `1.0.0`
- Mozilla status: automatically screened and tentatively approved
- Approval comment: `automatic validation`
- Mozilla may still perform human review later and request changes if needed
