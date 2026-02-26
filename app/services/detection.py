import re
import torch
import librosa
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification

# =========================
# TEXT CHECK (keep this)
# =========================
INDIAN_CHAR_PATTERN = re.compile(r'[\u0900-\u097F]')

def contains_indian_text(text: str) -> bool:
    return bool(INDIAN_CHAR_PATTERN.search(text))


# =========================
# LOAD MODEL ONCE (VERY IMPORTANT)
# =========================
MODEL_NAME = "MilesPurvis/english-accent-classifier"

feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()


# =========================
# REAL ACCENT DETECTION
# =========================
def detect_indian_accent(audio_path: str) -> float:
    """
    Returns probability that accent is Indian.
    """

    audio, sr = librosa.load(audio_path, sr=16000)

    inputs = feature_extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)[0]

    # Get label mapping
    labels = model.config.id2label

    indian_index = None
    for idx, label in labels.items():
        if "indian" in label.lower():
            indian_index = idx
            break

    if indian_index is None:
        return 0.0  # fallback safety

    return float(probs[indian_index].item())