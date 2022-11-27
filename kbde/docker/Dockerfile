FROM ubuntu:focal

ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED=1

# Base dependencies
RUN apt-get update && apt-get install -y \
    tree parallel gettext vim git wget lsb-release \
    python3-pip build-essential

# Create app dir
WORKDIR /app

# Add Python version file
ADD python.txt /app/

# Install Python version
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y `cat python.txt` lib`cat python.txt`-dev `cat python.txt`-distutils \
    && echo '#!/bin/bash\n\n`cat python.txt` "$@"' > python \
    && chmod +x python

# Custom system dependencies
ADD install.bash /app/
RUN bash install.bash

# Python dependencies
ADD requirements.txt /app/
RUN ./python -m pip install -r requirements.txt

# Add everything else
ADD . /app/

# Default command
CMD bash release.bash && honcho start -f Procfile-deployed
