#!/usr/bin/env bash

set -e

python3 -u ./src/video_downloader.py 2>&1 | while read -r line; do
  printf "\e[36m[downloader]\e[0m %s\n" "$line"
done &

for resolution in "${@}"; do
  python3 -u ./src/video_converter.py "$resolution" 2>&1 | while read -r line; do
    printf "\e[33m[converter %s]\e[0m %s\n" "$resolution" "$line"
  done &
done

trap 'kill $(jobs -p)' EXIT
wait
