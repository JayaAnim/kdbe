FROM ubuntu:focal

ARG DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED=1

# Configure sudo
RUN apt update \
    && apt install -y sudo \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Base dependencies
RUN apt install -y \
    tree parallel gettext vim git wget lsb-release build-essential

# Create app dir
WORKDIR /app

# Add Python version file
ADD python.txt /app/

# Install Python version
RUN apt install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt install -y \
        `cat python.txt` \
        `cat python.txt`-venv \
        `cat python.txt`-dev \
        python3-pip

# Custom system dependencies
ADD scripts/install.bash /app/scripts/
RUN ./scripts/install.bash

# User
ARG USER_NAME=root
ARG USER_UID=0
ARG USER_GID=0

RUN id $USER_NAME \
    || (addgroup --gid $USER_UID $USER_NAME \
        && adduser $USER_NAME --uid $USER_UID --gid $USER_GID --disabled-password --gecos "" \
        && usermod -aG sudo $USER_NAME)

# Switch to the correct user
USER $USER_NAME

# Python dependencies
ADD requirements.txt /app/
RUN bash -c '`cat python.txt` -m venv ~/env \
    && source ~/env/bin/activate \
    && pip install -U pip \
    && pip install wheel \
    && `cat python.txt` -m pip install -r requirements.txt'

#Add everything else
ADD . /app/

# Default command
CMD bash -c 'source ~/env/bin/activate \
    && ./scripts/release.bash \
    && honcho start -f Procfile-deployed'
