FROM python:3.11-slim

# 1. Install uv (Faster than pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set Working Directory
WORKDIR /app
COPY . /app/

# 3. Install System Dependencies (Music Bot ke liye zaroori hain)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    bash \
    ffmpeg \
    git \
    zip \
    build-essential \
    python3-dev \
    libssl-dev \
    libffi-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. Install Python Dependencies using uv
# --system use kar rahe hain kyunki container mein venv ki zaroorat nahi hoti
RUN uv pip install --system --no-cache -r requirements.txt

# 5. Bot Start Command
CMD ["bash", "start"]
