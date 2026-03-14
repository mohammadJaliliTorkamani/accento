const API_URL = "http://127.0.0.1:8000/detect/batch";

console.log("[AccentDetector] Background worker started");

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {

    console.log("[AccentDetector] Message received:", msg);

    if (msg.type !== "detectVideos") {
        sendResponse({success: false, error: "Unknown message type"});
        return;
    }

    (async () => {
        try {
            console.log("[AccentDetector] Sending request to API:", msg.urls);

            const res = await fetch(API_URL, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({urls: msg.urls})
            });

            let data = await res.json();

// Ensure data is always an object
            if (!data || typeof data !== "object") {
                console.warn("[AccentDetector] API returned invalid data, defaulting to {}");
                data = {};
            }

            sendResponse({success: true, data});

        } catch (e) {
            console.error("[AccentDetector] API error:", e);

            sendResponse({success: false, error: e.toString()});
        }
    })();
    return true; // Keep message channel open
});