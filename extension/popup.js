const ACCENTS = [
    "american", "british", "indian", "australian", "canadian", "irish", "south_african"
];

const LANGUAGES = [
    "english", "spanish", "french", "german", "hindi", "mandarin", "arabic"
];

function createCheckbox(container, value, checked) {
    const label = document.createElement("label");

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = value;
    cb.checked = checked;

    label.appendChild(cb);
    label.append(" " + capitalize(value));
    container.appendChild(label);
}

function capitalize(str) {
    return str.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

function loadSettings() {
    chrome.storage.sync.get(["allowedAccents", "allowedLanguages"], (data) => {
        const allowedAccents = data.allowedAccents || ACCENTS;
        const allowedLanguages = data.allowedLanguages || LANGUAGES;

        const accentContainer = document.getElementById("accent-list");
        const langContainer = document.getElementById("language-list");

        accentContainer.innerHTML = "";
        langContainer.innerHTML = "";

        ACCENTS.forEach(a => createCheckbox(accentContainer, a, allowedAccents.includes(a)));
        LANGUAGES.forEach(l => createCheckbox(langContainer, l, allowedLanguages.includes(l)));
    });
}

function saveSettings() {
    const selectedAccents = Array.from(document.querySelectorAll("#accent-list input[type=checkbox]"))
                                .filter(cb => cb.checked).map(cb => cb.value);

    const selectedLanguages = Array.from(document.querySelectorAll("#language-list input[type=checkbox]"))
                                .filter(cb => cb.checked).map(cb => cb.value);

    chrome.storage.sync.set({
        allowedAccents: selectedAccents,
        allowedLanguages: selectedLanguages
    });

    window.close();
}

document.getElementById("save").onclick = saveSettings;

loadSettings();