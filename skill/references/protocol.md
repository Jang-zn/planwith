# Bounded planning protocol

## Scope and limits

Handle at most three material topics per user-requested run. Put additional topics in the
backlog; ask before expanding. Each topic permits eight external CLI calls and 30 minutes
of cumulative CLI execution. User waiting time is excluded. Each call defaults to five
minutes (maximum ten). No automatic retries. One manual retry is allowed only for a transient
failure within the existing phase/call budget. No new review cycle without user direction or
an explicit user response introducing new conditions after completion. Record why it reopened.
The script enforces topic limits, phase progression and input gates. The coordinator enforces
the run-wide three-topic limit and semantic rules below; it is not an autonomous background daemon.

## Debate

1. Write the coordinator's independent proposal before seeing the peer's. Send only the common
   brief to the peer for its independent proposal. Give material claims stable IDs (A-01, B-01).
2. Each side restates the strongest version of the other proposal, then identifies at most three
   decision-changing objections with evidence, impact and an alternative. Save both sides.
3. Each side accepts, rejects with reasons, or marks each objection as needing validation.
   Preserve what changed and what did not. Do not demand disagreement for its own sake.
4. Send a standalone judge brief to a fresh CLI call. Prefer the opposite provider to the host.
   Remove author names where practical, label alternatives A/B, and include the constraints,
   evidence, rebuttals, current revised claims and fixed scoring rubric. Do not omit inconvenient
   arguments. Fresh context is not a guarantee of neutrality.
5. The judge may authorize only one additional targeted exchange if the issue changes a real
   decision, has a new unanswered argument, can progress with available evidence, and budget remains.
   Use `final` then `verdict`. Otherwise stop. For important decisions, the remaining verdict call
   may be a different-provider independent check instead. Disagreeing judges do not trigger more judges.

## Scorecard

Score comparable proposals/claims, not models. Default equal weights, set BEFORE seeing proposals:
- Problem/goal fit (0–5)
- Evidence quality (0–5)
- Feasibility under actual constraints (0–5)
- Cost and risk response (0–5)
- Response to material objections (0–5)

Anchors: 0 contradicts requirements/evidence; 1 major unsupported gaps; 2 substantial gaps;
3 plausible with explicit limitations; 4 well supported with minor gaps; 5 strongly supported
and addresses material alternatives. Explain criteria-specific reasoning, do not just repeat anchors.
Use **not assessable** when evidence is absent; do not convert that to zero or compute a misleading
total. When all criteria are assessable, show total /25 (or predeclared weighted total).
Every score requires a claim/evidence reference, limitation, and what could change the score.
Scores are review judgments, not probability of commercial success. Confidence is separate:
low/medium/high with reasons. Disqualifying constraints override totals. Do not average away
missing permissions, essential feasibility or required user choices. Explicitly retain dissent.

Judge output must include score table, per-criterion reasons, decisive differences, assumptions,
blocking conditions, recommendation, confidence, unresolved questions, re-evaluation conditions,
and termination verdict: recommendation / conditional / validation-needed / user-decision / budget.

## User input

Ask immediately when an answer changes the premise; otherwise group up to three questions at
round end with options, consequences and a recommendation. Always allow free text. Participants
flag questions to the coordinator; only the coordinator asks the user in the host conversation.
Pause the affected topic before asking. No answer is not consent. Unrelated topics may proceed
within the run budget. Record exact answer, interpreted constraint and affected claim IDs.
New input does not reset call budgets. If necessary, finish with unresolved work and request a
new bounded cycle. Never let a judge resolve the user's risk preferences on their behalf.

## Documents and evidence

Use `discussion-template.md` as the topic layout. Bridge state is mechanical bookkeeping,
not a substitute for readable discussion. Preserve chronological outputs below the current
scorecard. Research uses the host's authorized tools; peer calls receive cited excerpts and dates.
AI role-play of a customer is not customer evidence. For design, compare actual task flows or
prototypes when available. For technical and business plans, separate known facts from estimates.
Do not store secrets or unnecessary personal data in Git-bound discussions.
