import os
import torch
import librosa
import yt_dlp
import torch.nn.functional as F
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification

MODEL_NAME = "dima806/english_accents_classification"

# -----------------------------
# 1️⃣ Download Audio from YouTube
# -----------------------------
def download_audio(youtube_url, output_path="audio.wav"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    if os.path.exists("temp.wav"):
        os.rename("temp.wav", output_path)

    return output_path


# -----------------------------
# 2️⃣ Load Model (CPU optimized)
# -----------------------------
print("Loading accent model...")
feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_NAME)
model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()


# -----------------------------
# 3️⃣ Predict Accent + Probabilities
# -----------------------------
def predict_accent(audio_path, duration=10):
    # Load only first N seconds for speed
    audio, sr = librosa.load(audio_path, sr=16000, duration=duration)

    inputs = feature_extractor(
        audio,
        sampling_rate=16000,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1)

    logits_list = logits.squeeze().tolist()
    probs_list = probs.squeeze().tolist()

    pred_id = torch.argmax(logits, dim=-1).item()
    pred_label = model.config.id2label[pred_id]

    prob_dict = {
        model.config.id2label[i]: float(probs_list[i])
        for i in range(len(probs_list))
    }

    # Binary Indian vs Not-Indian probability
    indian_prob = sum(
        prob for label, prob in prob_dict.items()
        if "indian" in label.lower()
    )
    not_indian_prob = 1 - indian_prob

    return {
        "predicted_label": pred_label,
        "logits": logits_list,
        "all_probabilities": prob_dict,
        "indian_probability": indian_prob,
        "not_indian_probability": not_indian_prob
    }


# -----------------------------
# 4️⃣ Run Everything
# -----------------------------
if __name__ == "__main__":
    url = input("Enter YouTube URL: ")

    print("Downloading audio...")
    audio_file = download_audio(url)

    print("Analyzing accent...")
    result = predict_accent(audio_file, duration=10)

    print("\n====== RESULT ======")
    print("Predicted Accent:", result["predicted_label"])
    print("Indian Probability:", round(result["indian_probability"], 4))
    print("Not Indian Probability:", round(result["not_indian_probability"], 4))
    print("Logits:", result["logits"])
    print("\nAll Probabilities:")
    for k, v in result["all_probabilities"].items():
        print(f"{k}: {round(v, 4)}")