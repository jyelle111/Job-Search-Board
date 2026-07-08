---
name: job-board-sync
description: On-demand — apply queued job-board decisions, auto-draft resume/cover letter for newly-interested jobs, auto-generate interview prep for newly-scheduled rounds, auto-fill live applications (via subagents), then rebuild the board.
---

Apply the user's queued job-board decisions, then run any follow-on drafting work those
decisions trigger. Before first use, replace every `{{PROJECT_ROOT}}` and
`{{SANDBOX_MOUNT}}`/`{{SANDBOX_MOUNT_OUTPUTS}}` placeholder below with your real paths (see
`job-search-morning.md`'s intro), and replace the Google Drive connector tool name in Step 1
with whatever you configured in `template.html` (see the top-level README's Drive Q&A) — or
skip Steps 1-2 entirely if you're only using the "Copy for chat" fallback, not live Drive sync.

Steps:

1. Find the newest sync file: call your Google Drive connector's file-search tool with a
   query like "title contains 'jobsearch-sync-queue-'" (pageSize 10). Pick the file with the
   newest createdTime. If none exist from the last 3 days, skip straight to step 4 (there
   may still be sweep/drafting work to do even with no new decisions) instead of stopping.
2. If a sync file was found: download it, base64-decode the content, parse the JSON:
   `{created_at, decisions:[...]}`. Each decision has a "kind" of one of: "job" {id, status,
   reason?}, "note" {id, note}, "answer" {id, answer}, "interview_add" {id, interview_id,
   round, date, format, interviewers}, "interview_note" {id, interview_id, note}. ("id" is
   always the job id.)
3. Apply each decision via `mcp__workspace__bash` (glob path works regardless of session
   name). For text containing single quotes or other shell-hostile characters, write it to
   `/tmp/arg.txt` and pass `"$(cat /tmp/arg.txt)"`.
   - kind "job": `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py '<id>'
     '<status>' '<reason or empty string>'`. If status is "applied", also run:
     `python3 .../update_job.py --set '<id>' '{"date_applied":"<today YYYY-MM-DD>"}'` (only
     if the job has no `date_applied` yet — check jobs.json first).
   - kind "note": `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py --note '<id>'
     '<note text>'`. Long notes (pasted transcripts) are fine.
   - kind "answer": `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py --answer
     '<id>' '<answer>'`
   - kind "interview_add": `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py
     --add-interview '<id>' '<json: {"id":"<interview_id>","round":"<round>","date":"<date>","format":"<format>","interviewers":"<interviewers>"}>'`.
   - kind "interview_note": `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py
     --interview-note '<id>' '<interview_id>' '<note text>'`
   Output `OK` = applied. `NOT_FOUND` = skip and note. `DUPLICATE_ID` on `--add-interview`
   means it was already added (e.g. a re-sync) — harmless, skip. Re-applying an identical
   status is harmless.

4. **Sweep for missing documents** (this is the self-healing step — run it EVERY time,
   regardless of whether steps 1-3 found anything, because a job can end up "interested"
   with no draft for reasons other than a fresh decision this run: a manual status edit in
   chat, an older job marked interested before this automation existed, or a previous run's
   subagent failing partway). Read jobs.json and build the list of every job whose status is
   "interested" AND whose `documents_path` is empty/missing. For each one, launch ONE
   subagent (Agent tool, subagent_type "general-purpose", description like "Draft
   resume/cover letter for <Company>") — sequentially, waiting for each to finish before
   starting the next, to avoid two subagents writing into jobs.json or scanning the
   Applications folder at the same time. This isolation is deliberate: it keeps the (long,
   detail-heavy) drafting work out of this task's own context. Give each subagent this
   fully self-contained prompt, filling in the bracketed values from jobs.json and
   resolving `{{PROJECT_ROOT}}` to the real path:

   "You are drafting a tailored resume and cover letter for a job application, id
   [JOB_ID]. Read `{{PROJECT_ROOT}}/JobSearch/data/jobs.json` (Read tool, host path) and
   find the job record with this id for the full JD summary, fit_reasons, gaps, keywords,
   and comp fields. Then invoke the resume-cover-letter-writer skill (Skill tool, or read
   `{{PROJECT_ROOT}}/skills/resume-cover-letter-writer/SKILL.md` directly if it isn't
   registered as a formal skill) and follow it completely end to end: read the profile
   source-of-truth files fresh, pick the positioning angle, draft and tailor the resume and
   cover letter, build with the docx skill, validate, convert to PDF, render a page image
   and actually look at it, self-audit every factual claim against
   master-profile.md/github-projects.md, and file both PDFs under
   `{{PROJECT_ROOT}}/Applications/<Company> - <Role>/` using a clean human-readable company
   name. Verify the files landed using Glob on the host path (not just the bash exit code)
   before proceeding. Then run, via `mcp__workspace__bash`:
   `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py --set '[JOB_ID]'
   '{\"documents_path\":\"Applications/<Company> - <Role>/\"}'` (use the exact folder name
   you actually created) and `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py
   '[JOB_ID]' 'drafts_ready' 'Auto-drafted by job-board-sync'`. This is a background
   automation run — the user is not present. Never submit the application, never open a
   browser, never contact anyone; drafting and filing the documents is the entire scope.
   Report back the exact folder path and a one-line confirmation."

   Count how many drafting subagents you launched and how many completed successfully for
   the final report.

5. **Sweep for drafts_ready jobs needing a live application fill** (this is the auto-fill
   pipeline — run it EVERY time). Read jobs.json and build the list of every job whose
   status is "drafts_ready" AND whose `apply_fill_status` field is absent/missing (this
   makes each job get exactly one attempt; once `apply_fill_status` is set to anything,
   never re-attempt it automatically — that's a terminal state until the user clears the
   field or acts on it). For each one, launch ONE subagent (Agent tool, subagent_type
   "general-purpose", description like "Auto-fill application for <Company>") —
   sequentially, waiting for each to finish before starting the next, so two subagents
   never drive a browser at the same time. Give each subagent this fully self-contained
   prompt, filling in the bracketed values from jobs.json:

   "You are filling out a live job application form on the user's behalf, in the
   background, with the user NOT present to supervise in real time. This makes the safety
   rules below non-negotiable — there is no one watching to catch a mistake.

   Read `{{PROJECT_ROOT}}/JobSearch/data/jobs.json` (Read tool, host path) and find the job
   record with id [JOB_ID] for its url, company, title, jd_summary, fit_reasons, gaps,
   keywords, and documents_path (folder containing Resume.pdf and Cover Letter.pdf). Also
   read `{{PROJECT_ROOT}}/Profile/master-profile.md` (host path) for the candidate's full
   employment history, contact info, and standing application policies, and
   `{{PROJECT_ROOT}}/Profile/github-projects.md` for project talking points if the form has
   open-ended questions.

   Load the Chrome MCP tools (ToolSearch query
   'select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__form_input,mcp__claude-in-chrome__file_upload,mcp__claude-in-chrome__browser_batch,mcp__claude-in-chrome__tabs_create_mcp').
   Open a new tab and navigate to the job's url.

   HARD STOP CONDITIONS — check for these before typing anything, and re-check at every step:
   - If the site requires creating an account, signing up, or logging in before you can
     access or fill any application fields, STOP immediately. Do not create an account. Do
     not enter a password anywhere, ever, even into a 'create password' field. Do not enter
     the candidate's email into a signup form that would trigger account creation. Set
     `apply_fill_status` via the command below to 'blocked_login_required' with a note
     describing exactly where it stopped, and end your turn — do not attempt any workaround.
   - If a CAPTCHA or bot-detection challenge appears, stop, set `apply_fill_status` to
     'blocked_captcha', and end your turn.
   - If the job posting is expired, removed, or 404s, set `apply_fill_status` to
     'blocked_expired' and end your turn.
   - If anything is genuinely ambiguous or you are not confident filling a field correctly
     (e.g. a required field with no truthful answer available), leave that field and note
     it — do not guess or fabricate.

   If none of the above apply, fill out the entire application form:
   - Upload Resume.pdf and Cover Letter.pdf from the documents_path folder to any
     resume/cover-letter upload fields (file_upload tool).
   - Personal info: use exactly the contact line printed at the top of
     master-profile.md (name, email, phone, address/city — whatever it actually contains)
     — do not use any other values, and do not invent a preferred name if none is given.
   - Employment history — IMPORTANT, use discretion, do not dump the full history by
     default: first extract the text of documents_path/Resume.pdf (via `pdftotext -layout`
     over `mcp__workspace__bash`, using the host-path-to-sandbox-path mapping, or by reading
     it if a text layer is available) and identify exactly which employers/roles/dates
     appear on THAT tailored resume — the resume-cover-letter-writer skill already made a
     deliberate editorial choice about which roles to feature for this specific job, and the
     online application should tell the same story, not a longer one. Enter ONLY those
     entries into the application's work-history section, in the same reverse-chronological
     order and with the same title/company/dates/date-ranges printed on the resume. Do NOT
     default to the full employment history in master-profile.md — that full list exists as
     ground truth for verifying facts, not as a checklist of entries to always transcribe.
     (Exception: if the specific ATS form explicitly requires 'complete work history going
     back N years' as a hard compliance requirement — e.g. background-check or
     government-contractor language — then use the full history from master-profile.md
     instead, and note this in apply_fill_notes.) For employer fields that are search
     comboboxes: try searching the real name first; if 'No results found', search 'Other'
     and use the resulting free-text field for the real employer name. For native
     month/year date inputs, prefer calling form_input with value in 'YYYY-MM' format (e.g.
     '2024-01') — this is more reliable than click-and-type. Always re-verify a dropdown's
     actual selected value with find() after setting it rather than trusting a screenshot,
     since screenshots can be stale mid-form.
   - Standing policies from master-profile.md (apply on every application, no exceptions):
     follow whatever the "Standing application policies" section says about education
     disclosure, work authorization, and voluntary self-identification questions
     (gender/race/ethnicity/disability/veteran status) exactly — select the stated 'decline
     / prefer not to answer' option where one exists. If a field is a forced binary with no
     decline option (e.g. a plain Yes/No 'Are you Hispanic or Latino?' dropdown), do NOT
     guess or pick an answer on the user's behalf — leave that specific field
     unanswered/on its default and clearly flag it by name in apply_fill_notes so the user
     corrects it during their own review, rather than silently guessing.
   - Open-ended screening questions: answer truthfully and specifically, grounded only in
     real facts from jd_summary, fit_reasons, gaps, keywords, master-profile.md, and
     github-projects.md. Never fabricate an employer, title, date, metric, or skill. If
     there's a genuine gap (e.g. no healthcare domain experience), say so honestly rather
     than glossing over it — see the gaps field for what to disclose.

   NEVER-SUBMIT RULE (the single most important rule): never click any button whose label
   is or contains 'Submit', 'Apply', 'Finish', 'Complete Application', 'Send Application',
   or similar finalizing language — no matter how confident you are, no matter what step of
   a multi-step form you're on. Stop one step before that button every time. Multi-step
   'Save and Continue' buttons that just advance to the NEXT section of the same
   in-progress application (not a final review/submit page) are fine to click, since the
   form isn't finished yet — but if you are ever unsure whether a button is a final submit
   or just an intermediate 'next', treat it as final and stop. Never press Enter/Return
   while focus is inside a form field — on some sites this silently triggers a submit
   action; use Tab or click elsewhere to move between fields instead. Before every click
   anywhere near a submit-like button, take a brand-new screenshot immediately beforehand
   (never reuse an older screenshot's coordinates) and prefer find()-based element refs over
   raw coordinates in that zone. Also re-screenshot immediately before any click after
   adding a new repeating entry (e.g. a new work-experience block) or toggling a checkbox —
   sticky footers and layout shifts silently cause clicks to land on the wrong element or
   miss entirely; verify each field's value immediately after setting it rather than
   trusting the action's own success message. If a form field's value doesn't seem to
   update correctly (e.g. it appears to concatenate old and new text, or a stale value keeps
   reappearing), it's likely a React-controlled input that ignores plain keyboard/paste
   events — use the form_input tool (which sets the value through the framework's real
   input path) rather than repeated raw typing/deleting.

   When you reach the natural stopping point (either the last fillable step before a final
   review/submit screen, or the review/submit screen itself with everything filled in and
   nothing clicked), take a final screenshot to confirm the form is filled and no submission
   occurred, then run via `mcp__workspace__bash`:
   `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py --set '[JOB_ID]'
   '{\"apply_fill_status\":\"filled_pending_submit\",\"apply_fill_notes\":\"<one line: what
   was filled, which tab/browser it's left open in, anything the user should double
   check>\"}'`. Do not change the job's status field — it stays 'drafts_ready' until the
   user submits and updates it themselves. Leave the browser tab open; do not close it.

   This is a background automation run. The user is not present to answer questions or
   approve anything mid-task. Never contact anyone, never accept a CAPTCHA, never enter
   payment info, never create an account, never enter a password, and never click a final
   submit control under any circumstances. Report back a one-line summary of what happened."

   Count how many auto-fill subagents you launched, how many reached
   `filled_pending_submit`, and how many were blocked (with reasons) for the final report.

6. **Sweep for interview rounds missing prep.** Read jobs.json again and find every
   interview round (across all jobs' "interviews" arrays) whose `prep.study_notes`,
   `prep.best_practices`, AND `prep.recommended_questions` are all empty. For each one,
   launch ONE subagent per round (Agent tool, subagent_type "general-purpose", description
   like "Interview prep for <Company> <round>"), sequentially, with this self-contained
   prompt:

   "Prepare the user for a job interview. Read `{{PROJECT_ROOT}}/JobSearch/data/jobs.json`
   (Read tool) and find job id [JOB_ID] for company, title, and jd_summary, and within its
   \"interviews\" array find the round with id [INTERVIEW_ID] for its round name, format,
   date, and interviewers. Also read `{{PROJECT_ROOT}}/Profile/master-profile.md` and
   `github-projects.md` (Read tool) for the candidate's background to match against.
   Research the company and role with WebSearch (load via ToolSearch first if needed) —
   recent news, product focus, culture/interview-process signals, and the named
   interviewer's public background if one is given. Produce three blocks, each well under
   150 words and written as dense, skimmable notes (not prose paragraphs): study_notes
   (concrete things to review before this specific round), best_practices (how to perform
   well in THIS round's format specifically — a phone screen, onsite, and take-home call for
   different tactics), recommended_questions (2-4 sharp questions the user should ask that
   are specific to this company/round, not generic filler). Then write a JSON object to
   `/tmp/prep_[INTERVIEW_ID].json` with structure
   `{\"prep\":{\"study_notes\":\"...\",\"best_practices\":\"...\",\"recommended_questions\":\"...\"}}`
   and run: `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/update_job.py --interview-set
   '[JOB_ID]' '[INTERVIEW_ID]' \"$(cat /tmp/prep_[INTERVIEW_ID].json)\"`. This is a
   background automation run — the user is not present. Never contact anyone or submit
   anything; research and note-writing only."

   Count how many prep subagents you launched and completed for the final report.

7. For every "passed" decision with a reason (from step 3, if any ran), append one bullet to
   `{{PROJECT_ROOT}}/Profile/feedback-log.md` under a "## <today> — Board sync" heading
   (newest-first, after the intro lines): "- Passed <job title or id>: <reason>". Use the
   Edit tool on the host path; fall back to bash on
   `{{SANDBOX_MOUNT}}/Profile/feedback-log.md`.
8. Rebuild the board: `mcp__workspace__bash`:
   `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/build_board.py /tmp/board.html && cp
   /tmp/board.html {{SANDBOX_MOUNT_OUTPUTS}}/board.html` — then call
   `mcp__cowork__update_artifact` with the board artifact's id, `html_path` of the copied
   file, and an `update_summary` summarizing what changed this run. (`build_board.py` also
   extracts resume/cover-letter text previews automatically — no extra step needed.)
9. Do not modify any other files beyond what's described above. Never submit applications.
   Never contact recruiters or interviewers on the user's behalf.

Final output: "Synced N decisions (X applied, Y skipped), swept M missing drafts (Z
completed), F drafts_ready jobs for auto-fill (G filled_pending_submit, H blocked), P
missing interview preps (Q completed): <one line summary>". If there was nothing to sync
AND nothing to sweep, just say so briefly.
