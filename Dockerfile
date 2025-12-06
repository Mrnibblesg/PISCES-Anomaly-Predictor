FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install Python, build deps and TensorFlow (CPU)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    liblzma-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --no-cache-dir --upgrade pip setuptools wheel \
    && python3 -m pip install --no-cache-dir tensorflow

    #WORKDIR /workspace

    # Copy current directory into the container workdir
    #COPY . /workspace
    VOLUME ["/app"]



    CMD ["/bin/bash"]
