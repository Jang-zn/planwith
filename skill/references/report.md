# Report for the human, not for agents

Create/update `<output-base>/round-NNN/conclusion-report.html`. Cover every current and carried-forward
topic, including unfinished ones. Keep Markdown, evidence IDs, scoring, confidence labels, hypothesis
ledgers, internal quality checks and research methodology in records. These are NOT report sections.
Do not just collapse internal score tables: omit them from reader HTML by default.

## Required reading experience

The reader should immediately understand:
1. What was discussed?
2. What did each side suggest, and how did those ideas improve each other?
3. What conclusion did the agents reach, and why is it useful?
4. What do we propose doing now? What did the user actually decide already?
5. What will AI handle next, and what has not been finished?
6. What direction, choice, preference or added opinion do we want from the user?

Do not populate feedback with tester counts, QA staffing or recruiting questionnaires. Default to
solo development; include a broad optional team-size question only when it changes the direction
and has not already been answered. Prefer AI-owned tasks and a solo-operable scope.

Give the joint recommendation FIRST, explain the short discussion story, and end with an invitation
for feedback. Do not dump transcripts, jargon, confidence labels, evidence IDs, scores or tied
alternatives onto the reader. Do not make them solve the agents' analysis. Recommendations must be
concrete: "처음에는 이름과 날짜만 입력하도록 구성함" rather than "가설 검증 필요".
Uncertainty still matters: if it changes the user's choice, explain its practical consequence in
one simple sentence. Never hide a real blocker or present unverified behavior as completed work.

## Language

Apply bundled [ELI5](editorial/eli5/SKILL.md): vocabulary simple enough for a five-year-old,
short concrete sentences, one thought per sentence. Respect the adult reader; no baby talk.
Explain any unavoidable technical word immediately. Do not sacrifice factual accuracy.
Then use the bundled [Korean editorial source](editorial/korean-humanizer/instruction.md).
Do not execute its upstream npx updater. User register remains `~함`, `~임`, `~예정`, noun endings;
avoid `~해요`, opaque noun chains, jargon, and promotional filler. Changes in content are deliberate
summarization of the discussion, not fabrication of quotes, agreement, work completed or user approval.

## Structure and visuals

Use report.py and the reader schema in quality.md. The author must write the reader narrative
from the actual discussion; a renderer cannot turn an evidence ledger into a good story on its own.
Legacy records without a reader summary must fail with a clear request to write that summary;
do not silently invent dialogue or put the old machine report back on screen.

Discussion summaries may be paraphrases labeled by speaker; do not present paraphrases as verbatim
quotes. Show the initial idea, useful response and resulting synthesis. Never force fictional
opposition into an otherwise agreeable discussion.

Screen-planning topics MUST show actual illustrative screen layouts inline: labels, example inputs,
buttons/cards and the task flow. Engineering topics MUST show a simple labeled flow or diagram of
what happens, not just a component-name list. Mark mockups as examples, distinguish built from planned,
and keep all important information visible without opening another file. A screenshot of text is
not a useful diagram. The renderer supports `screen`, `flow`, and embedded PNG/JPEG/WebP `image`.
Use available image generation/visual tools when helpful; no API fallback or unnecessary decoration.
For interactive/3D needs, extend the structured renderer with an accessible static fallback.

White/light background, flat panels, one restrained accent, readable type, space between ideas,
mobile layout and print CSS. No ornamental animation or inflated dashboards. Topic navigation
and a small optional link to records are enough; avoid a wall of tables and badges.

## Verify

Read the report as the user: can they say "what are we doing and what do they want from me" in
under a minute? Does it explain actual synthesis instead of scores? Does every question truly
need the user's preference? Are unfinished tasks clearly separate from work assigned to AI?
Render and verify source integrity with report.py. Check all topics, approval truth, narrative
fidelity, and inline examples. Inspect desktop/mobile layout when browser tools permit; disclose
unverified visual QA when blocked. Do not rewrite prior round outputs without explicit user request.
Present/open the HTML by default and invite feedback in the host conversation. HTML is a static
report, not a working feedback-submission form; never imply that answers entered there are saved.
