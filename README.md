# Accento: AI-Powered Youtube Accent Analysis Backend + Chrome Extension


## Project Overview

Accento is a production-ready AI backend service that analyzes spoken
English in YouTube videos and classifies the speaker's accent using
machine learning.

The system uses a hybrid architecture:

-   FastAPI (async) --- handles API requests
-   Celery workers (sync) --- performs ML processing
-   MongoDB + Redis --- persistence and caching

This design enables instant API responses while heavy processing runs
asynchronously.

------------------------------------------------------------------------

## Key Capabilities

| Capability               | Description                                      |
|--------------------------|--------------------------------------------------|
| Accent Detection         | Classifies English accents using ONNX models     |
| Language Detection       | Skips non-English audio early                    |
| Live Stream Handling     | Skips live videos automatically                  |
| Async Processing         | FastAPI + Celery architecture                    |
| Redis Caching            | Prevents duplicate work                          |
| MongoDB Storage          | Stores results and states                        |
| Batch Processing         | Queue multiple videos                            |
| Chrome Extension Ready   | Supports real-time filtering                     |

------------------------------------------------------------------------

## Architecture Overview

    FastAPI (async)
       ↓
    Redis (cache)
       ↓
    MongoDB (async)
       ↓
    Celery Worker (sync)
       ↓
    ML Pipeline (Whisper + Wav2Vec2 ONNX)

------------------------------------------------------------------------

## Processing Flow

1.  Client sends video URL
2.  API checks Redis
3.  If not found → checks MongoDB
4.  If not found → inserts status = "processing"
5.  Celery task is triggered

### Worker Steps

-   Re-checks Redis (cache hit shortcut)
-   Re-checks MongoDB (idempotency)
-   Fetches video metadata
-   Skips live streams
-   Downloads audio
-   Detects language
-   Skips non-English audio
-   Runs accent detection
-   Stores result in MongoDB
-   Caches result in Redis

6.  Client re-requests result

------------------------------------------------------------------------

## Processing States

| Status     | Description                      |
|------------|----------------------------------|
| processing | Task is queued or running        |
| done       | Successfully processed           |
| error      | Processing failed                |

------------------------------------------------------------------------

## Special Cases

### Live Streams

``` json
{
  "status": "done",
  "reason": "live_stream_skipped"
}
```

### Non-English Audio

``` json
{
  "status": "done",
  "reason": "non_english"
}
```

------------------------------------------------------------------------

## Features

### Accent Classification

Detects the most likely accent of English speech.

### Output Includes

-   Predicted accent
-   Confidence score

Full probability distribution is computed internally but not returned in
API responses.

### Example Response

``` json
{
  "status": "done",
  "url": "...",
  "accent": "american",
  "confidence": 0.82
}
```

------------------------------------------------------------------------

## Intelligent Processing Pipeline

### Optimizations

-   Early Redis cache lookup
-   MongoDB fallback
-   Skip live videos
-   Skip non-English audio
-   Process only \~5 seconds of audio

------------------------------------------------------------------------

## Asynchronous ML Processing

    API → Queue → Worker → Store → Cache

-   API remains fast
-   Workers handle heavy ML tasks

------------------------------------------------------------------------

## Caching Strategy

    Request → Redis → MongoDB → Worker

-   Redis = fast lookup
-   MongoDB = persistent storage
-   Worker = fallback processing

------------------------------------------------------------------------

## Folder Structure

    accento/
    │
    ├── app/
    │   ├── api/
    │   │   └── routes/
    │   │       ├── detection.py
    │   │       └── health.py
    │
    │   ├── core/
    │   │   ├── cache.py
    │   │   ├── cache_sync.py
    │   │   ├── config.py
    │   │   ├── database_async.py
    │   │   ├── database_sync.py
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
    │   │   ├── youtube_service.py
    │   │   └── accent_model/
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

## Setup & Running

### 1️⃣ Clone

``` bash
git clone https://github.com/mohammadJaliliTorkamani/accento
cd accento
```

### 2️⃣ Environment Variables

``` env
APP_NAME=yt-indian-detector
ENV=development
DEBUG=True

MONGO_URL=mongodb://admin:admin123@mongo:27017/yt_detector?authSource=admin
MONGO_DB=yt_detector

REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

TEMP_AUDIO_DIR=/tmp/audio
ACCENT_THRESHOLD=0.6
```

### 3️⃣ Run

``` bash
docker compose up --build
```

------------------------------------------------------------------------

## API Endpoints

### Health

    GET /health

### Detect

    POST /detect

Initial response:

``` json
{
  "status": "processing"
}
```

### Batch Detection

    POST /detect/batch

``` json
{
  "url1": { "status": "processing" },
  "url2": { "status": "processing" }
}
```

Batch endpoint queues jobs only --- results must be fetched later.

------------------------------------------------------------------------

## Chrome Extension

Supports a browser extension that: - Detects accents on YouTube pages\
- Applies visual indicators (green/red borders)\
- Filters videos based on user preferences

------------------------------------------------------------------------

## Performance Optimizations

-   Redis caching
-   MongoDB persistence
-   Early exit for live/non-English
-   Short audio (\~5 sec)
-   ONNX runtime for fast inference
-   Background workers

------------------------------------------------------------------------

## Future Improvements

-   Return full probability distribution
-   GPU acceleration
-   Real-time streaming
-   Distributed workers
-   Observability (Prometheus + Grafana)
-   Authentication & rate limiting

------------------------------------------------------------------------

## License

MIT License
