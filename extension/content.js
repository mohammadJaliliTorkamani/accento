// ================= CONFIG =================

const MAX_QUEUE_LENGTH = 50;        // maximum videos stored
const BATCH_SIZE = 3;               // videos per API request
const POLL_INTERVAL = 4000;         // queue check interval
const RECHECK_DELAY = 15000;        // recheck processing videos
const LONG_VIDEO_THRESHOLD = 20 * 60; // 20 minutes


// ================= STATE =================

const videoQueue = [];
const videoMap = new WeakMap();


// ================= HELPERS =================

function getVideoElements() {
  return Array.from(
    document.querySelectorAll(
      "ytd-rich-item-renderer, ytd-video-renderer, ytd-grid-video-renderer, ytd-reel-video-renderer"
    )
  );
}

function extractUrl(el) {
  const a = el.querySelector("a[href*='watch'], a[href*='shorts']");
  if (!a) return null;
  return a.href.split("&")[0];
}


// ================= VIDEO DURATION =================

function getVideoDuration(el) {
  const timeEl = el.querySelector(
    "ytd-thumbnail-overlay-time-status-renderer span"
  );

  if (!timeEl) return 0;

  const parts = timeEl.innerText.trim().split(":").map(Number);

  if (parts.length === 2) {
    const [m, s] = parts;
    return m * 60 + s;
  }

  if (parts.length === 3) {
    const [h, m, s] = parts;
    return h * 3600 + m * 60 + s;
  }

  return 0;
}


// ================= BORDER STYLING =================

function markElement(el, status) {
  el.classList.remove(
    "detector-processing",
    "detector-indian",
    "detector-nonindian"
  );

  if (status === "processing") {
    el.classList.add("detector-processing");
  }

  if (status === "indian") {
    el.classList.add("detector-indian");
  }

  if (status === "nonindian") {
    el.classList.add("detector-nonindian");
  }
}


// ================= QUEUE DISCOVERY =================

function updateQueue() {
  const elements = getVideoElements();

  for (const el of elements) {
    const url = extractUrl(el);
    if (!url) continue;

    if (!videoMap.has(el)) {
      const duration = getVideoDuration(el);

      const video = {
        el,
        url,
        status: "processing",
        lastChecked: 0,
        duration,
        priority: duration > LONG_VIDEO_THRESHOLD ? 1 : 0
      };

      videoMap.set(el, video);

      if (videoQueue.length < MAX_QUEUE_LENGTH) {
        videoQueue.push(video);
      }

      markElement(el, "processing");
    }
  }
}


// ================= API CALL =================

async function callAPI(urls) {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      { type: "detectVideos", urls },
      (response) => {

        console.log("API response:", response);

        if (!response) {
          resolve(null);
          return;
        }

        if (response.success) {
          resolve(response.data);
        } else {
          console.error("API error:", response.error);
          resolve(null);
        }
      }
    );
  });
}


// ================= QUEUE PROCESSING =================

async function processQueue() {

  const now = Date.now();

  // prioritize shorter videos
  videoQueue.sort((a, b) => a.priority - b.priority);

  const toSend = videoQueue
    .filter(v =>
      v.status === "processing" &&
      (v.lastChecked === 0 || now - v.lastChecked > RECHECK_DELAY)
    )
    .slice(0, BATCH_SIZE);

  if (toSend.length === 0) return;

  const urls = toSend.map(v => v.url);

  console.log("Sending batch:", urls);

  toSend.forEach(v => v.lastChecked = now);

  const data = await callAPI(urls);
  if (!data) return;

  Object.entries(data.results).forEach(([url, result]) => {

    const video = videoQueue.find(v => v.url === url);
    if (!video) return;

    if (result.status === "processing") {

      video.status = "processing";
      markElement(video.el, "processing");

      console.log(url, "still processing");

    } else if (result.status === "done") {

      if (result.is_indian) {

        video.status = "indian";
        markElement(video.el, "indian");

        console.log(url, "INDIAN", result.confidence);

      } else {

        video.status = "nonindian";
        markElement(video.el, "nonindian");

        console.log(url, "NOT INDIAN", result.confidence);
      }
    }

    video.lastChecked = Date.now();
  });
}


// ================= MAIN LOOP =================

setInterval(() => {

  updateQueue();
  processQueue();

}, POLL_INTERVAL);