import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import re
import torch
import torch.nn.functional as F
import soundfile as sf
from transformers import Wav2Vec2ForSequenceClassification

# =========================
# TEXT CHECK
# =========================
INDIAN_CHAR_PATTERN = re.compile(r'[\u0900-\u097F]')

def contains_indian_text(text: str) -> bool:
    return bool(INDIAN_CHAR_PATTERN.search(text))


# =========================
# LOAD MODEL (SAFE VERSION)
# =========================
_MODEL = None

def get_accent_model():
    global _MODEL

    if _MODEL is None:
        torch.set_num_threads(1)

        model_name = "dima806/english_accents_classification"

        _MODEL = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

        _MODEL.eval()
        _MODEL.to("cpu")  # Force CPU to avoid Docker/GPU crashes

    return _MODEL


# =========================
# ACCENT DETECTION
# =========================
def detect_indian_accent(audio_path: str, max_seconds: int = 15) -> float:
    """
    Returns probability (0–1) that the audio contains an Indian English accent.
    """

    model = get_accent_model()

    # Load audio safely (avoids librosa segfault issues)
    waveform, sr = sf.read(audio_path)

    # Convert to mono if needed
    if len(waveform.shape) > 1:
        waveform = waveform.mean(axis=1)

    # Limit duration
    waveform = waveform[: max_seconds * sr]

    # Convert to tensor
    waveform = torch.tensor(waveform, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        outputs = model(waveform)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1)[0]

    # Sum probabilities of labels containing "indian"
    id2label = model.config.id2label
    indian_probability = 0.0

    for i, prob in enumerate(probs):
        if "indian" in id2label[i].lower():
            indian_probability += float(prob)

    return float(min(max(indian_probability, 0.0), 1.0))