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

## Collaborative thesis → antithesis → synthesis

The purpose is a better shared proposal, not winning an argument. Independent first ideas are
useful; ownership must not prevent combining them. Use the same bounded phases in peer.py:

1. `proposal`: state an initial idea (thesis), why it helps the user and what to discuss with the peer.
2. `critique`: respond to the other idea (antithesis): what is useful, what is missing, what you would
   change and why. Ask "What if we combine this with ...?" Do not manufacture opposition.
3. `revision`: synthesize a genuinely improved proposal. Specify which useful elements from each
   side were retained, changed or dropped, and how the new whole serves the user's goal better.
   Both sides respond to that synthesis. Agreement is allowed; forced compromise is not required.
4. `judge`: a fresh session acts as synthesis editor and completion reviewer, not a score referee.
   Check whether the resulting proposal answers the user's request, resolves the actual concerns,
   and is concrete enough to explain. Identify what AI can finish itself and what only the user
   can choose. Produce a usable joint recommendation in plain language, not a leaderboard.
5. If one specific unresolved issue can improve the synthesis within budget, `final` exchanges
   explore it and `verdict` edits the final shared proposal. Otherwise stop and report progress.
   Further thesis/antithesis/synthesis cycles require the next user-directed planning round.

Do not calculate a winner from points or report a tie. Numeric scoring is OPTIONAL internal
support only if useful or explicitly requested; store it in records, never the default HTML.
Existing rubric/score fields remain supported for older records, not required for new debate.
If the user asks for scoring again, preserve the grounded-score rules: no unsupported numbers,
no success-probability claims, and constraints override totals. The user still receives a clear
recommendation, not a homework assignment to interpret scores.

A synthesis must say what is proposed, why, what will be done, what remains, and which specific
preference/direction question needs user input. Do not claim the user approved an AI agreement.

## User input

Ask immediately when an answer changes the premise; otherwise present the joint proposal first and ask at most three direction/preference questions
with plain consequences and a recommended default. Always allow free text. Participants
flag questions to the coordinator; only the coordinator asks the user in the host conversation.
AI handles research, comparisons and internal checks itself within the authorized scope. Do not
ask the user to perform generic hypothesis validation or interpret a tied score. If an external
fact genuinely cannot be checked, explain only the practical effect on the proposal.
Pause the affected topic before asking. No answer is not consent. Unrelated topics may proceed
within the run budget. Record exact answer, interpreted constraint and affected claim IDs.
New input does not reset call budgets. If necessary, finish with unresolved work and request a
new bounded cycle. Never let a judge resolve the user's risk preferences on their behalf.

## Documents and evidence

Use `discussion-template.md` as the topic layout. Bridge state is mechanical bookkeeping,
not a substitute for readable discussion. Preserve chronological outputs below the current
shared proposal. Research uses the host's authorized tools; peer calls receive cited excerpts and dates.
AI role-play of a customer is not customer evidence. For design, compare actual task flows or
prototypes when available. For technical and business plans, separate known facts from estimates.
Do not store secrets or unnecessary personal data in Git-bound discussions.

## Solo developer default and resource questions

Assume the user is a solo developer using AI assistance unless they provide another team setup.
No separate testers, QA staff, designers or recruitable validation participants are assumed.
Do not ask how many developers/testers/validators they can supply, or require recruiting people
before useful planning can proceed. Do not turn an unknown resource count into a blocking question.

If a materially different plan depends on team size and it is unknown, one optional broad question
is allowed: "혼자 개발하는 기준으로 진행 중임. 함께하는 팀이 있다면 알려주면 반영 가능함."
Never repeat it across topics or rounds. Without an answer, continue with the explicit solo assumption.
Volunteered staffing information can support a broader proposal, but it is not a prerequisite.

Prefer a scope one person can build and operate, staged delivery, automation and AI-owned checks.
When outside user feedback is truly important, explain its specific benefit and propose an optional
small next step; do not ask for a headcount or present a recruited test group as already available.
Solo defaults must be included in peer and synthesis-review prompts so peers do not reintroduce
resource questionnaires. Filter such routine peer questions before presenting feedback to the user.
No user answer may be invented; the solo assumption remains labeled as an assumption.
