#!/usr/bin/env sh

if [ "$#" -ne 3 ] || ! [ -d "$1" ]; then
  echo "Usage: $0 [DATASET PATH] [DESTINATION PATH] [MODEL PATH]" >&2
  exit 1
fi

DATASET_DIR=$(readlink -f "$1")
DESTINATION_PATH=$(readlink -f "$2")
MODEL_PATH=$(readlink -f "$3")

mkdir -p "$DESTINATION_PATH"

python3 code/generate_plots.py --data "$DATASET_DIR" --dst "$DESTINATION_PATH" --explore-model "$MODEL_PATH"
