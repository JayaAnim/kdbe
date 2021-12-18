#!/bin/bash

set -ueo pipefail


apt-get update

# Install git
apt-get -y install git

# Install pip
apt-get -y install python3-pip
python3 -m pip install -U pip
python3 -m pip install wheel

# Install from local kbde or from repo
python3 -m pip install ./kbde \
    || python3 -m pip install git+https://gitlab.com/kb_git/kbde.git
