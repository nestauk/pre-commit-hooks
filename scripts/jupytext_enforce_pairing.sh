#!/usr/bin/env bash
failed=0;
for nb in "$@"; do
  py="${nb%.ipynb}.py";
  if [[ "$nb" == *.ipynb && ! -f "$py" ]]; then
    echo "⚠️  Missing paired file: $py - generating it using jupytext..." >&2;
    jupytext --set-formats ipynb,py:percent "$nb";
    if [[ ! -f "$py" ]]; then
      echo "❌ Paired file $py still missing after generation attempt." >&2;
      failed=1;
    elif [[ -f "$py" ]]; then
      echo "✅ Paired file generated" >&2;
    fi;
  fi;
  if ! git ls-files --error-unmatch "$py" >/dev/null 2>&1; then
    echo "❌ Paired file exists but is not tracked by git: $py" >&2;
    echo "💡 Run: git add \"$py\" \"$nb\"" >&2;
    failed=1;
  fi;
done;
exit $failed;
