FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ffmpeg \
    libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY . /app

RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

ENTRYPOINT [ "python3", "client.py" ]
