#!/bin/bash

# Simple script to build and run the news scraper test in Docker

echo "=========================================="
echo "  Copper News Scraper Test"
echo "=========================================="
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build -f Dockerfile.test -t copper-news-scraper-test .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo ""
echo "✅ Docker image built successfully!"
echo ""

# Run the container
echo "🚀 Running news scraper test..."
echo ""
docker run --rm copper-news-scraper-test

echo ""
echo "=========================================="
echo "  Test completed!"
echo "=========================================="
