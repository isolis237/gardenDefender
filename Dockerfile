# ---------- build layer ----------
FROM python:3.10-slim-bookworm AS builder
WORKDIR /install

COPY requirements.txt .


# install gpu enabled versions of torch
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir \
    torch==2.1.2+cu121 \
    torchvision==0.16.2+cu121 \
    torchaudio==2.1.2+cu121 \
    --extra-index-url https://download.pytorch.org/whl/cu121 && \
    pip install --no-cache-dir -r requirements.txt
    

# ---------- runtime layer ----------
FROM python:3.10-slim-bookworm

# install dependencies for image and video processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy only install python backages and binaries from build stage
COPY --from=builder /usr/local/lib/python3.10/site-packages \
                    /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copy your code and models
COPY app/    ./app
COPY models/ ./models

# run script on startup
#CMD ["python", "app/finetune.py"]