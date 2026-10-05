---
name: planwith
description: Plan or review with both Claude and Codex through their locally authenticated official CLIs. Use when the user asks to plan with Claude/Codex, 코덱스랑 기획, 클로드랑 기획, or cross-model debate. Produces topic-based discussions, grounded judge scorecards, and project planning documents with user decision gates.
---

# Planwith

You are the coordinator in the current conversation. The other official CLI is the peer.
If `PLANWITH_PARTICIPANT=1`, do not orchestrate or invoke this skill; return only the requested contribution.
Use the user's language. Never impersonate the other provider or claim a failed call participated.

Read [protocol.md](references/protocol.md) before starting. Use the bundled `scripts/peer.py`
(relative to this installed skill) for every external participant/judge call. On Windows use
`py -3`; on macOS/Linux use `python3`. Resolve the script and project root to absolute paths.
The user should not need to run bridge commands manually.

## Entry and persistence

1. Resolve the working project's root (Git root when applicable, otherwise working directory).
   Honor the user's output location; default to `docs/<initiative>/`. Never put deliverables in
   the installed skill directory. Read existing brief, decisions and discussion index first.
2. Extract goals, constraints and evidence from the current conversation. Ask only material
   missing questions. Do not silently assume personal use versus a public commercial product.
3. Create/update `README.md`, `00-brief.md`, `decisions.md`, `open-questions.md`, `sources.md`.
   Create substantive target/problem, product, business/operations, UX/design, technical design,
   and validation/roadmap documents as relevant; label draft, needs-validation or user-approved.
   Never invent research or generate empty exhaustive plans to fill a template.
4. Organize discussions by decision, not provider:
   `discussions/001-target/discussion.md` and `state.json`. Maintain `discussions/README.md`
   as a table of topic, status, recommendation and link. State files contain no machine paths
   or provider session IDs. Committed documents are the handoff between computers.

## Bridge usage

```text
python3 <skill>/scripts/peer.py --project <absolute-root> --topic docs/<initiative>/discussions/001-target init --title "Initial target"
python3 <skill>/scripts/peer.py --project <absolute-root> --topic docs/<initiative>/discussions/001-target call --provider codex --phase proposal --prompt-file <absolute-prompt-file>
```

Use `claude` when coordinating from Codex; `codex` when coordinating from Claude.
Keep prompt inputs in the project's ignored `work/planwith/` folder, not in global settings.
Each call is fresh: explicitly supply the current brief, evidence and relevant contributions.
Do not rely on hidden session memory. The bridge appends responses to the topic document;
append your own contributions there too. Never overwrite original contributions when summarizing.

Use phases `proposal`, `critique`, `revision`, `judge`, optionally `final`, then `verdict`.
Use `pause --question "..."` before requesting required user input. Yield to the user in the
host conversation. Use `answer --file <file-containing-actual-user-answer>` only after their
answer arrives. Record it verbatim and update the shared brief before the next call.
Use `finish --reason "..."` and record unresolved items when done or exhausted.
Use `status` to resume. Never delete state to evade limits or fabricate a user answer.

## Deliver

Put the judge scorecard and recommendation at the top of the topic document, with the full
contributions and user answers below. Update affected planning documents to the current
accepted position, linking back to the topic. Distinguish AI recommendation from user approval.
Report decisions, remaining questions and next validation steps in the host conversation.
No commits, pushes, messages to customers, or implementation are implied by planning alone.
