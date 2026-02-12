# Base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install dependencies and Chromium
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    curl \
    wget \
    unzip \
    chromium \
    xvfb \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Set environment variables for Chromium
ENV CHROME_BIN="/usr/bin/chromium"
ENV server_config="True"
ENV DISPLAY=:99

# Run the process-based app with virtual display
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & python app.py"]

