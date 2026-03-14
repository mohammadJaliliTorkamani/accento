from faster_whisper import WhisperModel

from app.core.logger import logger

_LANG_MODEL = None


def get_model():
    global _LANG_MODEL

    if _LANG_MODEL is None:
        logger.info("Loading whisper model")

        _LANG_MODEL = WhisperModel(
            "tiny",
            device="cpu",
            compute_type="int8"
        )

    return _LANG_MODEL


def detect_language(audio_path: str):
    model = get_model()

    _, info = model.transcribe(
        audio_path,
        beam_size=1
    )

    return info.language
