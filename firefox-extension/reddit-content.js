(function () {
  let lastKnownUrl = window.location.href;
  let lastCountedUrl = null;

  function isTrackedRedditCommentsUrl(rawUrl) {
    try {
      const parsedUrl = new URL(rawUrl);
      return (
        (parsedUrl.hostname === "reddit.com" ||
          parsedUrl.hostname === "www.reddit.com") &&
        /^\/r\/[^/]+\/comments\/[^/]+(?:\/.*)?$/.test(parsedUrl.pathname)
      );
    } catch (error) {
      return false;
    }
  }

  function sendPageView() {
    return browser.runtime.sendMessage({
      type: "reddit_page_view",
    }).catch(function () {
      return undefined;
    });
  }

  function syncRedditPageView() {
    const nextUrl = window.location.href;
    if (nextUrl !== lastKnownUrl) {
      lastKnownUrl = nextUrl;
    }

    if (!isTrackedRedditCommentsUrl(nextUrl) || nextUrl === lastCountedUrl) {
      return;
    }

    lastCountedUrl = nextUrl;
    sendPageView();
  }

  function init() {
    syncRedditPageView();

    const observer = new MutationObserver(function () {
      syncRedditPageView();
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    window.setInterval(syncRedditPageView, 1000);
  }

  init();
})();
