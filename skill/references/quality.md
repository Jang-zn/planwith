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
judge scorecard, evidence, user gates and report; mode changes scope, not truth standards.

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

## Predeclared rubric

Pass `peer.py init --rubric general|discovery|business|design|engineering` BEFORE proposals.
Weights in criterion order (goal fit, evidence, feasibility, cost/risk, rebuttal response):
- general: 20,20,20,20,20
- discovery: 25,35,15,15,10
- business: 20,25,20,25,10
- design: 30,20,20,15,15
- engineering: 15,20,30,25,10

Judge uses these weights unchanged. Scores remain 0–5; totals displayed /100 only when all scores
are assessable. Source-less items are null, not zero. Blocking conditions override total.
Custom rubrics may be discussed but this version's validator supports only these fixed presets.

## Impact tracking

Write `records/impacts.json` as a list (empty for first round with no changes). Each entry has
`decision`, `before`, `after`, `reason`, and `areas`: list of objects with `name`, `status`
(updated/retained/review_needed), `reason`. Check target, problem, price, MVP, UX, architecture,
data, operations and validation for each material change. Exclude an area only with a stated reason.
Link changed documents and claim IDs in changes.md. Never mark retained merely because nobody
looked at it. Surface review_needed in the HTML, and do not label the plan implementation-ready
while material dependencies remain unreviewed.

## Structured report checks

For each `records/discussions/<id>/`, store `conclusion.json` alongside discussion.md/state.json:

```json
{
  "id": "001-target", "title": "초기 타겟", "status": "finished",
  "recommendation": "좁은 타겟부터 검증 필요", "confidence": "낮음: 고객 조사 미실시",
  "approval": "pending", "approval_evidence": [], "rubric": "discovery",
  "questions": ["사용자 선택 필요 항목"], "unknowns": ["가정과 저비용 검증 방법"],
  "blockers": [], "dissent": "남은 반대 의견", "next_action": "다음 행동",
  "alternatives": [{"name": "대안 A", "scores": [
    {"value": null, "reason": "판단 근거 부족", "evidence": [], "limitation": "조사 미실시", "revisit": "고객 인터뷰 후 재평가"}
  ]}]
}
```

The scores array above is abbreviated: supply exactly FIVE objects in criterion order. Use actual
judge output, not coordinator-invented numbers. approval=approved/rejected requires user-kind
ledger evidence of that specific decision. Report status must equal topic state. Waiting topics
may have an empty alternatives list; do not make up a judge assessment.

Write `records/report.json` with `title`, `summary`, `topic_ids` (all topic directory IDs in sorted
order). Retain readable MD as audit evidence. For carried-forward topics, create a clearly labeled
summary record with provenance rather than copying old state/call history. Mark old scores as old.

Run `report.py render --round <round-path>` then `report.py verify --round <round-path>`.
The renderer makes a self-contained report with escaped text, all topics, evidence, score bars,
user decisions, unknowns and impact comparison. Validation checks topic coverage, state, rubric,
score ranges, references and post-render changes. It does NOT prove that JSON faithfully interprets
MD or that cited evidence is true: manually reconcile those before rendering. Later record edits
require re-rendering. No JSON/MD runtime fetch, API, or CDN is needed by the report.
The HTML template can be extended for useful visuals, but regenerate and validate afterwards;
never claim manual HTML edits passed the content-integrity check. Screenshots and semantic review
remain necessary for custom visuals. Use a new structured renderer field for repeatable extensions.

## Recovery

Use `peer.py ... status` for saved phase, calls remaining, time remaining and next action.
Failures are recorded in discussion.md and consume budget. Do not retry a judge beyond its phase
cap or silently start a new round. Respect existing locks; clear a stale lock only after confirming
no runner is active. A quota problem waits for quota/account recovery; no polling or API fallback.
