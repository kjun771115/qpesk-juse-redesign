---
name: yt-scene-analysis
description: 유튜브 링크나 로컬 영상의 화면(장면)을 분석해 장면별 타임라인·화면 텍스트·시각 자료 설명을 만든다. Gemini API로 영상을 직접 이해시키고, 키가 없으면 ffmpeg 프레임 시트로 Claude가 직접 본다. "장면 분석", "화면 분석", "영상 요약" 요청이나 yt-study-agent 1단계에서 사용.
---

# 장면 분석 (yt-scene-analysis)

입력: 유튜브 URL 또는 로컬 영상 경로, 출력 폴더(`$OUT`)
출력: `$OUT/scenes.md` — 장면별 `[mm:ss–mm:ss] 장면 제목 / 화면 내용 / 화면 텍스트 / 핵심 포인트`

## 경로 A — Gemini (기본, 유튜브 URL 직접 처리 가능)

1. `GEMINI_API_KEY`(Google AI Studio → Get API key)가 환경에 있는지 확인. 없으면 사용자에게 요청.
2. 실행:
   ```bash
   python3 .claude/skills/yt-scene-analysis/scripts/gemini_video.py "<URL 또는 파일>" \
     --mode scenes --out "$OUT/scenes.md"
   ```
   - 모델은 `GEMINI_MODEL` 환경변수로 바꿀 수 있다 (기본값은 스크립트 상단 `DEFAULT_MODEL`). AI Studio에서 최신 Flash 모델명을 확인해 지정.
   - 로컬 파일은 Files API로 업로드 후 `ACTIVE`가 될 때까지 기다린 뒤 분석한다.
   - 핵심 요약만 필요하면 `--mode summary`.

## 경로 B — 프레임 시트 (키 없음 / Gemini 실패 / 교차 검증)

1. 로컬 파일이 아니면 `yt-dlp -f "bv*[height<=720]+ba/b[height<=720]" -o "$OUT/video.%(ext)s" "<URL>"` 로 받는다.
2. 3×3 타일 이미지 생성:
   ```bash
   bash .claude/skills/yt-scene-analysis/scripts/contact_sheets.sh "<영상>" "$OUT/frames" 3
   ```
   (인자 3 = 3초마다 1프레임. 긴 영상은 10~30으로 늘린다. 타일 순서 = 시간 순서, 각 칸 = interval초.)
3. `$OUT/frames/sheet_*.jpg`를 Read 도구로 직접 보고 `scenes.md`를 같은 형식으로 작성한다.
   타일 번호 n, 칸 k(0부터)의 시각 ≈ ((n-1)·9 + k) × interval 초.

## 자체 검수
- [ ] 장면 타임라인이 영상 처음부터 끝까지 빈 구간 없이 이어진다
- [ ] 화면에 보이는 글자(자막·UI·슬라이드)를 원문 그대로 옮겼다
- [ ] 영상에 없는 내용을 추측해 넣지 않았다 (불확실하면 `(불확실)` 표시)
- [ ] 사용한 경로(A/B)와 모델명을 `scenes.md` 맨 아래에 기록했다
