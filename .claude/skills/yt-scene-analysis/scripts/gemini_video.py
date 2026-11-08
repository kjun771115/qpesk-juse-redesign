#!/usr/bin/env python3
"""Gemini API로 영상(유튜브 URL 또는 로컬 파일)을 분석한다. 표준 라이브러리만 사용.

usage: gemini_video.py SOURCE --mode {scenes,summary,transcript} --out FILE
env:   GEMINI_API_KEY (필수), GEMINI_MODEL (선택)
"""
import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

DEFAULT_MODEL = "gemini-2.5-flash"  # AI Studio의 최신 Flash 모델명으로 GEMINI_MODEL 지정 권장
BASE = "https://generativelanguage.googleapis.com"

PROMPTS = {
    "scenes": (
        "이 영상을 장면 단위로 분석해 한국어 markdown으로 작성하라. 각 장면은 다음 형식:\n"
        "### [mm:ss–mm:ss] 장면 제목\n- 화면 내용: ...\n- 화면 텍스트(원문 그대로): ...\n"
        "- 핵심 포인트: ...\n영상 처음부터 끝까지 빈 구간 없이. 보이지 않는 내용은 추측하지 말고 "
        "불확실하면 (불확실)이라고 표시하라."
    ),
    "summary": (
        "이 영상의 핵심을 한국어로 요약하라: 1) 한 줄 요약 2) 핵심 주장 3~7개(각각 근거가 나오는 "
        "타임스탬프 [mm:ss] 포함) 3) 시청자가 실행할 수 있는 단계 4) 언급된 도구·용어 목록."
    ),
    "transcript": (
        "이 영상의 음성을 원어 그대로 전사하라. 10~15초 단위 문단으로 나누고 각 문단 앞에 "
        "[mm:ss] 타임스탬프를 붙여라. 요약하거나 의역하지 말 것. 다른 설명은 출력하지 말 것."
    ),
}


def req(method, url, key, body=None, headers=None, raw=False):
    h = {"x-goog-api-key": key}
    h.update(headers or {})
    data = body if isinstance(body, (bytes, type(None))) else json.dumps(body).encode()
    if data is not None and "Content-Type" not in h:
        h["Content-Type"] = "application/json"
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=600) as resp:
            return resp if raw else json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {url}\n{e.read().decode(errors='replace')[:2000]}")


def upload(path, key):
    size = os.path.getsize(path)
    mime = mimetypes.guess_type(path)[0] or "video/mp4"
    start = req("POST", f"{BASE}/upload/v1beta/files", key,
                {"file": {"display_name": os.path.basename(path)}},
                {"X-Goog-Upload-Protocol": "resumable", "X-Goog-Upload-Command": "start",
                 "X-Goog-Upload-Header-Content-Length": str(size),
                 "X-Goog-Upload-Header-Content-Type": mime}, raw=True)
    up_url = start.headers["x-goog-upload-url"]
    with open(path, "rb") as f:
        info = req("POST", up_url, key, f.read(),
                   {"Content-Type": mime, "X-Goog-Upload-Offset": "0",
                    "X-Goog-Upload-Command": "upload, finalize"})
    file = info["file"]
    while file.get("state") == "PROCESSING":
        time.sleep(5)
        file = req("GET", f"{BASE}/v1beta/{file['name']}", key)
    if file.get("state") != "ACTIVE":
        sys.exit(f"file not active: {file}")
    return {"file_data": {"mime_type": mime, "file_uri": file["uri"]}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--mode", choices=PROMPTS, default="scenes")
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt", help="기본 프롬프트 대신 사용할 지시문")
    a = ap.parse_args()

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set (Google AI Studio > Get API key)")
    model = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL)

    if a.source.startswith(("http://", "https://")):
        video = {"file_data": {"file_uri": a.source}}
    else:
        video = upload(a.source, key)

    body = {"contents": [{"parts": [video, {"text": a.prompt or PROMPTS[a.mode]}]}]}
    res = req("POST", f"{BASE}/v1beta/models/{model}:generateContent", key, body)
    try:
        text = "".join(p.get("text", "") for p in res["candidates"][0]["content"]["parts"])
    except (KeyError, IndexError):
        sys.exit(f"unexpected response: {json.dumps(res, ensure_ascii=False)[:2000]}")

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(text.rstrip() + f"\n\n---\n_분석: Gemini `{model}` · mode={a.mode}_\n")
    print(f"wrote {a.out} ({len(text)} chars, model={model})")


if __name__ == "__main__":
    main()
