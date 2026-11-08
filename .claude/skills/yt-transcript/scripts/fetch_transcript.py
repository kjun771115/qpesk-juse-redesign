#!/usr/bin/env python3
"""YouTube 자막을 yt-dlp로 받아 타임스탬프 대본(markdown)으로 정리한다.

usage: fetch_transcript.py URL --out DIR [--langs ko,en]
       fetch_transcript.py --vtt FILE.vtt --out DIR   (이미 받은 VTT만 정리)
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

TS = re.compile(r"(\d+):(\d{2}):(\d{2})[.,](\d{3})\s+-->")
TAG = re.compile(r"<[^>]+>")


def to_seconds(h, m, s):
    return int(h) * 3600 + int(m) * 60 + int(s)


def fmt(sec):
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def parse_vtt(path):
    """VTT -> [(sec, text)], 롤링 자동자막의 중복 줄 제거."""
    cues, cur_t, buf = [], None, []
    with open(path, encoding="utf-8", errors="replace") as f:
        for raw in f:
            line = raw.strip()
            m = TS.match(line)
            if m:
                if cur_t is not None and buf:
                    cues.append((cur_t, buf))
                cur_t, buf = to_seconds(*m.groups()[:3]), []
            elif line and cur_t is not None and not line.isdigit():
                buf.append(TAG.sub("", line).strip())
        if cur_t is not None and buf:
            cues.append((cur_t, buf))

    out, seen_last = [], ""
    for t, lines in cues:
        for text in lines:
            if not text or text == seen_last:
                continue
            # 롤링 자막: 이전 줄을 포함해 길어지는 경우 마지막 것만 남김
            if out and text.startswith(out[-1][1]) and t - out[-1][0] <= 5:
                out[-1] = (out[-1][0], text)
            elif out and out[-1][1].endswith(text):
                continue
            else:
                out.append((t, text))
            seen_last = text
    return out


def group(lines, window=15):
    """window초 단위로 문단을 묶어 읽기 좋게."""
    paras, start, buf = [], None, []
    for t, text in lines:
        if start is None:
            start = t
        if t - start >= window and buf:
            paras.append((start, " ".join(buf)))
            start, buf = t, []
        buf.append(text)
    if buf:
        paras.append((start, " ".join(buf)))
    return paras


def download(url, out, langs):
    if not shutil.which("yt-dlp"):
        sys.exit("yt-dlp not found: pip install -U yt-dlp")
    info = subprocess.run(
        ["yt-dlp", "-J", "--skip-download", url], capture_output=True, text=True
    )
    meta = json.loads(info.stdout) if info.returncode == 0 else {}
    for flag, source in (("--write-subs", "manual"), ("--write-auto-subs", "auto")):
        subprocess.run(
            ["yt-dlp", "--skip-download", flag, "--sub-langs", langs,
             "--sub-format", "vtt", "-o", os.path.join(out, "sub.%(ext)s"), url],
            capture_output=True, text=True,
        )
        files = sorted(glob.glob(os.path.join(out, "sub*.vtt")))
        if files:
            # langs 우선순위대로 선택
            for lang in langs.split(","):
                for f in files:
                    if f".{lang}" in os.path.basename(f):
                        return f, source, meta
            return files[0], source, meta
    return None, None, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--vtt")
    ap.add_argument("--out", required=True)
    ap.add_argument("--langs", default="ko,en")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    meta = {}
    if a.vtt:
        vtt, source = a.vtt, "vtt-file"
    else:
        vtt, source, meta = download(a.url, a.out, a.langs)
        if not vtt:
            print("NO_SUBTITLES: fall back to gemini_video.py --mode transcript")
            sys.exit(2)

    lines = parse_vtt(vtt)
    paras = group(lines)
    title = meta.get("title", "")
    with open(os.path.join(a.out, "transcript.md"), "w", encoding="utf-8") as f:
        f.write(f"# Transcript{': ' + title if title else ''}\n\n")
        for t, text in paras:
            f.write(f"[{fmt(t)}] {text}\n\n")
    info = {
        "url": a.url, "title": title, "channel": meta.get("channel"),
        "duration": meta.get("duration"), "source": source,
        "vtt": os.path.basename(vtt), "lines": len(lines),
        "last_ts": fmt(lines[-1][0]) if lines else None,
    }
    with open(os.path.join(a.out, "transcript.meta.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
