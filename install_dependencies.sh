#!/bin/bash

# Install system dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev
elif [[ "$OSTYPE" == "darwin"* ]]; then
    brew install portaudio
fi

# Install Python dependencies
pip install -r requirements.txt
pip install pyaudio
