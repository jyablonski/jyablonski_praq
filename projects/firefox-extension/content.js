(function () {
  const MAX_DELTA_SECONDS = 5;
  const FLUSH_INTERVAL_MS = 10000;

  let trackedVideo = null;
  let bufferedSeconds = 0;
  let lastPlaybackTickMs = 0;
  let lastKnownUrl = window.location.href;
  let lastKnownVideoId = getVideoIdFromUrl(lastKnownUrl);
  let flushTimerId = null;
  let observer = null;

  function getVideoIdFromUrl(rawUrl) {
    try {
      const parsedUrl = new URL(rawUrl);
      if (
        parsedUrl.hostname !== "www.youtube.com" ||
        parsedUrl.pathname !== "/watch"
      ) {
        return null;
      }

      return parsedUrl.searchParams.get("v");
    } catch (error) {
      return null;
    }
  }

  function isActivelyPlaying(video) {
    return Boolean(
      video &&
        !video.paused &&
        !video.ended &&
        video.readyState >= HTMLMediaElement.HAVE_CURRENT_DATA
    );
  }

  function sendMessage(payload) {
    return browser.runtime.sendMessage(payload).catch(function () {
      return undefined;
    });
  }

  function resetPlaybackClock() {
    lastPlaybackTickMs = isActivelyPlaying(trackedVideo) ? Date.now() : 0;
  }

  function syncBufferedWatchTime() {
    if (!isActivelyPlaying(trackedVideo)) {
      lastPlaybackTickMs = 0;
      return;
    }

    const nowMs = Date.now();
    if (lastPlaybackTickMs > 0) {
      const deltaSeconds = (nowMs - lastPlaybackTickMs) / 1000;
      if (deltaSeconds > 0 && deltaSeconds <= MAX_DELTA_SECONDS) {
        bufferedSeconds += deltaSeconds;
      }
    }

    lastPlaybackTickMs = nowMs;
  }

  function flushBufferedWatchTime(syncFirst) {
    if (syncFirst) {
      syncBufferedWatchTime();
    }

    if (bufferedSeconds <= 0) {
      return;
    }

    const secondsToFlush = Math.round(bufferedSeconds * 1000) / 1000;
    bufferedSeconds = 0;

    sendMessage({
      type: "watch_time",
      seconds: secondsToFlush,
    });
  }

  function handlePlay() {
    lastPlaybackTickMs = Date.now();
  }

  function handleTimeUpdate() {
    syncBufferedWatchTime();
  }

  function handlePauseLikeEvent() {
    syncBufferedWatchTime();
    lastPlaybackTickMs = 0;
    flushBufferedWatchTime(false);
  }

  function handleSeeking() {
    syncBufferedWatchTime();
    resetPlaybackClock();
  }

  function removeVideoListeners(video) {
    if (!video) {
      return;
    }

    video.removeEventListener("play", handlePlay);
    video.removeEventListener("playing", handlePlay);
    video.removeEventListener("timeupdate", handleTimeUpdate);
    video.removeEventListener("pause", handlePauseLikeEvent);
    video.removeEventListener("ended", handlePauseLikeEvent);
    video.removeEventListener("waiting", handlePauseLikeEvent);
    video.removeEventListener("seeking", handleSeeking);
  }

  function addVideoListeners(video) {
    video.addEventListener("play", handlePlay);
    video.addEventListener("playing", handlePlay);
    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("pause", handlePauseLikeEvent);
    video.addEventListener("ended", handlePauseLikeEvent);
    video.addEventListener("waiting", handlePauseLikeEvent);
    video.addEventListener("seeking", handleSeeking);
  }

  function attachVideo(video) {
    if (trackedVideo === video) {
      return;
    }

    if (trackedVideo) {
      syncBufferedWatchTime();
      flushBufferedWatchTime(false);
      removeVideoListeners(trackedVideo);
    }

    trackedVideo = video;

    if (!trackedVideo) {
      lastPlaybackTickMs = 0;
      return;
    }

    addVideoListeners(trackedVideo);
    resetPlaybackClock();
  }

  function handleUrlChange() {
    const nextUrl = window.location.href;
    if (nextUrl === lastKnownUrl) {
      return;
    }

    const nextVideoId = getVideoIdFromUrl(nextUrl);
    const shouldCountPageView =
      nextVideoId && nextVideoId !== lastKnownVideoId;

    if (shouldCountPageView) {
      sendMessage({ type: "youtube_page_view" });
    }

    lastKnownUrl = nextUrl;
    lastKnownVideoId = nextVideoId;
  }

  function syncPageState() {
    handleUrlChange();
    attachVideo(lastKnownVideoId ? document.querySelector("video") : null);
  }

  function handleVisibilityOrUnload() {
    flushBufferedWatchTime(true);
  }

  function init() {
    syncPageState();

    flushTimerId = window.setInterval(function () {
      flushBufferedWatchTime(true);
      syncPageState();
    }, FLUSH_INTERVAL_MS);

    observer = new MutationObserver(function () {
      syncPageState();
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true,
    });

    window.addEventListener("beforeunload", handleVisibilityOrUnload);
    window.addEventListener("pagehide", handleVisibilityOrUnload);
    document.addEventListener("visibilitychange", handleVisibilityOrUnload);
  }

  init();
})();
