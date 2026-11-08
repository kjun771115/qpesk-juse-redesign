#!/usr/bin/env bash
# usage: contact_sheets.sh VIDEO OUT_DIR [INTERVAL_SEC=3]
# INTERVAL초마다 한 프레임씩 뽑아 3x3 타일(시트)로 묶는다.
set -euo pipefail
VIDEO="$1"; OUT="$2"; IV="${3:-3}"
mkdir -p "$OUT"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")
ffmpeg -v error -y -i "$VIDEO" \
  -vf "fps=1/${IV},scale=480:-1,drawtext=text='%{pts\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.6,tile=3x3" \
  "$OUT/sheet_%02d.jpg" 2>/dev/null || \
ffmpeg -v error -y -i "$VIDEO" -vf "fps=1/${IV},scale=480:-1,tile=3x3" "$OUT/sheet_%02d.jpg"
echo "duration=${DUR}s interval=${IV}s sheets=$(ls "$OUT"/sheet_*.jpg | wc -l)"
