# Conclusion report

Create or update `<output-base>/round-NNN/conclusion-report.html` at the end of EVERY planning run,
including runs that end with pending user input or unresolved topics. If the initial destination
is unknown, honor the entry gate first. Aggregate ALL existing topics for this initiative, not
just this run's three topics. Include round number, previous report link, and a concise comparison
of changed decisions, reasons and newly available evidence. Carry-forward conclusions must be
labeled with their source round; do not imply that unchanged old scores were re-evaluated. Reconcile discussion index, topic directories, state and decisions.
If a record is missing or contradictory, show that limitation instead of inferring a conclusion.
Read source Markdown and state from the current round's `records/` (legacy rounds retain their old paths).
Markdown remains the source of record; HTML is a readable derived report, never a second decision store.

## Editorial passes (required)

1. Read [ELI5](editorial/eli5/SKILL.md). Explicit audience: nontechnical adult decision-maker,
   not a literal child. Explain what was decided, why it matters and what happens next. Define
   necessary jargon on first use; use concrete examples only when they clarify. Never sacrifice
   factual accuracy for simplicity; this overrides upstream's suggestion to accept 80% accuracy.
2. Read [korean-humanizer source instructions](editorial/korean-humanizer/instruction.md),
   using the bundled [taxonomy](editorial/korean-humanizer/references/ai-tell-taxonomy.md) as needed.
   These pinned sources are packaged locally; do NOT run the upstream npx stub or updater.
   Apply to the report draft, not to verbatim debate transcripts. Preserve names, numbers,
   scores, conditions, citations and dissent. Source attribution and MIT licenses are adjacent.
3. User-required register overrides casual upstream examples: Korean formal report style with
   `~함`, `~임`, `~필요`, `~예정`, or clear noun endings. No `~해요`, chatty questions, emojis or
   promotional filler. Prefer `고객 5명에게 확인 필요` over `고객 대상 검증의 수행 필요성 존재`.
   Noun endings must not produce opaque noun chains. Use neutral language; do not claim stylistic
   patterns prove AI authorship. At most two editing passes; preserve limitations rather than
   polishing uncertain claims into facts. Do not print editorial diagnostics in the reader's report.

## Content and layout

Use `assets/conclusion-report.html` as an adaptable starting point, not a mandatory rigid layout.
Replace every example/placeholder before delivery. Set title, initiative, update date and scope.
Lead with the overall conclusion, then a compact map/table of EVERY topic with state, recommendation,
confidence, user approval status, blockers and links to its section and original discussion.
For each topic: plain-language conclusion, why, options compared, judge scores and their reasons,
remaining dissent, required validation, user decision and next action. Preserve unassessable scores;
never plot them as zero. Do not rank unrelated topics or different scoring rubrics together.
Include source dates and evidence links; distinguish empirical measures from model review scores.

Visualize where it clarifies: labeled 0–5 bars for comparable criteria, a decision/approval flow,
phase roadmap, system diagram or screen-flow examples. Every chart needs units, a plain-language
caption and a text/table equivalent. Illustrative screens/images must be labeled as examples,
not as validated product behavior. Do not invent chart data or dates to make visuals attractive.

Flat, quiet design: white/off-white background, dark text, one restrained accent, thin borders,
ample space, readable type (body at least 16px), comfortable line height, limited content width.
No decorative gradients, glass panels, large shadows or ornamental motion. Mobile layout,
keyboard navigation, visible focus, semantic headings, contrast and print CSS are required.
Use clear status text as well as color. Keep technical implementation details out of the report.

No blanket tool restriction: use SVG, Mermaid rendered to SVG, Chart.js, Three.js, screen mockups,
or available image generation when materially useful. Do not force 3D or images into simple
comparisons. Use the host's available image-generation capability; do not introduce API keys.
If a requested tool is unavailable, use an honest suitable alternative. All essential conclusions
must remain readable without JavaScript, network, WebGL or optional visual assets. Prefer inline
CSS/SVG and embedded images for a portable HTML; locally bundle needed libraries/assets and link
relatively when embedding is impractical. Avoid CDN-only core content or runtime fetch of MD/JSON
that breaks when the report is opened via file://. Never insert raw untrusted text as HTML/script.

## Verification and handoff

- Match topic count/IDs/statuses, scores, recommendations and user approvals against source MD.
- Confirm no placeholders, fabricated facts, missing/unlinked topics or broken relative links.
- Open/render at desktop and mobile widths with available browser tools; inspect overflow,
  labels, table readability, keyboard controls and print layout. Repair before delivery. If visual
  tools are unavailable, disclose that visual QA is unverified instead of claiming success.
- Open the HTML in the host preview/browser when supported, otherwise provide its absolute file
  link and tell the user it can be opened directly in a browser. Link it from `records/README.md` using `../conclusion-report.html`. Present the HTML as the
  default deliverable; it must be understandable without opening any MD. Links from the report
  to detailed evidence use `records/...` and are secondary.
- A later decision or user answer requires refreshing this same report, including its timestamp.
