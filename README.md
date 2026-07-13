# Job Search Board

An automated job search system for Claude Cowork: it researches new job postings twice a
day, scores them for fit and legitimacy, tracks everything on a local dashboard, drafts a
tailored resume and cover letter the moment you mark a job "interested," and can even
fill out (but never submit) live application forms for you.

Everything here is a **template** — no one's personal data, job history, or contact
information is included. You don't configure it by hand: you clone the repo, connect the
folder in a Claude Cowork session, and paste one prompt — Claude then asks you everything it
needs and sets the whole thing up. **Jump to [Get started in Claude Cowork](#get-started-in-claude-cowork)
below.** (The [Setup Q&A](#setup-qa-for-the-ai-doing-the-install) further down is the detailed
checklist that Claude follows during that install — you don't need to read it yourself.)

---

## Get started in Claude Cowork

Three steps: **clone → connect → paste the prompt**. The whole configuration is interactive —
Claude asks you for your comp floor, roles, history, schedule, and preferences, then wires up
the scripts, scheduled tasks, and dashboard for your instance.

### Step 1 — Clone this repo

Clone (or download the ZIP of) this repository into a folder you'll keep. That folder becomes
your project root, so there's nothing to copy anywhere afterward.

```bash
git clone https://github.com/jyelle111/Job-Search-Board.git ~/Documents/job-search
```

### Step 2 — Open a Cowork session and connect that folder

**On claude.ai (web):**
1. Go to **claude.ai** and sign in.
2. Open **Cowork** from the left sidebar.
3. Click **New** to start a session.
4. **Connect a folder** (the folder / 📎 connect control) and grant access to the folder from
   Step 1 (e.g. `~/Documents/job-search`).
5. Click into the message box.

**In the Claude desktop app (Mac / Windows):**
1. Open the **Claude** desktop app and sign in.
2. Open the **Cowork** tab.
3. Start a **New** session.
4. **Connect a folder** and grant access to the folder from Step 1 when prompted.
5. Click into the message box.

> If your Cowork build doesn't show a connect-folder button, skip step 4 — the prompt below
> tells Claude to connect the folder itself.

### Step 3 — Paste this prompt and send it

Copy the block below **verbatim** into the Cowork message box and send. Claude does the rest,
pausing to ask you each question it needs.

```text
Install the Job Search Board system for me in this connected folder.

Read README.md here — especially the "Setup Q&A (for the AI doing the install)" section —
and treat it as your install checklist. If this folder isn't connected as a Cowork
directory yet, connect it first.

Do the whole install yourself, and ask me for every piece of information you need instead of
guessing or inventing placeholders. At minimum, ask me for:
- my compensation floor, target roles / role families, locations, and remote rules, plus any
  hard "never apply" rules  → Profile/preferences.md
- my employment history, skills, education, and standing answers to common application
  questions (work authorization, notice period, etc.)  → Profile/master-profile.md
- whether I keep a portfolio or GitHub projects worth citing  → Profile/github-projects.md
  (optional — skip if not relevant)
- my timezone and what times the two daily research runs should fire (default 5:00 AM and
  2:00 PM), and whether to start them enabled or disabled until I've reviewed a test run
- whether I want live Google Drive sync for board decisions (optional)

Then configure everything end to end: replace the {{PROJECT_ROOT}}, {{SANDBOX_MOUNT}}, and
{{SANDBOX_MOUNT_OUTPUTS}} placeholders and RESUME_ROOT_HOST, save my filled-in Profile/*.md
files, register the resume-cover-letter-writer skill, create the four scheduled tasks, and
build and publish the dashboard artifact.

Finally, do one test morning research run, show me the dashboard, walk me through the
"Sync now", "Copy for chat", and "Talk about this" buttons, and tell me exactly what you did
and anything I still need to do myself.

Hard rules, no exceptions: never submit a job application, never invent a fact about me, and
never resurface a job I've already passed on.
```

That's it. Claude works through the checklist, confirms each piece as it goes, and hands you a
live dashboard plus two scheduled research runs. Answer its questions as they come.

> **Want to see the dashboard before installing anything?** Open
> `JobSearch/artifact/board.sample.html` in any browser — it's a fully built preview with two
> fictional jobs. The buttons are inert in a plain file; they come alive once the real artifact
> is published during install.

---

## Update an existing install

Already running the board and want the latest features (new dashboard tabs, script fixes,
etc.)? **Your personal data is safe:** `JobSearch/data/jobs.json`, your `Profile/*.md`, your
`Applications/`, and the built `board.html` are all git-ignored, so pulling updates never
touches them — only the shared system files (dashboard template, scripts, skill, task prompts)
move forward.

Open a Cowork session on the **same project folder** you installed into, then copy this block
**verbatim** into the message box and send. Claude does the diff, merge, rebuild, and re-publish
for you, preserving both your data and your local config.

```text
Update my installed Job Search Board to the latest version from the upstream repo, without touching any of my personal data.

Work carefully, from the project root:

1. Protect my work first. Commit my current local state so nothing can be lost:
   `git add -A && git commit -m "local config before update"`.
   (My real data — jobs.json, Profile/*.md, Applications/ — is git-ignored, so this only
   snapshots the config edits I made at install.) If this folder is NOT a git clone (I
   downloaded a ZIP), stop and tell me — then instead fetch the latest tracked files from
   https://github.com/jyelle111/Job-Search-Board and copy them in OVER the old ones, but never
   over jobs.json, Profile/*.md, feedback-log.md, or anything under Applications/.

2. Show me what's changing before applying it:
   `git fetch origin`, then `git log --oneline HEAD..origin/main` and
   `git diff --stat HEAD origin/main`. Summarize the notable changes for me.

3. Merge the update: `git pull --no-edit origin main`. Any merge conflicts will be in the files
   I customized during install — resolve them by KEEPING MY local values and TAKING the upstream
   feature code. After merging, re-check and re-apply if any got reverted:
   - the Google Drive tool name where `DRIVE_CREATE` is set near the top of the <script> block
     in JobSearch/artifact/template.html (must not fall back to the REPLACE_WITH… placeholder),
   - my scheduled-task ids in the artifact's action calls in that same template — the three
     `trigger(...)` calls near the bottom (Find new roles → `job-search-morning`, Refresh →
     `job-board-refresh`, Draft now → `job-board-sync`) AND the `runScheduledTask("job-board-sync")`
     call inside `syncNow()` (the Sync now button, which applies every queued decision). If I used
     the default ids these need no change; if I renamed a task, keep my id.
   - `RESUME_ROOT_HOST` at the top of JobSearch/scripts/build_board.py.

4. If any files under scheduled-tasks/ or skills/ changed in this update, update the matching
   scheduled tasks / skill to match (re-resolving the {{PROJECT_ROOT}}, {{SANDBOX_MOUNT}}, and
   {{SANDBOX_MOUNT_OUTPUTS}} placeholders) so the automation matches the new prompts.

5. Rebuild the dashboard from MY data (not the sample):
   `python3 JobSearch/scripts/build_board.py` — this reads my real jobs.json and writes
   JobSearch/artifact/board.html.

6. Re-publish to the SAME artifact I already have (keep my existing link): call
   mcp__cowork__update_artifact with that rebuilt board.html and my current board artifact id.
   Do NOT create a new artifact.

7. Reload the dashboard, confirm the new features are live, and tell me exactly what changed,
   what config you preserved, and anything I still need to do myself.

Never modify or delete my jobs.json, jobs.backup.json, Profile/*.md, feedback-log.md, or
anything under Applications/. If anything is ambiguous, ask me before proceeding.
```

Your data stays put; only the board UI and system scripts advance to the latest version.

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
│   ├── artifact/template.html         ← the dashboard UI (Cowork artifact) — unbuilt template
│   ├── artifact/board.sample.html     ← ready-to-open PREVIEW, pre-built with sample data
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

**Q: Can I see what the dashboard looks like before installing anything?**
A: Yes — `JobSearch/artifact/board.sample.html` is a fully pre-built version of the
dashboard with two fictional jobs already in it (same data as `jobs.example.json`). Open it
directly in a browser to see the UI: pipeline stage chips up top, and each expanded job card
splits into section tabs — **Role** (description + keywords), **Fit** (fit/gap + legitimacy),
**Comp**, **Documents**, and **Interviews** — plus the fit meter, document previews, and
interview tracking. Note it's a static file at that point — the "Sync now,"
"Refresh board data," and "Run research now" buttons need `window.cowork` (only present
inside an actual Cowork artifact) and the scheduled tasks to exist, so those won't do
anything when opened as a plain file. `template.html` (the unbuilt version with the
`__JOBBOARD_DATA__` placeholder still in it) is what actually gets published as the
artifact — see the artifact Q&A below for how to build and publish the real, empty-start
version once installed.

**Q: What does a user need before I start?**
A: A Cowork session with a connected folder for this project (any name — the guide below
calls it `{{PROJECT_ROOT}}`), and Python 3 + `pdftotext` (part of `poppler-utils`) available
in the sandbox shell. The `docx` skill (for building resume/cover-letter files) and
`WebSearch` should already be available in Cowork. A Google Drive connector is optional —
see the Drive Q&A below.

**Q: Where should this project live?**
A: The user has cloned this repo into a folder they'll keep (e.g. `~/Documents/job-search`),
and that cloned folder IS the project root — it already contains the structure above, so
there's nothing to copy. Just connect it with `mcp__cowork__request_cowork_directory` if it
isn't connected already. (If instead the user handed you the files loose rather than a clone,
create/pick a folder, connect it, and copy every file in preserving that structure.)

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
1. Connect the cloned project folder (it already contains this repo's contents — see the
   "Where should this project live?" Q&A). Only copy files in if the user handed them to you
   loose instead of as a clone.
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
| Board refresh | `job-board-refresh.md` | manual only (triggered from the dashboard's "Refresh" button) |
| Board sync | `job-board-sync.md` | manual only (triggered from the dashboard's "Sync now" and "Draft now" buttons) |
| Morning run (also on-demand) | — | the dashboard's "Find new roles" button also triggers `job-search-morning` |
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
4. Wire the artifact's action buttons. Each one calls a scheduled task **by its exact id**, so
   those ids must match the tasks you created in the previous Q&A. With the default ids (which
   match the `scheduled-tasks/` filenames) it all works with no edit; if you named any task
   differently, update the matching call in `template.html` — there are **four** call sites
   across **three** task ids:
   - **Find new roles** (top bar) → `trigger("job-search-morning", …)`
   - **Refresh** (top bar) → `trigger("job-board-refresh", …)`
   - **Draft now** (shown on an undrafted role's Documents tab) → `trigger("job-board-sync", …)`
   - **Sync now** (the queued-decisions bar) → `runScheduledTask("job-board-sync", …)`, inside
     the `syncNow()` function. This is the important one: it applies **every** queued board
     decision — interested/pass/"they passed", **manual status changes and "Restore to review"
     from the archive**, notes, and interview rounds. The three `trigger(...)` calls sit near
     the bottom of the `<script>`; the Sync now call is in `syncNow()` just above them.

   The in-card decision buttons themselves (Interested, Pass, They passed, Change status,
   Restore, Add note, Add round…) need no per-button wiring — they queue to the browser and are
   all applied by that one Sync now → `job-board-sync` path (or the "Copy for chat" fallback).
   Also set `DRIVE_CREATE` (see the Drive Q&A) if you want one-click Sync now.

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
