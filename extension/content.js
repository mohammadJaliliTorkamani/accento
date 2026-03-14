// ================= CONFIG =================

const MAX_QUEUE_LENGTH = 50;
const BATCH_SIZE = 3;
const POLL_INTERVAL = 4000;
const RECHECK_DELAY = 8000;


// ================= STATE =================

const videoQueue = [];
const videoMap = new WeakMap();

let allowedAccents = [];


// ================= LOGGER =================

function log(...args) {
    console.log("[AccentDetector]", ...args);
}


// ================= SETTINGS =================

chrome.storage.sync.get(["allowedAccents"], (data) => {

    allowedAccents = data.allowedAccents || [];

    log("Loaded accent settings:", allowedAccents);
});


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


// ================= BORDER =================

function markElement(el, status) {

    el.classList.remove(
        "detector-processing",
        "detector-allowed",
        "detector-blocked",
        "detector-unknown"
    );

    el.classList.add(`detector-${status}`);

    log("Border updated:", status);
}


// ================= QUEUE DISCOVERY =================

function updateQueue() {

    const elements = getVideoElements();

    for (const el of elements) {

        const url = extractUrl(el);
        if (!url) continue;

        if (!videoMap.has(el)) {

            const video = {
                el,
                url,
                status: "pending",
                lastChecked: 0
            };

            videoMap.set(el, video);

            if (videoQueue.length < MAX_QUEUE_LENGTH) {

                videoQueue.push(video);

                log("Added to queue:", url);
            }
        }
    }
}


// ================= API CALL =================

async function callAPI(urls) {
    if (!urls || !urls.length) return null;

    log("Calling API:", urls);

    return new Promise((resolve) => {
        try {
            chrome.runtime.sendMessage(
                {type: "detectVideos", urls},
                (response) => {
                    // Catch extension invalidation errors
                    if (chrome.runtime.lastError) {
                        log("Extension context error:", chrome.runtime.lastError.message);
                        resolve(null);
                        return;
                    }

                    if (!response) {
                        log("No background response");
                        resolve(null);
                        return;
                    }

                    // Ensure data is always an object
                    if (!response.data || typeof response.data !== "object") {
                        log("Invalid API data:", response.data);
                        resolve({});
                        return;
                    }

                    if (response.success) {
                        resolve(response.data);
                    } else {
                        log("API error:", response.error);
                        resolve(null);
                    }
                }
            );
        } catch (err) {
            log("sendMessage failed:", err);
            resolve(null);
        }
    });
}


// ================= RESULT HANDLING =================

function handleResult(video, result) {

    log("Result:", video.url, result);

    if (result.status === "processing") {

        video.status = "processing";
        markElement(video.el, "processing");
        return;
    }

    if (result.status !== "done") {

        video.status = "unknown";
        markElement(video.el, "unknown");
        return;
    }

    const accent = result.accent;

    if (!accent) {

        video.status = "unknown";
        markElement(video.el, "unknown");
        return;
    }

    if (allowedAccents.length === 0 || allowedAccents.includes(accent)) {

        video.status = "allowed";
        markElement(video.el, "allowed");

    } else {

        video.status = "blocked";
        markElement(video.el, "blocked");
    }
}


// ================= PROCESS QUEUE =================

async function processQueue() {

    const now = Date.now();

    const processing = videoQueue.filter(v => v.status === "processing");

    log("Currently processing:", processing.length);

    // recheck processing videos
    if (processing.length > 0) {

        const toCheck = processing.filter(v =>
            now - v.lastChecked > RECHECK_DELAY
        );

        if (toCheck.length === 0) return;

        const urls = toCheck.map(v => v.url);

        log("Rechecking:", urls);

        toCheck.forEach(v => v.lastChecked = now);

        const data = await callAPI(urls);

// Reset stuck videos if API call fails
        if (!data) {
            log("Resetting processing videos due to failed API call");
            videoQueue.forEach(v => {
                if (v.status === "processing") v.status = "pending";
            });
            return;
        }

// Ensure safe object
        const safeData = typeof data === "object" ? data : {};

        Object.entries(safeData).forEach(([url, result]) => {
            const video = videoQueue.find(v => v.url === url);
            if (!video) return;

            handleResult(video, result);
            video.lastChecked = Date.now();
        });

        return;
    }

    // send new videos only if < BATCH_SIZE processing
    const pending = videoQueue
        .filter(v => v.status === "pending")
        .slice(0, BATCH_SIZE);

    if (pending.length === 0) {

        log("No pending videos");
        return;
    }

    pending.forEach(v => {

        v.status = "processing";
        v.lastChecked = now;

        markElement(v.el, "processing");
    });

    const urls = pending.map(v => v.url);

    log("Sending NEW batch:", urls);

    const data = await callAPI(urls);

    const safeData = data || {};

    Object.entries(safeData).forEach(([url, result]) => {
        const video = videoQueue.find(v => v.url === url);
        if (!video) return;

        handleResult(video, result);

        video.lastChecked = Date.now();
    });
}


// ================= MAIN LOOP =================

log("Content script started");

setInterval(() => {

    updateQueue();
    processQueue();

}, POLL_INTERVAL);