#!/usr/bin/env bash

ARG_FILE=.env
SAMPLE_ARG_FILE=sample.env

if [ -f "$ARG_FILE" ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo No .env file found. Please create one based on the sample.env file.
  exit 1
fi

docker compose up -d