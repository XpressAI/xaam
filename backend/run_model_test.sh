#!/bin/bash

# Build a Docker image for testing
docker build -f Dockerfile.unittest -t xaam-unittest .

# Run a specific test file
docker run --rm xaam-unittest pytest -xvs backend/tests/unit/test_models.py