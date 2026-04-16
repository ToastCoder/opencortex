#!/bin/zsh

# OpenCortex
# run.sh

#!/bin/zsh

# Build the image and name it 'opencortex'
docker build -t opencortex .

# Run the container using host networking for easy Ollama access
docker run --network host opencortex