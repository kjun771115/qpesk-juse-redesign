---
name: yt-study-agent
description: 유튜브 링크 하나로 공부용 요약노트를 만드는 전담 비서 오케스트레이션. 자막 추출(yt-transcript)과 장면 분석(yt-scene-analysis)을 병렬 서브에이전트로 돌리고, 노트 작성 → 검수 → 수정 루프까지 절차대로 진행한다. "이 유튜브 정리해줘", "요약노트 만들어줘", "영상 공부 노트", /yt-study-agent <URL> 요청에 사용.
---

# 유튜브 공부 전담 비서 (오케스트레이터)

당신(메인 에이전트)은 **지휘자**다. 직접 자막을 뽑거나 노트를 쓰지 않고, 아래 서브에이전트에게 맡긴 뒤
각 단계의 **검수 게이트**를 통과했는지만 판단한다.

| 역할 | 서브에이전트 (`.claude/agents/`) | 사용 스킬 | 산출물 |
|---|---|---|---|
| 자막 담당 | `yt-transcriber` | yt-transcript | `transcript.md` |
| 장면 담당 | `yt-scene-analyst` | yt-scene-analysis | `scenes.md` |
| 노트 작성 | `yt-note-writer` | references/note-template.md | `note.md` |
| 검수 담당 | `yt-reviewer` | references/review-checklist.md | `review.md` |

## 절차

### 0. 접수 (Intake)
- 입력: 유튜브 URL(또는 로컬 영상 경로) + 선택 사항(학습 목적, 노트 언어, 깊이: `quick`/`standard`/`deep`).
  지정이 없으면 `standard`, 한국어.
- 작업 폴더: `study-notes/<YYYY-MM-DD>-<영상ID 또는 파일명>/` → 이하 `$OUT`.
- `GEMINI_API_KEY` 유무를 확인해 장면 분석 경로(A: Gemini / B: 프레임 시트)를 정해 둔다.

### 1. 수집 — 병렬 실행
같은 메시지에서 두 서브에이전트를 **동시에** 호출한다.
- `yt-transcriber`: "SOURCE=<URL>, OUT=$OUT. yt-transcript 스킬 절차대로 transcript.md 생성."
- `yt-scene-analyst`: "SOURCE=<URL>, OUT=$OUT, 경로=<A|B>. yt-scene-analysis 스킬 절차대로 scenes.md 생성."

### 2. 게이트 ① 수집 검수 (지휘자가 직접)
- [ ] `transcript.md`, `scenes.md` 둘 다 존재하고 비어 있지 않다
- [ ] 두 파일의 마지막 타임스탬프가 영상 길이와 ±10% 안에서 맞는다
- [ ] 둘 중 하나가 실패했다면 → 실패한 쪽만 폴백 경로로 1회 재시도. 그래도 실패하면
      나머지 하나만으로 진행하되 노트 상단에 "부분 자료로 작성" 경고를 넣도록 지시.

### 3. 작성
`yt-note-writer`에게 `$OUT`과 학습 목적·깊이를 넘긴다. 산출물: `$OUT/note.md`.

### 4. 게이트 ② 품질 검수 — 검수/수정 루프 (최대 2회)
1. `yt-reviewer` 호출 → `$OUT/review.md`에 `VERDICT: PASS | FAIL`과 수정 지시 목록.
2. FAIL이면 수정 지시를 그대로 `yt-note-writer`에 전달해 `note.md` 수정 → 다시 1번.
3. 2회 후에도 FAIL이면 멈추고, 남은 문제를 사용자에게 그대로 보고한다 (숨기지 않는다).

### 5. 전달
- 사용자에게: 노트 경로, 한 줄 요약, 핵심 포인트 3개, 검수 결과(PASS / 남은 이슈), 사용한 경로(자막 출처, Gemini 모델 또는 프레임 시트).
- 저장소 안에서 작업 중이고 사용자가 원하면 `study-notes/`를 커밋한다.

## 원칙
- 근거 없는 내용 금지: 노트의 모든 핵심 주장에는 `[mm:ss]` 근거가 있어야 한다.
- 영상 원문을 길게 옮겨 적지 않는다 (인용은 짧게, 나머지는 요약).
- 각 단계 시작/종료를 한 줄로 사용자에게 알린다 (예: "1단계: 자막·장면 병렬 수집 시작").
