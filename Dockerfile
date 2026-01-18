# Focus Warden Docker Container
# Note: This requires X11 forwarding for the GUI to work

FROM python:3.11-slim

# Install system dependencies for GUI and screenshot
RUN apt-get update && apt-get install -y \
    python3-tk \
    scrot \
    xclip \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY focus_warden.py .

# Set environment for headless screenshot support
ENV DISPLAY=:0

# Run the application
CMD ["python", "focus_warden.py"]
