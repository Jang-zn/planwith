# Planning quality and operating modes

## Preflight

Run `python3 <skill>/scripts/doctor.py --project <captured-host-cwd>` before the first
participant call on this machine/session. It checks Python, CLI versions/options and subscription
login without model calls. It reports environment variable names only, never values or account IDs.
If it fails, fix the stated issue or report it; never fall back to an API or bypass auth checks.

## Mode

Record mode with `rounds.py new --mode quick|standard|deep`. Default standard without another
question. Infer quick for a lightweight sanity check, deep for explicit implementation-readiness.
Explain the selected mode briefly. All modes retain independent proposals, rebuttal, revision,
synthesis review, internal evidence, user gates and a human-readable report; mode changes scope, not truth standards.

| Mode | Scope |
|---|---|
| quick | One decision, one exchange, compact report; unresolved breadth goes to backlog |
| standard | Up to three material decisions, default exchange and optional targeted final exchange |
| deep | Up to three material decisions with explicit architecture, operations, failure scenarios and validation criteria |

Deep does not mean unlimited calls; expand topics only when the user requests it.

## Evidence ledger

Write `records/evidence.json` as a list of records with `id`, `kind` (fact/user/inference/hypothesis),
`claim`, `source` (URL or local document/claim reference), `checked_at` (date), and `limitation`.
Keep readable source explanations in sources.md and cite ledger IDs in proposals and scores.
User-provided constraints are evidence of preference, not proof of market demand. Every uncertain
claim needs a cheap validation action, success/failure threshold and the decision that would change.
Never fabricate sources or represent two models' agreement as independent customer evidence.

## Optional internal rubric

No points competition. The fresh reviewer edits the synthesis and checks completion. Older
score/rubric records remain readable, and scoring may be requested explicitly, but new topics
normally use `alternatives: []`. Never expose points, ties or ranking as the report's conclusion.
The existing preset weight validation applies only when numerical alternatives are provided.

## Impact tracking

Write `records/impacts.json` as a list (empty for first round with no changes). Each entry has
`decision`, `before`, `after`, `reason`, and `areas`: list of objects with `name`, `status`
(updated/retained/review_needed), `reason`. Check target, problem, price, MVP, UX, architecture,
data, operations and validation for each material change. Exclude an area only with a stated reason.
Link changed documents and claim IDs in changes.md. Never mark retained merely because nobody
looked at it. Translate material pending impacts into plain unfinished work, and do not label the plan implementation-ready
while material dependencies remain unreviewed.

## Structured report checks

Store conclusion.json beside each topic's discussion.md/state.json. Keep existing internal keys
(id, title, status, recommendation, confidence, approval, approval_evidence, rubric, questions,
unknowns, blockers, dissent, next_action). Use alternatives: [] unless internal scoring is needed.
Evidence and impact ledgers remain internal. User approval still requires an actual user record.

Add a REQUIRED `reader` object. These are the only topic fields used for the reader narrative:

```json
{
  "kind": "design",
  "question": "처음 화면에는 무엇을 보여줄까?",
  "conversation": [
    {"speaker": "Claude의 첫 생각", "point": "한 달에 쓰는 돈을 먼저 보여주자는 제안임."},
    {"speaker": "Codex의 보완", "point": "곧 돈이 나가는 날짜를 먼저 알아야 놓치지 않는다는 의견임."},
    {"speaker": "함께 다듬은 방향", "point": "다가오는 결제를 위에 두고, 월 지출은 작게 함께 보여주기로 제안함."}
  ],
  "result": "다가오는 결제를 가장 먼저 보여주는 화면으로 제안함.",
  "why": "언제 돈이 나가는지 바로 찾으면서 전체 지출도 볼 수 있기 때문임.",
  "direction": "첫 화면은 간단하게 구성하려 함.",
  "plan": ["다가오는 결제 표시", "월 지출 요약 표시"],
  "ai_tasks": ["작은 휴대폰에서도 글자가 잘 보이도록 화면 크기 조정 예정"],
  "unfinished": ["실제 결제 정보를 가져오는 기능은 아직 만들지 않음"],
  "feedback": [{
    "question": "날짜와 총지출 중 무엇을 더 먼저 보고 싶은가?",
    "recommendation": "날짜를 먼저 보여주는 방향을 추천함.",
    "why_user": "자주 확인하고 싶은 정보는 사용자 선호에 따라 달라짐.",
    "options": [{"label": "결제 날짜", "effect": "다가오는 결제를 먼저 확인"}, {"label": "총지출", "effect": "이번 달 지출을 먼저 확인"}]
  }],
  "visuals": [{"type": "screen", "title": "첫 화면 예시", "caption": "위에서 날짜를 보고 아래에서 총지출을 확인하는 구성임.", "screen_title": "다가오는 결제", "elements": [{"type": "card", "label": "음악 서비스 · 내일 · 10,000원 (예시)"}, {"type": "text", "label": "이번 달 총지출 30,000원 (예시)"}, {"type": "button", "label": "구독 추가"}]}]
}
```

Example is illustrative only; never use these fictional comments as an actual debate transcript.
kind: general/design/engineering. The latter two require inline visuals. flow visuals use `steps`
(list of at least two plain labels), title and caption. image visuals use path (relative to round),
alt, title and caption; PNG/JPEG/WebP up to 10 MB, embedded for portability. screen elements accept
text/field/button/card. No raw HTML or executable scripts from participant output.
Empty feedback means no user decision needed; still invite optional thoughts. Lists for plan,
ai_tasks and unfinished may be empty if truthful. Never assign AI's research homework to the user.

report.json retains title, summary and ALL topic_ids in sorted order. Summary must explain the
shared direction in plain language. Run report.py render and verify. Automated checks detect
missing topics, narrative fields, score/state issues and source changes. They cannot establish
that the written story accurately represents the discussion; the coordinator must read both.

## Recovery

Use `peer.py ... status` for saved phase, calls remaining, time remaining and next action.
Failures are recorded in discussion.md and consume budget. Do not retry a judge beyond its phase
cap or silently start a new round. Respect existing locks; clear a stale lock only after confirming
no runner is active. A quota problem waits for quota/account recovery; no polling or API fallback.
