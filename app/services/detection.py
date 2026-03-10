import os

import re
import torch
import librosa
import torch.nn.functional as F

from transformers import Wav2Vec2FeatureExtractor
from transformers import Wav2Vec2ForSequenceClassification
from faster_whisper import WhisperModel

os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"

# =========================
# TEXT CHECK
# =========================

INDIAN_CHAR_PATTERN = re.compile(r'[\u0900-\u097F]')

def contains_indian_text(text: str) -> bool:
    return bool(INDIAN_CHAR_PATTERN.search(text))


# =========================
# GLOBAL MODEL
# =========================

_MODEL = None
_LANG_MODEL = None
_FEATURE_EXTRACTOR = None

def get_language_model():
    global _LANG_MODEL

    if _LANG_MODEL is None:
        print("Loading language detection model...")
        _LANG_MODEL = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

    return _LANG_MODEL

def detect_language(audio_path: str):

    model = get_language_model()

    segments, info = model.transcribe(
        audio_path,
        beam_size=1
    )

    return info.language

def get_accent_model():
    global _MODEL, _FEATURE_EXTRACTOR

    if _MODEL is None:

        print("Loading lightweight accent model...")

        torch.set_num_threads(1)

        model_name = "MilesPurvis/english-accent-classifier"

        _FEATURE_EXTRACTOR = Wav2Vec2FeatureExtractor.from_pretrained(model_name)

        _MODEL = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

        _MODEL.eval()

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _MODEL.to(device)

        print("Model ready.")

    return _MODEL, _FEATURE_EXTRACTOR


# =========================
# ACCENT DETECTION
# =========================

def detect_indian_accent(audio_path: str, max_seconds: int = 10) -> float:
    print("Detecting...")
    """
    Returns probability (0–1) that the speaker has Indian English accent.
    """


    model, extractor = get_accent_model()
    print("Model loaded",model)

    # Load audio
    audio, sr = librosa.load(audio_path, sr=16000)

    # limit duration
    audio = audio[: max_seconds * 16000]

    # feature extraction
    inputs = extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():

        logits = model(**inputs).logits

        probs = F.softmax(logits, dim=-1)[0]

    # find indian class
    id2label = model.config.id2label
    print(id2label)

    indian_prob = 0.0

    for i, prob in enumerate(probs):
        if "indian" in id2label[i].lower():
            indian_prob += float(prob)

    return float(indian_prob)