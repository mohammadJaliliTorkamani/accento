# Accento: AI-Powered English Accent Detection Backend

![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=flat&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-89C53C?style=flat&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat&logo=huggingface&logoColor=black)

------------------------------------------------------------------------

# Project Overview

**Accento** is a **production-ready AI backend service** that analyzes
spoken English in YouTube videos and classifies the **speaker's accent**
using machine learning.

The system is designed with a **scalable, asynchronous backend
architecture**, enabling efficient processing of video audio using
background workers.

This backend is designed to power applications such as:

-   Chrome extensions that visually tag videos by accent
-   YouTube analytics tools
-   Speech and language research platforms
-   Content filtering systems

The system combines modern backend infrastructure with machine learning
inference to create a **high-performance video analysis pipeline**.

------------------------------------------------------------------------

# Key Capabilities

| Capability | Description |
|---|---|
| Automatic Accent Detection | Detects English accents using deep learning speech models |
| YouTube Audio Processing | Extracts audio from YouTube videos for analysis |
| Language Detection | Automatically determines spoken language before accent classification |
| Async Video Processing | Long-running ML tasks run in the background via Celery |
| High Performance Caching | Redis prevents duplicate processing of previously analyzed videos |
| Batch Processing | Analyze multiple videos in a single request |
| Chrome Extension Integration | Designed to support browser extensions that visually filter YouTube content |
------------------------------------------------------------------------

# Architecture Overview

    +-------------------+        +-------------------+
    |    FastAPI API     | <----> |    MongoDB DB     |
    | (REST Endpoints)   |        | (Accent Results)  |
    +---------+---------+        +-------------------+
              |
              v
        +-------------------+
        | Celery Worker      |
        | (Background Tasks) |
        +---------+---------+
                  |
                  v
            +-------------+
            |   AI Models |
            | Whisper +   |
            | Wav2Vec2    |
            +-------------+
                  |
                  v
            +-------------+
            |  Redis Cache |
            +-------------+

## Flow

1.  Client sends video URL to FastAPI\
2.  API checks Redis cache\
3.  If not cached → check MongoDB\
4.  If not processed → queue Celery task\
5.  Worker downloads video audio\
6.  Whisper detects language\
7.  Wav2Vec2 predicts accent distribution\
8.  Results stored in MongoDB\
9.  Redis caches results for fast retrieval

------------------------------------------------------------------------

| Layer | Technology | Purpose |
|---|---|---|
| API | FastAPI | Asynchronous REST API |
| Database | MongoDB | NoSQL storage for analysis results |
| Background Processing | Celery + Redis | Asynchronous ML processing |
| ML Framework | PyTorch | Model inference |
| Speech Models | Whisper + Wav2Vec2 | Language and accent detection |
| Video Processing | yt-dlp | YouTube audio extraction |
| Caching | Redis | Prevent duplicate work |
| Containerization | Docker + Docker Compose | Multi-service orchestration |
| Language | Python 3.10+ | Backend implementation |

------------------------------------------------------------------------

# Features

## Accent Classification

Detects the most likely accent of a speaker in English speech.

### Supported Accents

  Accent
  ---------------
  American
  British
  Indian
  Australian
  Canadian
  Irish
  South African
  Other

Each prediction returns:

-   Most probable accent
-   Confidence score
-   Full probability distribution

------------------------------------------------------------------------

## Intelligent Processing Pipeline

The system optimizes performance by:

1.  Detecting spoken language first
2.  Skipping accent detection for non-English videos
3.  Processing only short audio segments (\~10 seconds)

This significantly reduces compute requirements.

------------------------------------------------------------------------

## Asynchronous ML Processing

Heavy ML tasks are executed via **Celery workers**, ensuring the API
remains responsive.

    API Request → Queue Task → Worker Processes → Store Result

------------------------------------------------------------------------

## Caching Layer

Redis caching ensures previously analyzed videos return instantly.

    Request → Redis Cache → MongoDB → Worker Processing

This dramatically improves performance for repeated requests.

------------------------------------------------------------------------

# Folder Structure

    accento/
    │
    ├── app/
    │
    │   ├── api/
    │   │   └── routes/
    │   │       ├── detection.py
    │   │       └── health.py
    │
    │   ├── core/
    │   │   ├── cache.py
    │   │   ├── cache_sync.py
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   └── logger.py
    │
    │   ├── models/
    │   │   ├── base.py
    │   │   └── video_result.py
    │
    │   ├── schemas/
    │   │   └── detection.py
    │
    │   ├── services/
    │   │   ├── accent_service.py
    │   │   ├── language_service.py
    │   │   └── youtube_service.py
    │
    │   ├── tasks/
    │   │   └── video_processing.py
    │
    │   ├── workers/
    │   │   └── celery_worker.py
    │
    │   └── main.py
    │
    ├── extension/
    ├── docker-compose.yml
    ├── Dockerfile
    ├── requirements.txt
    ├── .env
    └── README.md

------------------------------------------------------------------------

# Setup & Running

## 1️⃣ Clone the Repository

    git clone https://github.com/your-username/accento.git
    cd accento

------------------------------------------------------------------------

## 2️⃣ Configure Environment Variables

Create `.env`

    APP_NAME=accento
    DEBUG=True

    MONGO_URL=mongodb://admin:admin123@mongo:27017
    MONGO_DB=accento

    REDIS_URL=redis://redis:6379

    CELERY_BROKER_URL=redis://redis:6379/0
    CELERY_RESULT_BACKEND=redis://redis:6379/0

    ACCENT_THRESHOLD=0.6
    TEMP_AUDIO_DIR=/tmp

------------------------------------------------------------------------

## 3️⃣ Start Services

Run:

    docker compose up --build

This launches:

| Service | Purpose |
|---|---|
| FastAPI | REST API |
| Celery Worker | ML processing |
| Redis | Task queue and caching |
| MongoDB | Persistent storage |

------------------------------------------------------------------------

# API Endpoints

## Health Check

    GET /health

Returns system status.

------------------------------------------------------------------------

## Detect Accent for a Video

    POST /detect

Example request:

``` json
{
  "url": "https://www.youtube.com/watch?v=example"
}
```

Example response:

``` json
{
  "accent": "american",
  "confidence": 0.82,
  "distribution": {
    "american": 0.82,
    "british": 0.07,
    "indian": 0.03,
    "australian": 0.02
  }
}
```

If processing is still running:

``` json
{
  "status": "processing"
}
```

------------------------------------------------------------------------

## Batch Detection

    POST /detect/batch

Example:

``` json
{
  "urls": [
    "https://youtube.com/watch?v=1",
    "https://youtube.com/watch?v=2"
  ]
}
```

------------------------------------------------------------------------

# Chrome Extension

This backend is designed to support a **YouTube Chrome browser
extension** that can:

-   Analyze videos on a YouTube page
-   Detect speaker accents
-   Visually tag videos with borders or labels
-   Allow users to filter content by accent

------------------------------------------------------------------------

# Future Improvements

Potential enhancements include:

-   GPU acceleration for faster inference
-   Subtitle-based pre-analysis to reduce compute
-   User-configurable accent filters
-   Rate limiting and API authentication
-   Model upgrades for higher accuracy
-   Observability tools (Prometheus + Grafana)
-   Celery monitoring via Flower

------------------------------------------------------------------------

# License

MIT License