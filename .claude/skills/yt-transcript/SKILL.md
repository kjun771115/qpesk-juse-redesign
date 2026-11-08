---
name: yt-transcript
description: 유튜브 링크(또는 로컬 영상 파일)에서 타임스탬프가 붙은 자막/대본을 추출한다. "자막 추출", "대본 뽑아줘", "transcript" 요청이나 yt-study-agent 오케스트레이션의 1단계에서 사용.
---

# 자막 추출 (yt-transcript)

입력: 유튜브 URL 또는 로컬 영상 경로, 출력 폴더(`$OUT`)
출력: `$OUT/transcript.md` (타임스탬프 `[mm:ss]` 단위 대본), `$OUT/transcript.meta.json`

## 절차

1. **유튜브 자막 우선** (가장 정확·무료)
   ```bash
   python3 .claude/skills/yt-transcript/scripts/fetch_transcript.py "<URL>" --out "$OUT" --langs ko,en
   ```
   - `yt-dlp`가 없으면 `pip install -U yt-dlp` 후 재시도.
   - 수동 자막 → 자동 자막 순서로 시도한다. 결과 meta의 `source`가 `manual`/`auto` 중 무엇인지 기록.
2. **자막이 없거나 로컬 파일이면 → Gemini 음성 전사로 폴백**
   ```bash
   python3 .claude/skills/yt-scene-analysis/scripts/gemini_video.py "<URL 또는 파일>" \
     --mode transcript --out "$OUT/transcript.md"
   ```
   (`GEMINI_API_KEY` 필요. 없으면 사용자에게 요청하고 멈춘다.)
3. **자체 검수** — 아래를 모두 만족해야 완료로 보고한다.
   - [ ] `transcript.md`가 비어 있지 않고 첫 줄부터 `[00:00]` 형식 타임스탬프가 있다
   - [ ] 마지막 타임스탬프가 영상 길이와 대략 일치한다 (meta의 `duration`과 비교)
   - [ ] 자동 자막의 중복 줄(롤링 자막)이 제거되었다
   - [ ] 언어와 출처(manual/auto/gemini)를 meta에 남겼다

## 실패 시 보고 형식
어떤 단계에서 무엇이 실패했는지(예: "YouTube 접근 차단 → Gemini 폴백 성공")를 한 줄로 남긴다. 추측으로 대본을 만들지 않는다.
