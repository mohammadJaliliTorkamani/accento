import torch
from transformers import Wav2Vec2ForSequenceClassification

MODEL_NAME = "MilesPurvis/english-accent-classifier"

model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

# dummy 5-second audio input (16kHz)
dummy_input = torch.randn(1, 16000 * 5)

torch.onnx.export(
    model,
    (dummy_input,),
    "app/services/accent_model/accent_model.onnx",
    input_names=["input_values"],
    output_names=["logits"],
    dynamic_axes={
        "input_values": {1: "audio_length"},
        "logits": {0: "batch_size"}
    },
    opset_version=14,
)

print("Exported accent_model.onnx")