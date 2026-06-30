(function () {
  const storageQueue = {
    current: Promise.resolve(),
  };

  function getDatePrefix(date) {
    const year = String(date.getFullYear());
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function getStorageKey(metric, date) {
    return `${getDatePrefix(date || new Date())}:${metric}`;
  }

  function isHttpUrl(parsedUrl) {
    return parsedUrl.protocol === "http:" || parsedUrl.protocol === "https:";
  }

  function isRedditCommentsUrl(parsedUrl) {
    return (
      (parsedUrl.hostname === "reddit.com" ||
        parsedUrl.hostname === "www.reddit.com") &&
      /^\/r\/[^/]+\/comments\/[^/]+(?:\/.*)?$/.test(parsedUrl.pathname)
    );
  }

  function isTrackedRedditHost(parsedUrl) {
    return (
      parsedUrl.hostname === "reddit.com" ||
      parsedUrl.hostname === "www.reddit.com"
    );
  }

  function isTrackedYouTubeHost(parsedUrl) {
    return parsedUrl.hostname === "www.youtube.com";
  }

  function isYouTubeWatchUrl(parsedUrl) {
    return (
      parsedUrl.hostname === "www.youtube.com" &&
      parsedUrl.pathname === "/watch" &&
      parsedUrl.searchParams.has("v") &&
      parsedUrl.searchParams.get("v")
    );
  }

  function classifyUrl(rawUrl) {
    try {
      const parsedUrl = new URL(rawUrl);
      if (!isHttpUrl(parsedUrl)) {
        return null;
      }

      if (isRedditCommentsUrl(parsedUrl)) {
        return null;
      }

      if (isTrackedRedditHost(parsedUrl)) {
        return null;
      }

      if (isYouTubeWatchUrl(parsedUrl)) {
        return "youtube";
      }

      if (isTrackedYouTubeHost(parsedUrl)) {
        return null;
      }

      return "other";
    } catch (error) {
      return null;
    }
  }

  function withStorageLock(task) {
    storageQueue.current = storageQueue.current
      .then(task)
      .catch(function (error) {
        console.error("Storage update failed.", error);
      });

    return storageQueue.current;
  }

  function incrementMetric(metric, amount) {
    const safeAmount = Number(amount);
    if (!Number.isFinite(safeAmount) || safeAmount <= 0) {
      return Promise.resolve();
    }

    const key = getStorageKey(metric);

    return withStorageLock(function () {
      return browser.storage.local.get(key).then(function (stored) {
        const currentValue = Number(stored[key] || 0);
        return browser.storage.local.set({
          [key]: currentValue + safeAmount,
        });
      });
    });
  }

  browser.tabs.onUpdated.addListener(function (tabId, changeInfo, tab) {
    if (changeInfo.status !== "complete" || !tab || !tab.url) {
      return;
    }

    const metric = classifyUrl(tab.url);
    if (!metric) {
      return;
    }

    incrementMetric(metric, 1);
  });

  browser.runtime.onMessage.addListener(function (message) {
    if (!message || typeof message.type !== "string") {
      return undefined;
    }

    if (message.type === "watch_time") {
      return incrementMetric("youtube_seconds", message.seconds);
    }

    if (message.type === "youtube_page_view") {
      return incrementMetric("youtube", 1);
    }

    if (message.type === "reddit_page_view") {
      return incrementMetric("reddit", 1);
    }

    return undefined;
  });
})();
