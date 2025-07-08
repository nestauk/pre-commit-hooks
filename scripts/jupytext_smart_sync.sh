#!/usr/bin/env bash
declare -A processed;
for file in "$@"; do
  if [[ "$file" == *.ipynb ]]; then
    nb_file="$file";
    py_file="${file%.ipynb}.py";
  elif [[ "$file" == *.py ]]; then
    py_file="$file";
    nb_file="${file%.py}.ipynb";
  else
    continue;
  fi;
  pair_key="${nb_file}:${py_file}";
  if [[ ${processed[$pair_key]} ]]; then
    continue;
  fi;
  processed[$pair_key]=1;
  if [[ -f "$nb_file" && -f "$py_file" ]]; then
    echo "❌ Files are out of sync, syncing via jupytext..." >&2;
    jupytext --sync "$py_file";
    echo "✅ Files synced" >&2;
    if git ls-files --modified | grep "$py_file" >/dev/null 2>&1; then
      echo "💡 Untracked modification from sync, run: git add \"$py_file\"" >&2;
    elif git ls-files --modified | grep "$nb_file" >/dev/null 2>&1; then
      echo "💡 Untracked modification from sync, run: git add \"$nb_file\"" >&2;
    fi;
  fi;
done;
