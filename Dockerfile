FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chromium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxss1 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV PORT=8000
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Start the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 