#!/bin/bash
docker run -d --env-file .env --network host telegram-document-converter
