import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME")
    ENV = os.getenv("ENV")
    DEBUG = os.getenv("DEBUG") == "True"

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    MONGO_URL = os.getenv("MONGO_URL")
    MONGO_DB = os.getenv("MONGO_DB")

    REDIS_URL = os.getenv("REDIS_URL")

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    TEMP_AUDIO_DIR = os.getenv("TEMP_AUDIO_DIR")
    ACCENT_THRESHOLD = float(os.getenv("ACCENT_THRESHOLD"))


settings = Settings()
