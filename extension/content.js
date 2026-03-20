// ================= CONFIG =================

const MAX_QUEUE_LENGTH = 50;
const POLL_INTERVAL = 4000;
const RECHECK_DELAY = 10000; // 10 seconds


// ================= STATE =================

const videoQueue = [];
const videoMap = new Map();

let allowedAccents = [];
let allowedLanguages = [];


// ================= LOGGER =================

function log(...args) {
    console.log("[AccentDetector]", ...args);
}


// ================= SETTINGS =================

// Initial load
chrome.storage.sync.get(["allowedAccents", "allowedLanguages"], (data) => {
    allowedAccents = data.allowedAccents || [];
    allowedLanguages = data.allowedLanguages || [];
    log("Loaded settings:", { allowedAccents, allowedLanguages });
});

// 🔥 Live updates when user changes settings
chrome.storage.onChanged.addListener((changes) => {
    if (changes.allowedAccents) {
        allowedAccents = changes.allowedAccents.newValue || [];
    }

    if (changes.allowedLanguages) {
        allowedLanguages = changes.allowedLanguages.newValue || [];
    }

    log("Updated settings:", { allowedAccents, allowedLanguages });

    // Re-evaluate all videos
    videoQueue.forEach(video => {
        if (video.lastAccent || video.lastLanguage) {
            handleResult(video, {
                status: "done",
                accent: video.lastAccent,
                language: video.lastLanguage
            });
        }
    });
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

        if (!videoMap.has(url)) {
            const video = {
                el,
                url,
                status: "pending",
                lastChecked: 0,
                lastAccent: null,
                lastLanguage: null
            };

            videoMap.set(url, video);

            if (videoQueue.length < MAX_QUEUE_LENGTH) {
                videoQueue.push(video);
                log("Added to queue:", url);
            } else {
                // optional cleanup
                const removed = videoQueue.shift();
                videoMap.delete(removed.url);
                videoQueue.push(video);
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
                { type: "detectVideos", urls },
                (response) => {
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
    const language = result.language;

    video.lastAccent = accent;
    video.lastLanguage = language;

    if (!accent) {
        video.status = "unknown";
        markElement(video.el, "unknown");
        return;
    }

    const accentAllowed =
        allowedAccents.length === 0 || allowedAccents.includes(accent);

    const languageAllowed =
        allowedLanguages.length === 0 || allowedLanguages.includes(language);

    if (accentAllowed && languageAllowed) {
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

    const pending = videoQueue.filter(v => v.status === "pending");
    const processing = videoQueue.filter(v => v.status === "processing");

    log("Pending:", pending.length, "Processing:", processing.length);

    // SEND NEW VIDEOS
    if (pending.length > 0) {
        const urls = pending.map(v => v.url);

        pending.forEach(v => {
            v.status = "processing";
            v.lastChecked = now;
            markElement(v.el, "processing");
        });

        const data = await callAPI(urls);
        if (!data) return;

        Object.entries(data).forEach(([url, result]) => {
            const video = videoMap.get(url);
            if (!video) return;

            handleResult(video, result);
            video.lastChecked = Date.now();
        });
    }

    // RECHECK PROCESSING
    const toCheck = processing.filter(v =>
        now - v.lastChecked > RECHECK_DELAY
    );

    if (toCheck.length === 0) return;

    const urls = toCheck.map(v => v.url);

    log("Rechecking:", urls);

    toCheck.forEach(v => v.lastChecked = now);

    const data = await callAPI(urls);
    if (!data) return;

    Object.entries(data).forEach(([url, result]) => {
        const video = videoMap.get(url);
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