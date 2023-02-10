FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ffmpeg \
    libespeak-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY . /app

# numpy needs to be installed manually first.
RUN pip3 install numpy
RUN pip3 install -r /app/requirements.txt

# Set the working directory to /app
WORKDIR /app

ENTRYPOINT [ "python3", "client.py" ]
