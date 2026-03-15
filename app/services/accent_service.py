import numpy as np
import torch
import torchaudio
import onnxruntime as ort
from transformers import Wav2Vec2FeatureExtractor

from app.core.logger import logger

MODEL_NAME = "MilesPurvis/english-accent-classifier"

_SESSION = None
_EXTRACTOR = None
_ID2LABEL = None


def get_model():
    global _SESSION, _EXTRACTOR, _ID2LABEL

    if _SESSION is None:

        _SESSION = ort.InferenceSession(
            "/app/app/services/accent_model/accent_model.onnx",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
        )

        _EXTRACTOR = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)

        from transformers import Wav2Vec2ForSequenceClassification
        model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)

        _ID2LABEL = model.config.id2label

    return _SESSION, _EXTRACTOR, _ID2LABEL


def detect_accent(audio_path: str):

    session, extractor, id2label = get_model()

    logger.info("Loading model...")
    audio, sr = torchaudio.load(audio_path)

    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        audio = resampler(audio)

    audio, sr = torchaudio.load(audio_path)

    # ensure mono
    if audio.shape[0] > 1:
        audio = audio.mean(dim=0, keepdim=True)

    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        audio = resampler(audio)

    audio = audio.squeeze().numpy()

    audio = audio[: 5 * 16000]

    inputs = extractor(
        audio,
        sampling_rate=16000,
        return_tensors="np",
        padding=False
    )

    ort_inputs = {
        "input_values": inputs["input_values"].astype("float32")
    }

    logits = session.run(None, ort_inputs)[0]

    probs = torch.softmax(torch.tensor(logits), dim=-1)[0].numpy()

    results = {
        id2label[i]: float(p)
        for i, p in enumerate(probs)
    }

    top_accent = max(results, key=results.get)

    return top_accent, results[top_accent], results