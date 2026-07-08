# Job Search Board

An automated job search system for Claude Cowork: it researches new job postings twice a
day, scores them for fit and legitimacy, tracks everything on a local dashboard, drafts a
tailored resume and cover letter the moment you mark a job "interested," and can even
fill out (but never submit) live application forms for you.

Everything here is a **template** — no one's personal data, job history, or contact
information is included. The setup guide below is written as Q&A so an AI agent (a fresh
Claude Cowork session, or another agent) can read this file and do the install itself.

---

## What's in this repo

```
Job Search Board/
├── README.md                          ← you are here
├── LICENSE                            ← MIT
├── JobSearch/
│   ├── README.md                      ← how the system works, once installed
│   ├── scripts/
│   │   ├── update_job.py              ← the only way jobs.json gets written to
│   │   └── build_board.py             ← rebuilds the dashboard from jobs.json
│   ├── artifact/template.html         ← the dashboard UI (Cowork artifact)
│   ├── data/jobs.example.json         ← schema reference — NOT real data
│   └── context/README.md              ← drop-folder for per-job context files
├── Profile/
│   ├── master-profile.template.md     ← your career facts (copy → master-profile.md)
│   ├── preferences.template.md        ← comp floor, roles, locations, rules
│   ├── github-projects.template.md    ← optional portfolio detail for technical roles
│   └── feedback-log.template.md       ← empty decision log
├── Applications/README.md             ← where tailored documents get filed (gitignored)
├── skills/resume-cover-letter-writer/SKILL.md   ← the drafting skill
└── scheduled-tasks/                   ← prompts for the 4 automated/on-demand tasks
    ├── job-search-morning.md
    ├── job-search-afternoon.md
    ├── job-board-refresh.md
    └── job-board-sync.md
```

---

## Setup Q&A (for the AI doing the install)

**Q: What does a user need before I start?**
A: A Cowork session with a connected folder for this project (any name — the guide below
calls it `{{PROJECT_ROOT}}`), and Python 3 + `pdftotext` (part of `poppler-utils`) available
in the sandbox shell. The `docx` skill (for building resume/cover-letter files) and
`WebSearch` should already be available in Cowork. A Google Drive connector is optional —
see the Drive Q&A below.

**Q: Where should this project live?**
A: Ask the user for (or create) a folder they want to use — e.g.
`~/Documents/job-search`. Connect it with `mcp__cowork__request_cowork_directory`, then copy
every file from this repo into it, preserving the folder structure above.

**Q: The scripts and scheduled-task prompts reference `{{PROJECT_ROOT}}` and
`{{SANDBOX_MOUNT}}` — what do I do with those?**
A: Find-and-replace them once you know the real paths:
- `{{PROJECT_ROOT}}` → the absolute host path Read/Write/Edit/Glob use for the connected
  folder (what the user sees in Finder/Explorer), e.g. `/Users/yourname/Documents/job-search`.
- `{{SANDBOX_MOUNT}}` → the path `mcp__workspace__bash` sees for that same folder — Cowork
  tells you this the moment you connect the folder (typically
  `/sessions/<session-id>/mnt/<folder-name>`).
- `{{SANDBOX_MOUNT_OUTPUTS}}` → your own scratch/outputs directory inside the sandbox (used
  as a staging area before handing a file to `mcp__cowork__update_artifact`).
Also update `RESUME_ROOT_HOST` near the top of `JobSearch/scripts/build_board.py` to the
same host path — it's used to build "open this file yourself" links on the dashboard.

**Q: What order should I do the install steps in?**
A:
1. Connect/create the project folder and copy this repo's contents into it.
2. Have the user (or ask them to) fill in `Profile/master-profile.template.md` and
   `Profile/preferences.template.md`, saving as `master-profile.md` and `preferences.md`
   (drop the `.template`). Ask them directly for anything you need — comp floor, target
   role families, location/remote rules, employment history, standing answers to
   education/work-authorization/self-ID questions — rather than guessing or inventing
   placeholder facts. `github-projects.template.md` is optional (useful for
   engineering-flavored roles with a portfolio to cite); skip it if not relevant.
3. Update the path placeholders (previous Q&A).
4. Make the `resume-cover-letter-writer` skill available — see the skill Q&A below.
5. Create the four scheduled tasks — see the scheduled-task Q&A below.
6. Build and publish the dashboard artifact — see the artifact Q&A below.
7. Do a first run: trigger `job-search-morning` once manually (or wait for its schedule),
   confirm it adds a few candidate jobs and rebuilds the dashboard, then walk the user
   through the dashboard once so they know what "Sync now" vs "Copy for chat" does.

**Q: How do I make the `resume-cover-letter-writer` skill available?**
A: Two options, either works:
- **Formal skill:** read `skills/resume-cover-letter-writer/SKILL.md` and register it as a
  custom skill (Cowork Settings → Capabilities → Skills, or the `skill-creator` skill if
  available) so it's invoked automatically whenever the user asks to apply somewhere.
- **Lightweight:** just leave the file in the project folder and note that any time a
  resume/cover letter needs drafting, you should read and follow
  `skills/resume-cover-letter-writer/SKILL.md` end to end. This works fine since
  `job-board-sync`'s auto-draft subagents already invoke it by name via the Skill tool — if
  that fails because it isn't a registered skill, have those subagents read the file
  directly instead.

**Q: How do I create the four scheduled tasks?**
A: For each file in `scheduled-tasks/`, call `mcp__scheduled-tasks__create_scheduled_task`
(load via ToolSearch first) with the file's content as the prompt, after resolving its path
placeholders. Suggested schedule (adjust to the user's timezone/preference):
| Task | File | Schedule |
|---|---|---|
| Morning research run | `job-search-morning.md` | daily, e.g. `0 5 * * *` (5:00 AM) |
| Afternoon research run | `job-search-afternoon.md` | daily, e.g. `0 14 * * *` (2:00 PM) |
| Board refresh | `job-board-refresh.md` | manual only (triggered from the dashboard's "Refresh board data" button) |
| Board sync | `job-board-sync.md` | manual only (triggered from the dashboard's "Sync now" button) |
Ask the user if they'd rather start with the daily research runs **disabled** until they've
reviewed a manual test run — enabling twice-daily automated research immediately is a
reasonable default, but let them decide.

**Q: How do I create the dashboard artifact?**
A:
1. Create `JobSearch/data/jobs.json` — start from `{"jobs": [], "daily_questions": [],
   "activity_log": [], "updated_at": null}` (an empty board; the schema in
   `jobs.example.json` shows what a populated entry looks like).
2. Run `python3 JobSearch/scripts/build_board.py` to produce `JobSearch/artifact/board.html`.
3. Call `mcp__cowork__create_artifact` with that HTML, give it whatever id/title you like
   (the scheduled-task files use "the board artifact's id" generically — pick one, e.g.
   `job-search-board`, and use that same id consistently everywhere `update_artifact` is
   called in the scheduled-task prompts you just created).
4. Note the artifact expects two scheduled task ids to exist for its buttons to work:
   whatever you named the research-run task (for "Run research now") and
   `job-board-refresh`'s id (for "Refresh board data"). If you used different ids than the
   defaults, update the two `trigger(...)` calls near the bottom of `template.html`.

**Q: Do I need Google Drive for this to work?**
A: No — it's optional. The dashboard's "Sync now" button uploads queued decisions to Google
Drive so `job-board-sync` can pick them up automatically; without it, the "Copy for chat"
button still works (it copies the same decisions as plain text for the user to paste into
chat, and you apply them manually). If the user does want live sync: find their Google
Drive connector's file-creation tool name (ToolSearch for "drive create file" or similar),
and replace `REPLACE_WITH_YOUR_DRIVE_CREATE_FILE_TOOL_NAME` near the top of the `<script>`
block in `template.html` with it. `job-board-sync.md`'s file-search step assumes the same
connector.

**Q: How do I keep the user's real data out of git?**
A: The included `.gitignore` already excludes `JobSearch/data/jobs.json`,
`JobSearch/data/jobs.backup.json`, everything under `JobSearch/context/` except its README,
everything under `Applications/` except its README, and the filled-in `Profile/*.md` files
(only the `.template.md` versions are tracked). Leave that as-is — don't commit real job
data, application PDFs, or a filled-in profile to a shared repo.

**Q: What are the rules I should never relax, even if the user asks casually?**
A: These are load-bearing for trust in an automation that acts on someone's behalf:
1. **Never click a final Submit/Apply/Finish/Send control on a job application, ever** —
   fill forms completely, then stop and hand off. This applies with zero exceptions inside
   the unattended auto-fill pipeline in `job-board-sync.md`, since no one is watching in
   real time to catch a mistake there.
2. **Never invent a fact** — every resume/cover-letter claim and every legitimacy signal
   must trace back to something in the profile files or something actually observed during
   research. Cap or omit anything unverifiable.
3. **Never resurface a job the user already passed on.**
4. Log decisions to `Profile/feedback-log.md` so the system's judgment improves over time
   instead of repeating the same corrections.

---

## License

MIT — see `LICENSE`. Free to use, fork, and adapt.
