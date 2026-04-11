function getDatePrefix(date) {
  const year = String(date.getFullYear());
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function formatHours(seconds) {
  return `${(seconds / 3600).toFixed(2)} hrs watched`;
}

function loadTodayStats() {
  const todayPrefix = getDatePrefix(new Date());
  const keys = [
    `${todayPrefix}:reddit`,
    `${todayPrefix}:youtube`,
    `${todayPrefix}:youtube_seconds`,
    `${todayPrefix}:other`,
  ];

  browser.storage.local.get(keys).then(function (stats) {
    const redditCount = Number(stats[keys[0]] || 0);
    const youtubeCount = Number(stats[keys[1]] || 0);
    const youtubeSeconds = Number(stats[keys[2]] || 0);
    const otherCount = Number(stats[keys[3]] || 0);

    setText("reddit-count", redditCount);
    setText("youtube-count", youtubeCount);
    setText("youtube-hours", formatHours(youtubeSeconds));
    setText("other-count", otherCount);
  });
}

loadTodayStats();
