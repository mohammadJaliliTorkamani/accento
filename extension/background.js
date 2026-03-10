const API_URL = "http://127.0.0.1:8000/detect/batch";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "detectVideos") {
    (async () => {
      try {
        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ urls: msg.urls })
        });
        const data = await res.json();

        console.log("Background API response:", data); // print API result

        sendResponse({ success: true, data });
      } catch (e) {
        console.error("Background API error", e);
        sendResponse({ success: false, error: e.toString() });
      }
    })();
    return true; // keep port open
  }
});