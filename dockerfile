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
    chromium-driver \
    xvfb \
    libnss3 \
    libfontconfig1 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app/

# Set environment variables for Chromium
ENV CHROME_BIN="/usr/bin/chromium"
ENV CHROMEDRIVER_PATH="/usr/bin/chromedriver"
ENV DISPLAY=:99

# Run the process-based app with virtual display
CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & python app.py"]

