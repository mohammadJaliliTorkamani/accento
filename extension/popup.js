document.addEventListener("DOMContentLoaded", () => {

    const ACCENTS = [
        "american", "british", "indian", "australian", "canadian", "irish", "south_african"
    ];

    const LANGUAGES = [
        "english", "spanish", "french", "german", "hindi", "mandarin", "arabic"
    ];

    function capitalize(str) {
        return str.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    }

    function createToggle(container, value, active) {
        const div = document.createElement("div");
        div.className = "toggle" + (active ? " active" : "");

        const label = document.createElement("span");
        label.textContent = capitalize(value);

        const slider = document.createElement("div");
        slider.className = "slider";

        div.appendChild(label);
        div.appendChild(slider);

        div.onclick = () => div.classList.toggle("active");

        div.dataset.value = value;
        container.appendChild(div);
    }

    function loadSettings() {
        chrome.storage.sync.get(["allowedAccents", "allowedLanguages"], (data) => {
            const allowedAccents = data.allowedAccents || ACCENTS;
            const allowedLanguages = data.allowedLanguages || LANGUAGES;

            const accentContainer = document.getElementById("accent-list");
            const langContainer = document.getElementById("language-list");

            accentContainer.innerHTML = "";
            langContainer.innerHTML = "";

            ACCENTS.forEach(a => createToggle(accentContainer, a, allowedAccents.includes(a)));
            LANGUAGES.forEach(l => createToggle(langContainer, l, allowedLanguages.includes(l)));
        });
    }

    function saveSettings() {
        const accentContainer = document.getElementById("accent-list");
        const langContainer = document.getElementById("language-list");

        const selectedAccents = Array.from(accentContainer.children)
            .filter(div => div.classList.contains("active"))
            .map(div => div.dataset.value);

        const selectedLanguages = Array.from(langContainer.children)
            .filter(div => div.classList.contains("active"))
            .map(div => div.dataset.value);

        chrome.storage.sync.set({
            allowedAccents: selectedAccents,
            allowedLanguages: selectedLanguages
        });

        window.close();
    }

    document.getElementById("save").onclick = saveSettings;

    loadSettings();
});