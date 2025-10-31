# --- Base Image ---
FROM python:3.12-slim

# --- Install system dependencies (LibreOffice + fonts + runtime libs) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    fonts-dejavu \
    fonts-liberation \
    ghostscript \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Set working directory ---
WORKDIR /app

# --- Copy project files ---
COPY . /app

# --- Install Python dependencies ---
RUN pip install --no-cache-dir -r requirements.txt

# --- Create necessary folders ---
RUN mkdir -p /app/downloaded /app/converted

# --- Set environment variables ---
ENV PYTHONUNBUFFERED=1 \
    PATH="/usr/lib/libreoffice/program:${PATH}"

# --- Command to run the bot ---
CMD ["python", "bot.py"]
