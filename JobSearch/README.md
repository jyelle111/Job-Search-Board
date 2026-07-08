# Job Search System — How It Works

## Pieces
- `data/jobs.json` — single source of truth for every job ever seen (all statuses).
  Passed/skipped jobs stay here forever so they never resurface. **Not tracked in git** —
  this is your personal data (see `../.gitignore`); `data/jobs.example.json` shows the schema.
- `data/jobs.backup.json` — auto backup of the previous version, written on every update.
- `scripts/update_job.py` — the ONLY way to write to jobs.json (atomic, validated). Also
  handles interview-round records (`--add-interview`, `--interview-set`, `--interview-note`).
- `scripts/build_board.py` — rebuilds the board artifact from jobs.json + `artifact/template.html`.
  Also extracts a read-only text preview of each job's Resume.pdf/Cover Letter.pdf (via
  `pdftotext`) and embeds it in the board snapshot, since an artifact sandbox can't open
  local files as links — this is how the dashboard lets you "read" a drafted document
  without leaving the board. **Edit `RESUME_ROOT_HOST` at the top of this script to your
  own absolute path before first use.**
- `../Profile/` — your career facts (`master-profile.md`), search preferences/floors/rules
  (`preferences.md`), optional portfolio detail (`github-projects.md`), and a running
  decision log (`feedback-log.md`). Copy the `.template.md` versions and fill them in.
- `../Applications/<Company> - <Role>/` — tailored resume + cover letter per application
  (the real files — the board only shows a preview + the path).
- **Job Board artifact** — the UI, created via `mcp__cowork__create_artifact`. It's a
  SNAPSHOT: data is embedded at build time by `scripts/build_board.py` merging
  `data/jobs.json` into `artifact/template.html`. Interested/Pass clicks, question answers,
  interview rounds, and interview notes all queue in the board (browser localStorage) and
  sync via the "Sync now"/"Copy for chat" bar.
- **Scheduled tasks** (see `../scheduled-tasks/`) — two research runs per day (research new
  jobs, add matches, rebuild the board), plus two on-demand tasks wired to the board's
  buttons: `job-board-refresh` (rebuild only) and `job-board-sync` (apply queued decisions,
  auto-draft documents, auto-generate interview prep, auto-fill live applications).

## Job statuses
`new` → (you mark interested) → `interested` → `plan_pending` → `drafts_ready` →
`approved_to_submit` → `applied` → `interviewing` → `offer`
Any point: `passed` (not interested), `skipped` (not now), `expired` (posting gone),
`rejected` (interview process ended without an offer).

## Auto-draft on "interested"
Marking a job "I'm interested" on the board and hitting Sync now does more than change its
status: `job-board-sync` checks whether the job already has `documents_path` set, and if
not, launches a dedicated subagent that reads the job record, runs the full
`resume-cover-letter-writer` skill (profile read, drafting, docx build, PDF conversion,
self-audit, filing under `Applications/<Company> - <Role>/`), and marks the job
`drafts_ready`. No extra approval gate before drafting starts — but nothing is ever
submitted without your explicit go-ahead.

## Interview tracking
Once a job is `applied`, add interview rounds from the board's "Interviews" section (round
name, date, format, interviewer). Adding a round:
- Moves the job to `interviewing` (never downgrades a job already at `offer`/`rejected`).
- Queues an `interview_add` decision; on the next Sync, `job-board-sync` creates the round
  record AND launches a subagent to research the company/round and write back
  `study_notes`, `best_practices`, and `recommended_questions` for that specific round.
- You can add running notes to any round from the board (before or after the interview) —
  these sync the same way as job notes.
- **"Talk about this"** (on every job row) copies the full job + interview context — JD
  summary, comp, fit/gaps, notes, interview prep, your own notes — to your clipboard, since
  a static dashboard can't open a live chat turn on its own; paste it into a new chat
  message to talk it through with full context.

## Check-in workflow (say "job check-in" in chat, or your own phrasing)
1. Claude reads jobs.json, summarizes: new matches, status of applied jobs, pending
   approvals, in-progress drafts, upcoming interview rounds.
2. You approve/pass on new matches (chat or board buttons).
3. Marking a job interested auto-drafts documents (see above) — review the draft preview on
   the board, then tell Claude in chat when it's approved to submit; submission always
   happens via your own browser, with your explicit approval, and Claude asking about any
   unknown form fields.
4. Claude asks up to 3 profile-gap questions and logs answers to `feedback-log.md`.

## Hard rules
- Nothing is ever submitted without your explicit approval of the final documents. Drafting
  itself is automatic (see above) — submission is not, ever, even inside the fully
  unattended auto-fill pipeline (see `job-board-sync`).
- Comp floors, location rules, and role families live in `Profile/preferences.md` — that's
  the one file to edit to retune matching.
- All decisions get logged to `Profile/feedback-log.md`.
- **Legitimacy scoring**: every match carries `legit_score` (0–100, 100 = certainly real)
  with `legit_evidence` and `legit_flags`. Evidence-based only — signals must be actually
  observed (posting fetched, ATS verified, company confirmed), never invented. Unverifiable
  posts cap at 50; below 30 aren't added at all. The board shows a ⚠ FAKE RISK chip under 55.
- Fit scoring should weigh real systems/impact from your background (see
  `Profile/github-projects.md` if you keep one), not just keyword matching against the JD.
