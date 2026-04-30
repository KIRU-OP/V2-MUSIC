FROM python:3.13-slim

# 1. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 2. Set Directory
WORKDIR /app
COPY . /app/

# 3. Install System Dependencies
# Python 3.13 naya hai, isliye build-essential aur python3-dev zaroori hain 
# taaki jo packages ready nahi hain wo compile ho sakein.
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
    && rm -rf /var/lib/apt/lists/*

# 4. Install Dependencies using uv (Fixed Command)
# 'uv sync' ki jagah 'uv pip install' use kiya hai jo zyada stable hai 
# aur '--system' taaki Railway ke environment mein direct chale.
RUN uv pip install --system --no-cache -r requirements.txt

# 5. Bot Start Command
CMD ["bash", "start"]
