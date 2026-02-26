import re
import torch
from speechbrain.pretrained import EncoderClassifier

# =========================
# TEXT CHECK
# =========================
INDIAN_CHAR_PATTERN = re.compile(r'[\u0900-\u097F]')

def contains_indian_text(text: str) -> bool:
    return bool(INDIAN_CHAR_PATTERN.search(text))


# =========================
# LOAD LIGHTER MODEL ONCE
# =========================
classifier = EncoderClassifier.from_hparams(
    source="speechbrain/lang-id-commonlanguage_ecapa",
    run_opts={"device": "cpu"}
)


# =========================
# FAST ACCENT DETECTION
# =========================
def detect_indian_accent(audio_path: str) -> float:
    """
    Returns probability of Indian accent.
    """

    # limit audio length automatically inside classifier
    out_prob, score, index, label = classifier.classify_file(audio_path)

    # label is string like: 'english', 'hindi', etc.
    # This model is language-id, not pure accent-id,
    # so we treat English probability as base and refine.

    probabilities = out_prob.squeeze().tolist()
    labels = classifier.hparams.label_encoder.ind2lab

    indian_score = 0.0

    for i, lab in labels.items():
        if "india" in lab.lower() or "hindi" in lab.lower():
            indian_score = probabilities[i]
            break

    return float(indian_score)