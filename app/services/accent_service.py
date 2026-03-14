import librosa
import torch
import torch.nn.functional as F
from transformers import (
    Wav2Vec2FeatureExtractor,
    Wav2Vec2ForSequenceClassification
)

from app.core.logger import logger

_MODEL = None
_EXTRACTOR = None


def get_model():
    global _MODEL, _EXTRACTOR

    if _MODEL is None:
        logger.info("Loading accent model")

        model_name = "MilesPurvis/english-accent-classifier"

        _EXTRACTOR = Wav2Vec2FeatureExtractor.from_pretrained(model_name)

        _MODEL = Wav2Vec2ForSequenceClassification.from_pretrained(model_name)

        _MODEL.eval()

        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        _MODEL.to(device)

    return _MODEL, _EXTRACTOR


def detect_accent(audio_path: str):
    model, extractor = get_model()

    audio, sr = librosa.load(audio_path, sr=16000)

    audio = audio[: 10 * 16000]

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

    id2label = model.config.id2label

    results = {}

    for i, p in enumerate(probs):
        results[id2label[i]] = float(p)

    top_accent = max(results, key=results.get)

    return top_accent, results[top_accent], results
