#!/bin/bash
docker run -d --env-file --network host .env telegram-document-converter
