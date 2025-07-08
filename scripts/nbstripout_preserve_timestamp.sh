#!/usr/bin/env bash
for file in "$@"; do
  if [[ "$file" == *.ipynb && -f "$file" ]]; then
    original_timestamp=$(stat -f "%m" "$file" 2>/dev/null || stat -c "%Y" "$file" 2>/dev/null);
    nbstripout "$file";
    if [[ -n "$original_timestamp" ]]; then
      touch -t $(date -r "$original_timestamp" "+%Y%m%d%H%M.%S") "$file" 2>/dev/null || \
      touch -d "@$original_timestamp" "$file" 2>/dev/null;
    fi;
  fi;
done;
