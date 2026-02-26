FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 1. Install system dependencies (FFmpeg)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]