# Telegram Document Converter

A simple Telegram bot for converting documents and images between formats using LibreOffice and pdf2docx.
Supports PDF, Word, PowerPoint, and image files.

## Setup
### 1. Create a .env file

```
BOT_TOKEN=your_telegram_bot_token
ALLOWED_USERS=123456789,987654321
```
- Leave the ALLOWED_USERS field empty to allow anyone to use the bot.
### 2. Build the image

```
./build.sh
```


### 3. Run the container
```
./docker.sh
```
The bot will start in the background and begin polling Telegram.

## Notes

- Files are automatically deleted after conversion.

- You can mount local folders to persist files if needed:

```
docker run -d --env-file .env \
  -v $(pwd)/downloaded:/app/downloaded \
  -v $(pwd)/converted:/app/converted \
  telegram-document-converter
```

- To update the bot, rebuild and re-run:

```
./build.sh
docker stop telegram-document-converter && docker rm telegram-document-converter
./docker.sh
```

## Requirements
- Docker (or Docker Desktop with WSL2 on Windows)

- A valid Telegram bot token

## Supported Conversions

| From    | To   |
| ------- | ---- |
| DOCX    | PDF  |
| PDF     | DOCX |
| PPTX    | PDF  |
| PDF     | PPTX |
| JPG/PNG | PDF  |
| PDF     | PNG  |
