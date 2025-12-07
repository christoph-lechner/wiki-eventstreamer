#!/bin/bash

# report git commit id
echo "git commit id:"
git log -1 --pretty=format:%H || echo "failed to determine git commit id"


set -xe

# set up virtual environment
source /home/dataacq/venv_wikistreamreader_prod/bin/activate

# run with relative path, to make sure we are in the correct working directory
./wikistreamreader.py --status_port=9090
