import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "accento")

    DEBUG = os.getenv("DEBUG", "False") == "True"

    MONGO_URL = os.getenv("MONGO_URL")
    MONGO_DB = os.getenv("MONGO_DB", "accento")

    REDIS_URL = os.getenv("REDIS_URL")

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    ACCENT_THRESHOLD = float(os.getenv("ACCENT_THRESHOLD", 0.6))

    TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR", "/tmp")

    SUPPORTED_ACCENTS = [
        "american",
        "british",
        "indian",
        "australian",
        "canadian",
        "irish",
        "south_african",
        "other"
    ]


settings = Settings()
