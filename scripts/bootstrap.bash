#!/bin/bash

set -ueo pipefail


# Clone the repo
git clone https://gitlab.com/kb_git/kbde.git

# Install
python3 -m pip install kbde/

# Cleanup
rm kbde/ -rf
