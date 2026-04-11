# Modern Browser Extensions

## 1. How Browser Extensions Work

### The Mental Model

A browser extension is a collection of web technologies (HTML, CSS, JS) that the browser loads into isolated contexts with elevated privileges. The key insight is that an extension is not one program. It is several small programs running in different sandboxes, communicating through message passing.

Think of it like a microservices architecture inside the browser:

- A **background script** (or service worker) acts as the central coordinator. It runs in its own isolated context with no DOM, no page access, but full access to browser APIs (tabs, storage, bookmarks, etc).
- **Content scripts** are injected into web pages. They share the page's DOM but run in an isolated JavaScript world. They can read and modify the page, but they cannot directly call browser APIs (with minor exceptions like `storage` and `runtime.sendMessage`).
- **Popup pages** and **options pages** are small HTML documents rendered in their own contexts (the popup bubble, or a tab/embedded frame). They have access to browser APIs similar to the background script.
- **Devtools pages** can extend the developer tools panel.

These components communicate through a structured messaging system: `runtime.sendMessage`, `runtime.connect` (for long-lived ports), and in some cases `tabs.sendMessage` (background to content script).

### The Manifest

Every extension starts with `manifest.json`. This is the declaration of everything: what scripts to load, what permissions to request, what UI surfaces to register, what URLs to match for content script injection. It is the single source of truth the browser reads to understand your extension.

A minimal Manifest V3 example:

```json
{
  "manifest_version": 3,
  "name": "My Extension",
  "version": "1.0",
  "permissions": ["storage", "activeTab"],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": ["https://example.com/*"],
      "js": ["content.js"]
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": "icon.png"
  }
}
```

### What Runs Where

| Component | Runs in | Has DOM? | Browser APIs? | Page access? |
| -------------- | ----------------------------- | ---------- | ------------------------------ | ------------------------------ |
| Background/SW | Own isolate | No | Full | No (indirect via messaging) |
| Content script | Page process (isolated world) | Page's DOM | Limited (`runtime`, `storage`) | Yes (DOM only, not JS globals) |
| Popup | Own process | Own DOM | Full | No |
| Options page | Own process | Own DOM | Full | No |
| Devtools page | Own process | Own DOM | `devtools.*` APIs | Indirect |

The "isolated world" concept for content scripts is important. Your content script can do `document.querySelector('.some-class')` and manipulate the page, but if the page has `window.myApp = {...}`, your content script cannot see `window.myApp`. The JS namespaces are separate. If you need to interact with page JS, you have to inject a script element into the page's actual context (sometimes called a "page script" or "main world" injection), which introduces its own security considerations.

### Security Boundaries

The browser enforces several boundaries:

- **Content script isolation**: Content scripts share the DOM but not the JS context with the page. The page cannot call your content script functions or read your variables.
- **Permissions gating**: Browser APIs (tabs, history, bookmarks, cookies) are gated behind declared permissions. The browser prompts the user at install time for certain permissions.
- **CSP enforcement**: Extension pages (popup, options, background) have a Content Security Policy. By default this disallows `eval()`, inline scripts in HTML, and loading remote scripts. You must bundle everything.
- **Host permissions**: To inject content scripts or make cross-origin requests from the background, you must declare host permissions (`"host_permissions": ["https://example.com/*"]`). In MV3, these can be optional and granted at runtime.
- **CORS relaxation**: The background script can make fetch requests to any origin you have host permissions for, bypassing normal CORS restrictions. This is a key reason extensions use background scripts as proxy fetchers.

### Storage

Extensions have access to `browser.storage.local` and `browser.storage.sync`. Local storage is per-device with a generous limit (typically 10MB in Chrome, essentially unlimited in Firefox). Sync storage syncs across devices where the user is signed in, with tighter limits (around 100KB total, 8KB per item in Chrome). Both are async key-value stores, similar in API to a simplified version of IndexedDB but much easier to use. Data is stored as JSON-serializable objects.

```js
// Write
await browser.storage.local.set({ settings: { theme: "dark", count: 42 } });

// Read
const { settings } = await browser.storage.local.get("settings");

// Listen for changes (works in any context)
browser.storage.onChanged.addListener((changes, area) => {
  if (changes.settings) {
    console.log("Old:", changes.settings.oldValue);
    console.log("New:", changes.settings.newValue);
  }
});
```

Storage changes fire events across all extension contexts (background, popup, content scripts), making `storage.onChanged` a useful cross-context communication channel for reactive state.

### Messaging

The messaging system is the glue between components:

```js
// Content script -> Background
browser.runtime.sendMessage({ type: "fetchData", url: "https://api.example.com/data" });

// Background: listen for messages from any extension context
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "fetchData") {
    fetch(message.url)
      .then(r => r.json())
      .then(data => sendResponse(data));
    return true; // Keep the message channel open for async sendResponse
  }
});

// Background -> specific content script in a tab
browser.tabs.sendMessage(tabId, { type: "updateUI", data: result });
```

The `return true` pattern in `onMessage` is a common source of bugs. If your handler is async, you must return `true` synchronously to signal that `sendResponse` will be called later. Alternatively, you can return a Promise (Firefox supports this natively; Chrome added support in recent versions).

For long-lived connections (streaming data, ongoing communication), use `runtime.connect` to create a port:

```js
// Content script
const port = browser.runtime.connect({ name: "stream" });
port.onMessage.addListener(msg => console.log(msg));
port.postMessage({ subscribe: "updates" });

// Background
browser.runtime.onConnect.addListener(port => {
  if (port.name === "stream") {
    port.onMessage.addListener(msg => { /* handle */ });
    port.postMessage({ status: "connected" });
  }
});
```

______________________________________________________________________

## 2. Firefox vs Chrome Extensions

### Core Architecture

Both browsers adopted the WebExtensions API standard. Firefox explicitly designed its extension system to be compatible with Chrome's model after deprecating its legacy XUL/XPCOM extensions in 2017. The result is that roughly 80-90% of the API surface is identical or near-identical. The divergence comes from:

- Manifest version (V2 vs V3 and their implications)
- Namespace (`browser` vs `chrome`)
- Promise vs callback style
- Specific API behaviors and limitations
- Review, signing, and distribution

### Manifest V2 vs V3

This is the most consequential difference right now.

**Chrome** has fully committed to Manifest V3 and deprecated V2. New V2 extensions can no longer be published to the Chrome Web Store. Existing V2 extensions will stop working in Chrome on a rolling timeline (late 2024 through 2025 depending on the channel).

**Firefox** supports both V2 and V3. Firefox implemented MV3 with deliberate differences from Chrome's approach, specifically around background scripts. Firefox has no plans to drop V2 support on any hard timeline.

Key MV3 changes:

| Feature | MV2 | MV3 (Chrome) | MV3 (Firefox) |
| --------------------- | --------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------- |
| Background | Persistent page or event page | Service worker (no DOM, no persistent state, terminates after ~30s idle) | Service worker or persistent event page (your choice) |
| Remote code | Allowed (load scripts from CDN) | Forbidden | Forbidden |
| `webRequest` blocking | Available | Removed, replaced by `declarativeNetRequest` | Still available (Firefox kept it) |
| Content script world | "isolated" only | "isolated" or "MAIN" (inject into page JS context) | "isolated" or "MAIN" |
| Host permissions | In `permissions` | Separate `host_permissions` key | Separate `host_permissions` key |
| CSP | Customizable | Stricter, less customizable | Stricter, less customizable |
| Action | `browser_action` or `page_action` | Unified `action` | Unified `action` |

The service worker change in Chrome MV3 is the biggest practical pain point. Your background script has no `window`, no `document`, no `XMLHttpRequest` (use `fetch`), no `localStorage` (use `browser.storage`), and it can be terminated at any time after 30 seconds of inactivity. Any in-memory state is lost on termination. This forces a different programming model: you must persist anything important to storage and rehydrate on wake.

Firefox's decision to allow persistent background pages in MV3 (via `"background": { "scripts": ["bg.js"], "persistent": true }` or even a service worker) means Firefox extensions can dodge this complexity entirely. However, if you want cross-browser compatibility with Chrome, you still have to deal with service worker constraints.

### API Differences

Most APIs are functionally identical. Notable differences:

- **`browser` vs `chrome` namespace**: Firefox uses `browser.*` with native Promise returns. Chrome uses `chrome.*` with callbacks (though Chrome has added Promise support for most APIs in recent versions). Using `browser.*` is the recommended approach since it is the standard and Chrome supports it as an alias in MV3.
- **`declarativeNetRequest` vs `webRequest`**: Chrome replaced blocking `webRequest` with a declarative rule system. Firefox kept blocking `webRequest`. If your extension is an ad blocker or needs to modify requests, this matters enormously. Chrome's DNR is less flexible but more performant. Firefox lets you keep the imperative approach.
- **`browser.dns`**: Firefox-only.
- **`browser.sidebarAction`**: Firefox-only (creates a sidebar panel).
- **`chrome.offscreen`**: Chrome-only (creates a hidden document for DOM-dependent tasks the service worker cannot do, like audio playback or clipboard access).
- **Tab and window behaviors**: Minor differences in how tab properties are populated, when events fire, etc. Usually manageable with testing.

### Permissions and Review

**Chrome Web Store**: Requires a one-time $5 developer registration fee. Review times vary from hours to days. Google can and does reject extensions for overly broad permissions, unclear privacy policies, or policy violations. Google reviews are automated and sometimes inconsistent. Permissions changes in updates trigger re-review. The store supports automated publishing via the Chrome Web Store API.

**Firefox Add-ons (AMO)**: Free to register. Firefox requires all extensions to be signed by Mozilla, even for self-distribution. You submit to AMO, it signs the XPI, and you get it back. Review for listed (public) extensions involves both automated and manual review. "Unlisted" (self-distributed) extensions are signed quickly with mostly automated review. Firefox is generally more permissive about extension capabilities but does review for security issues.

### Local Development

**Chrome**: Go to `chrome://extensions`, enable Developer Mode, click "Load unpacked", select your extension directory. The extension stays loaded across browser restarts but you need to click the reload button after changes. For service worker changes, you must reload explicitly.

**Firefox**: Go to `about:debugging#/runtime/this-firefox`, click "Load Temporary Add-on", select any file in your extension directory. The extension is removed when Firefox closes. For persistent loading during development, use `web-ext run` (Mozilla's CLI tool), which launches Firefox with the extension loaded and supports hot-reload on file changes.

```bash
# Install web-ext globally
npm install -g web-ext

# Run Firefox with your extension, auto-reload on changes
web-ext run --source-dir ./src --firefox-profile dev-profile

# Build for distribution
web-ext build --source-dir ./src --artifacts-dir ./dist
```

`web-ext` is excellent and arguably the best part of the Firefox extension development experience.

### Permanent Installation and Self-Distribution

**Chrome**: Extensions must be installed from the Chrome Web Store for normal users. There is no supported way to permanently install a non-store extension for regular users. Enterprise admins can force-install via policy. During development, "Load unpacked" works but shows a warning on every browser start.

**Firefox**: Signed extensions can be installed directly from an XPI file. You can submit to AMO as "unlisted" to get it signed without being publicly listed. This makes self-distribution to friends, teams, or yourself trivial. You just share the signed XPI. Firefox also supports installing unsigned extensions in Nightly and Developer Edition by setting `xpinstall.signatures.required` to false, but this does not work in the release channel.

This difference matters a lot for personal-use extensions. Chrome effectively forces you to publish to the store or use developer mode with warnings. Firefox lets you sign and install privately with zero friction.

______________________________________________________________________

## 3. Cross-Browser Extension Development

### Feasibility

Building one extension for both browsers is feasible and common for small-to-medium extensions. The core APIs (storage, messaging, tabs, content scripts) are compatible enough that most logic works unchanged. The friction comes from manifest differences and a handful of API divergences.

### Portable vs Browser-Specific APIs

**Usually portable without changes:**

- `storage.local`, `storage.sync`
- `runtime.sendMessage`, `runtime.onMessage`, `runtime.connect`
- `tabs.query`, `tabs.create`, `tabs.update`, `tabs.sendMessage`
- `action` (popup, badge, icon) in MV3
- `notifications`
- `alarms`
- Content script injection and DOM manipulation
- `i18n`

**Often require browser-specific handling:**

- `webRequest` blocking (Chrome MV3 requires `declarativeNetRequest` instead)
- Background context (service worker vs event page behavior)
- `offscreen` documents (Chrome-only workaround for service worker limitations)
- `sidebarAction` (Firefox-only)
- `dns` (Firefox-only)
- Certain `contextMenus` behaviors (minor differences)
- Clipboard access patterns differ

### Namespace: `browser` vs `chrome`

Firefox introduced the `browser` namespace with native Promise support as the WebExtensions standard. Chrome uses `chrome` with callbacks (and increasingly with Promise support too). In MV3, Chrome also exposes the `browser` namespace as an alias.

For cross-browser code today, you have a few options:

1. **Use `browser` directly**: Works natively in Firefox. Works in Chrome MV3. If you need to support older Chrome, use a polyfill.
1. **Use the `webextension-polyfill`** (by Mozilla): This is a small library that wraps `chrome.*` callbacks into `browser.*` Promises. It is the most battle-tested approach for cross-browser extensions. Even in MV3, it smooths over remaining inconsistencies.
1. **Write a thin adapter**: If you want to avoid the dependency, a 10-line wrapper works for simple cases.

```js
// Simple adapter
const api = typeof browser !== "undefined" ? browser : chrome;
```

This works for basic usage but does not handle the callback-to-promise conversion. The polyfill is better for anything non-trivial.

### Managing Manifest Differences

You will likely need two manifests or a build step that produces them. Key differences:

```json
// Chrome MV3
{
  "manifest_version": 3,
  "background": {
    "service_worker": "background.js"
  },
  "action": { "default_popup": "popup.html" }
}

// Firefox MV3 (if you want the persistent background option)
{
  "manifest_version": 3,
  "background": {
    "scripts": ["background.js"]
  },
  "action": { "default_popup": "popup.html" },
  "browser_specific_settings": {
    "gecko": {
      "id": "my-extension@example.com",
      "strict_min_version": "109.0"
    }
  }
}
```

Firefox requires `browser_specific_settings.gecko.id` for signed extensions. Chrome ignores this field. The `background` format differs. A build script can generate both from a shared template.

### Recommended Codebase Structure

```
my-extension/
  src/
    background.js       # Shared background logic
    content.js          # Shared content script
    popup/
      popup.html
      popup.js
      popup.css
    options/
      options.html
      options.js
    lib/
      api.js            # Shared utilities, API wrapper
      storage.js        # Shared storage helpers
    manifest.chrome.json
    manifest.firefox.json
  scripts/
    build.js            # Generates dist/chrome and dist/firefox
  dist/
    chrome/
    firefox/
```

The build script copies shared files into both output directories and places the correct manifest as `manifest.json` in each.

______________________________________________________________________

## 4. Technical Constraints and Implementation Details

### Language Requirements

Extensions are fundamentally JavaScript, HTML, and CSS. The browser loads and executes these directly. However, you are not limited to writing raw JS:

**TypeScript**: Fully viable and recommended for anything beyond trivial complexity. You write TS, compile to JS, and ship the JS. The build step is the same as any TS project: `tsc` or a bundler that handles TS (esbuild, vite, webpack, rollup). The tradeoff is that you now need a build step, which adds complexity to development (file watching, source maps for debugging, output directory management).

**Frameworks (React, Preact, Svelte, Vue)**: Reasonable for popup and options page UIs. A popup is just an HTML page, so you can render React into it. The tradeoffs:

- Adds bundle size (React + ReactDOM is around 40KB minified+gzipped). Preact is around 3KB and is a strong alternative for extension UIs.
- Requires a bundler.
- Popup HTML must include the bundled script, not an inline script (CSP restriction).
- Overkill for simple popups with a few buttons. Very helpful for complex options pages or multi-view popups.

For content scripts, frameworks are less common because you are operating inside someone else's page. Injecting React to render a widget into a page is possible (render into a shadow DOM to isolate styles) but adds weight and complexity.

**Build tooling**: If you use TS, React, or any non-vanilla setup, you need a bundler. Modern recommendations:

- **vite + CRXJS plugin** (for Chrome, experimental Firefox support): The most ergonomic DX. Handles HMR for popup and content scripts.
- **WXT** (web extension tooling): A framework specifically for cross-browser extensions. Handles manifest generation, TypeScript, framework support, and multi-browser builds. Opinionated but removes a lot of boilerplate.
- **esbuild or rollup** with manual config: More control, less magic. Good if you want to understand every piece.
- **webpack**: Works but heavier than necessary for most extensions.

If you want zero build step, write vanilla JS and plain HTML. Many useful extensions are simple enough for this.

### What Gets Shipped

Your final extension package (a `.zip` for Chrome, `.xpi` for Firefox which is also just a zip) contains:

- `manifest.json`
- All JS files (bundled or raw)
- All HTML files (popup, options, etc.)
- All CSS files
- Icons (typically 16x16, 48x48, 128x128 PNGs)
- Any other static assets (images, fonts, wasm files)
- The `_locales/` directory if you use i18n

Source maps are optional (useful for debugging but increase size; strip them for production). No `node_modules`, no TS source files, no config files.

### Content Scripts on SPAs

This is one of the trickiest areas. Traditional content scripts are injected when a page matching your URL pattern loads. But SPAs like YouTube, Reddit, Twitter, and Gmail use client-side routing: the URL changes but the page does not actually reload. Your content script runs once on initial load and never re-fires for subsequent navigations.

Strategies:

1. **MutationObserver**: Watch for DOM changes and react to them. This is the most reliable approach for detecting new content appearing.

```js
const observer = new MutationObserver(mutations => {
  for (const mutation of mutations) {
    // Check if the elements you care about have appeared
    const target = document.querySelector('.new-content-class');
    if (target && !target.dataset.processed) {
      target.dataset.processed = 'true';
      // Do your thing
    }
  }
});

observer.observe(document.body, { childList: true, subtree: true });
```

2. **URL change detection**: Listen for `popstate` events or poll `location.href` to detect SPA navigation.

```js
let lastUrl = location.href;
new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    onUrlChange();
  }
}).observe(document.body, { childList: true, subtree: true });
```

3. **`webNavigation.onHistoryStateUpdated`** (in the background script): This API fires when a page uses `history.pushState` or `history.replaceState`, which is how most SPAs navigate.

```js
// background.js
browser.webNavigation.onHistoryStateUpdated.addListener(
  details => {
    browser.tabs.sendMessage(details.tabId, {
      type: "spa-navigation",
      url: details.url
    });
  },
  { url: [{ hostContains: "youtube.com" }] }
);
```

The `webNavigation` approach requires the `webNavigation` permission but is the cleanest solution.

### Storage Limitations

- `storage.local`: 10MB default in Chrome (can request `"unlimitedStorage"` permission for more). Firefox has a 10MB default quota too but the actual limit is higher in practice.
- `storage.sync`: Around 100KB total, 8KB per item, 512 items max in Chrome. Firefox is similar. Sync has write rate limits (roughly 2 writes per second).
- Both are async. There is no synchronous storage API in MV3.
- Data must be JSON-serializable. No functions, no circular references, no `Date` objects (store as ISO strings), no `Map`/`Set` (convert to arrays/objects).
- `storage.session` (MV3): In-memory only, cleared when the service worker terminates (Chrome) or when the browser closes. Useful for ephemeral state you do not want persisted. Quota is around 10MB.

For larger data needs, you can use IndexedDB from the background script (service workers support IndexedDB).

______________________________________________________________________

## 5. Common Gotchas and Failure Modes

### Permission Overreach

Requesting `<all_urls>` or broad host permissions when you only need access to specific sites triggers more aggressive review and scares users during installation. Both Chrome and Firefox have moved toward optional permissions and runtime host permission grants. Request the minimum you need in `permissions`, put nice-to-haves in `optional_permissions`, and use `permissions.request()` at runtime when the user triggers a feature that needs more access.

The `activeTab` permission is your best friend for many use cases. It grants temporary access to the current tab when the user clicks your extension icon, with no scary install warning.

### CSP Restrictions

Extension pages cannot run inline scripts. This means no `<script>` tags with code in your HTML, no `onclick="doStuff()"` attributes. All scripts must be in separate files referenced via `src`. This catches people who are used to writing quick inline scripts in HTML. The fix is always: move the code to a `.js` file and use `<script src="popup.js"></script>`.

You also cannot `eval()` or use `new Function()` in extension contexts. If a library depends on these, it will not work.

Loading scripts from external URLs (CDNs) is forbidden in MV3. Everything must be bundled locally.

### Messaging Bugs

The most common messaging issues:

1. **Forgetting `return true`** in `onMessage` handlers when using `sendResponse` asynchronously. Without it, the message channel closes immediately and the sender gets `undefined`.
1. **Sending a message to a content script in a tab that has not loaded yet**. The content script might not be injected yet, especially on browser start or after extension reload. Always handle `runtime.lastError` or catch the rejected promise.
1. **Sending messages from a content script when the background/service worker is inactive (MV3)**. The message will wake the service worker, but there can be a delay, and if your `onMessage` listener is registered inside an async initialization flow, it might miss the first message.
1. **Trying to send non-serializable data**. Messages are JSON-serialized. DOM nodes, functions, and class instances cannot be sent.

### Background Lifecycle Issues (MV3 Service Worker)

In Chrome MV3, the service worker is terminated after approximately 30 seconds of inactivity. This means:

- Global variables are lost. Any state must be persisted to `storage.local` or `storage.session`.
- `setInterval` and `setTimeout` do not persist across terminations. Use the `alarms` API for anything that needs to run periodically.
- WebSocket connections are dropped. You must reconnect on wake. This is a major pain point for extensions that need persistent connections.
- Event listeners must be registered synchronously at the top level of the service worker. If you register a listener inside an `async` function or after an `await`, it might not be registered in time when the service worker wakes up to handle an event.

```js
// WRONG: listener registered after async work
async function init() {
  const config = await browser.storage.local.get("config");
  browser.runtime.onMessage.addListener(handler); // Might miss events
}
init();

// RIGHT: register synchronously, handle async inside
browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  handleAsync(msg).then(sendResponse);
  return true;
});

async function handleAsync(msg) {
  const config = await browser.storage.local.get("config");
  // ...
}
```

### SPA Navigation Issues

Already covered above, but the core gotcha: your content script's `"matches"` pattern only triggers injection on real page loads, not SPA navigations. If you inject into `https://www.youtube.com/*`, your script runs once on the initial page load and never again as the user navigates between videos. You must use one of the strategies from the SPA section.

### Review and Rejection Risks

Chrome:

- Requesting unnecessary permissions is the most common rejection reason.
- Missing or vague privacy policy (required if you handle user data).
- Extensions that could have been a bookmark (too simple with no real functionality).
- Anything that looks like it modifies search results or injects ads.
- Using remote code execution patterns.

Firefox:

- Generally more lenient but still reviews for security.
- Obfuscated code will be rejected. If you use a bundler, submit source code alongside the bundle so reviewers can verify.
- Both AMO public listings and unlisted submissions for signing go through review.

### Debugging

**Chrome**: The service worker has its own inspector (click "Inspect" on the extension card at `chrome://extensions`). Content scripts are debuggable in the page's DevTools (they appear under the Sources tab in a separate section). Popup DevTools: right-click the popup and select "Inspect".

**Firefox**: `about:debugging` shows a link to inspect the background page. Content scripts appear in the page's debugger. `web-ext run` opens a clean profile with console output streamed to your terminal.

Pain points:

- Service worker termination mid-debug is disorienting. Chrome has a "keep alive" option in DevTools.
- Source maps work but require correct configuration, especially if you are using a bundler.
- Content script errors sometimes appear in the page console, sometimes in the extension console, depending on how the error propagates.

### Performance and Privacy

Extensions run in the browser's process space and can impact performance:

- Heavy content scripts on every page load will slow down browsing. Be selective with your `matches` patterns.
- `MutationObserver` on `document.body` with `subtree: true` fires frequently on dynamic pages. Debounce your handler or narrow the observation target.
- Large storage writes are not instant. Batch writes when possible.
- Background service workers that wake up frequently add latency to browser operations.

Privacy considerations:

- Extensions can read and modify any page the user visits (if they have the permissions). Users and reviewers are rightfully cautious about broad permissions.
- Content scripts can exfiltrate page data silently. This is why permission transparency matters.
- `storage.sync` sends data to the browser vendor's sync servers. Do not store sensitive data there.

______________________________________________________________________

## 6. Real-World Guidance

### Path for a Personal/Small Extension

1. Start with vanilla JS, no build step. One `manifest.json`, one `background.js`, one `content.js`, one `popup.html` + `popup.js`. Get the core logic working.
1. Develop in Firefox using `web-ext run` for fast iteration with auto-reload.
1. Test in Chrome by loading unpacked.
1. If you only need it for yourself, submit to Firefox AMO as unlisted, get it signed, install the XPI. For Chrome, just live with "Load unpacked" and the developer mode warning, or publish to the Chrome Web Store if you do not mind the process.
1. Add TypeScript or a framework only when complexity demands it.

### Path for a Production/Public Extension

1. Set up a build system from the start. WXT or vite + CRXJS are strong starting points. TypeScript is worth the investment for anything that will be maintained.
1. Implement the minimum viable feature with the minimum permissions. Use `activeTab` and optional permissions wherever possible.
1. Test on both Chrome and Firefox. Maintain separate manifests generated by the build.
1. Write a clear privacy policy even if your extension handles no user data (Chrome requires it for certain permissions).
1. Automate builds: separate output directories for Chrome and Firefox, automated zipping, possibly CI/CD for store publishing.
1. Submit to both stores. Be prepared for review feedback, especially from Chrome. Submit source code to Firefox alongside your bundle.
1. Set up update infrastructure. Both stores handle updates automatically for store-published extensions.

### Pre-Start Decision Checklist

- What pages does this need to run on? (Determines host permissions and content script patterns)
- Does it need to modify network requests? (webRequest/DNR, major cross-browser divergence)
- Does it need persistent background state or connections? (Service worker constraints in Chrome)
- Does it need to work on SPAs? (MutationObserver/webNavigation strategy)
- How will users configure it? (Popup, options page, or both)
- What data needs persisting? (storage.local vs sync vs session vs IndexedDB)
- Target browsers? (Chrome-only is simpler; cross-browser needs build tooling)
- Distribution model? (Store, self-distributed, enterprise, personal-only)
- Build tooling? (Vanilla for simple, bundler for TS/framework/cross-browser)
- Will you need to submit source to Firefox for review?

### Best Practices

- Request minimal permissions. Use `activeTab` when possible. Add `optional_permissions` for features users might not need.
- Register all event listeners synchronously at the top level of your background script/service worker.
- Do not store state in global variables in the service worker. Persist to storage, rehydrate on wake.
- Use `storage.onChanged` as a cross-context reactivity mechanism instead of excessive messaging.
- Debounce MutationObserver callbacks.
- Scope content scripts to the narrowest `matches` pattern that works.
- Use shadow DOM when injecting UI into pages to avoid style conflicts.
- Batch storage writes.
- Handle `runtime.lastError` or catch rejected promises on every message send.
- Include meaningful error messages in your popup/options UI when things fail.
- Version your storage schema if your data model might evolve.

### Anti-Patterns

- Requesting `<all_urls>` when you only need two domains.
- Using `setInterval` in the service worker for periodic tasks (use `alarms` API).
- Injecting content scripts into every page when you only need them on specific sites.
- Storing sensitive data (tokens, passwords) in `storage.sync`.
- Using `eval` or `new Function` (will break under CSP).
- Relying on inline event handlers in HTML (`onclick`, `onsubmit`).
- Assuming the background script is always running in MV3.
- Bundling a full framework (React 18 + dependencies) for a popup with three buttons.
- Not handling the case where the content script is not yet injected when you send it a message.
- Obfuscating code that you submit to Firefox.

______________________________________________________________________

### Key Resources

- Chrome extension docs: https://developer.chrome.com/docs/extensions
- Firefox extension docs: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions
- WXT framework: https://wxt.dev
- `web-ext` tool: https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/
- `webextension-polyfill`: https://github.com/nicolo-ribaudo/webextension-polyfill
- Browser extension compatibility table: https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Browser_support_for_JavaScript_APIs
