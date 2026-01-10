#!/bin/bash

echo "Starting Align - AI-Powered Mockup Generator"
echo "============================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and add your GEMINI_API_KEY"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Starting services with Docker Compose..."
docker-compose up --build

echo ""
echo "============================================="
echo "Align is now running!"
echo "Backend API: http://localhost:8000"
echo "Frontend App: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "============================================="
