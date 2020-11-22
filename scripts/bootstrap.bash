#!/bin/bash

set -ueo pipefail


# Make sure that pip is installed
apt-get -y install python3-pip

# Clone the repo
git clone https://gitlab.com/kb_git/kbde.git

# Install
python3 -m pip install kbde/

# Cleanup
rm kbde/ -rf
