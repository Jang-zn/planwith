# Planning rounds, not debate exchanges

Use `<base>/round-001/`, `round-002/`, etc. The base defaults to the captured host CWD's docs.
A user-specified output directory replaces the BASE; append the numbered round folder there.
If the user names an existing numbered round explicitly, resume it when active rather than nesting
another round folder. Closed rounds remain historical unless the user explicitly requests a correction.

Commands (use py -3 on Windows):

```text
python3 <skill>/scripts/rounds.py --project <host-cwd> new --reason "Initial idea clarification"
python3 <skill>/scripts/rounds.py --project <host-cwd> resume
python3 <skill>/scripts/rounds.py --project <host-cwd> close
python3 <skill>/scripts/rounds.py --project <host-cwd> new --reason "User feedback: narrow the initial target"
```

Optional `--output <relative-base>` honors the user's destination. Helper returns the current
absolute round path. Use its project-relative topic path for peer.py. The helper only manages
round metadata and `planwith-rounds.md`; the coordinator writes substantive documents.
Run `status` after creating report/README so index links refresh. Resolve paths locally on each PC.

- First request: clarify idea and constraints, create round-001, run bounded topic workflow.
- User answers a pending question, asks for clarification or resumes unfinished work: SAME round.
  Do not close while essential user input is pending. Topic budgets remain unchanged.
- After completing planned work/report: close the round. Unresolved issues may remain but must
  be explicit in the report. Closing is not user approval or proof of feasibility.
- User requests the next iteration or materially revises a completed plan: read previous result,
  clarify new input, create next round. Ask only if same-round revision versus new iteration is unclear.
- Never create endless rounds, restart exhausted budgets automatically, or reopen prior topics
  silently. A new planning round has fresh state ONLY because the user requested a new iteration.

Before a new round, read predecessor brief, decisions, open questions, discussion summaries and
report. Write the new brief with inherited constraints and new user input. Write changes.md with
prior decision → revised decision → reason/evidence → source topic links. Copy only relevant current
planning text into new documents; do not copy old state.json, round.json, transcripts or HTML wholesale.
Link to old discussions; mark carried-forward scores with their original round and date. Reevaluate
only changed topics. Include unchanged conclusions in the current report so it stands alone.

Old folders are preserved by workflow, not filesystem immutability. The round helper refuses an
additional active round; do not bypass this with manual mkdir. Existing unversioned docs are legacy
references: leave them intact and link from the first round; no automatic destructive migration.
User-authorized historical corrections must leave an explicit correction note. No automatic Git
commit or push is implied by a planning round.
