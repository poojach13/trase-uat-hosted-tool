#!/bin/sh
# Installs the tool's dependencies when Trase builds the hosted image.
set -e
pip install --no-cache-dir -r requirements.txt
