#!/bin/bash

set -xe

# set up virtual environment
source /home/dataacq/venv_wikistreamreader_prod/bin/activate

# run with relative path, to make sure we are in the correct working directory
./wikistreamreader.py
