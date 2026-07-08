---
name: resume-cover-letter-writer
description: "Write and tailor a resume and cover letter for a specific job application. Optimizes for ATS parsing and keyword match against the job description while staying strictly truthful to the candidate's master career profile (no invented employers, dates, titles, metrics, or skills). Use this skill any time the user is applying to a job, pastes a job posting or JD, asks for a tailored resume/cover letter, says 'apply for this role', or is filling out a job application — even if they don't explicitly say 'resume' or 'cover letter'. Pairs with the docx skill for document mechanics and with the JobSearch system (jobs.json) for tracking."
---

# Resume & Cover Letter Writer

Two goals in tension, both non-negotiable: maximize the odds of landing an interview, and
never state anything that isn't true. This skill exists because those two goals actually
reinforce each other — recruiters and hiring managers cross-check LinkedIn, ask follow-up
questions in interviews, and a fabricated line that unravels kills the offer faster than an
honest gap ever would. Optimize *framing, emphasis, and keyword matching* hard. Never
optimize *facts*.

Before first use, replace `{{PROJECT_ROOT}}` below with the actual path to this project on
the user's computer (see the top-level README's setup Q&A).

## 0. Always read the source of truth fresh

Before writing anything, read these files — don't rely on memory from a previous session,
since the profile gets updated over time (new employment facts, standing policies, answered
screening questions):

- `{{PROJECT_ROOT}}/Profile/master-profile.md` — contact info, employment history,
  positioning angles, skills, signature proof points, standing application policies
  (education, work auth, disability questions)
- `{{PROJECT_ROOT}}/Profile/github-projects.md` — deep detail on technical projects, if the
  user maintains one; useful for engineer-facing roles
- `{{PROJECT_ROOT}}/Profile/feedback-log.md` — past decisions and *why*, including comp
  figures already stated to specific companies (see Step 5)
- `{{PROJECT_ROOT}}/Profile/preferences.md` — comp floor, location/remote preferences, what
  counts as a fit

If any fact you need isn't in these files, don't invent it — ask the user, or leave it out.

## 1. Read the job description like a matching algorithm would

Pull out, explicitly:
- **Required/must-have skills and years of experience** — the things that gate a resume
  out of the pile
- **Exact phrasing** the JD uses for skills and technologies (e.g. "Retrieval-Augmented
  Generation (RAG)" vs "RAG" vs "retrieval augmented generation") — ATS keyword matching
  and human skimming both reward mirroring the JD's own words, but only for things the user
  actually has
- **Seniority/framing signals** — is this "ships production code" or "designs strategy"? A
  build role or a leadership role?
- **Culture/values language** — words like "ambiguity," "ownership," "startup pace,"
  "fundamentals" that signal what kind of story will resonate
- **Nice-to-haves** — lower priority for keyword matching, but useful for cover letter color

## 2. Pick the positioning angle

The user's master profile defines a handful of proven angles (see
`master-profile.md`'s "Positioning" section). Pick whichever has the highest genuine
overlap with the JD's requirements and framing — don't force-fit. If a role sits between
two angles, blend the summary and bullet emphasis rather than reusing a previous variant
verbatim. Check `{{PROJECT_ROOT}}/Applications/*/Resume.pdf` for existing variants first —
reuse and adapt rather than starting from zero, but always re-tailor the summary line and
bullet ordering to this specific JD.

## 3. Draft the resume

**Structure (single column, ATS-safe):**
1. Contact line: city/state, email, LinkedIn, phone — centered, small
2. Name — large, bold
3. Title line — tailored to the target role's positioning angle, not necessarily the exact
   job title
4. 3–5 sentence summary — lead with years of experience and the positioning angle, end with
   a sentence naming the target company and what the user wants to help them do (pull this
   from the JD's own framing of the problem)
5. EMPLOYMENT HISTORY — reverse chronological, title + company/location + dates
   (right-aligned via tab stop), 2–4 bullets per role
6. SKILLS — comma-separated, canonical skills list filtered/reordered to prioritize what
   this JD asks for first
7. LINKS — portfolio/personal site, if the user has one

**Bullet-writing rule:** each bullet should be traceable to a specific fact in
`master-profile.md` or `github-projects.md`. Lead each bullet with the outcome or the proof
point most relevant to *this* JD's stated needs, then the supporting detail. Reuse the
user's canonical signature proof points — pick the ones that map to what the JD is actually
screening for, don't dump all of them into every resume.

**ATS formatting rules — do not deviate:**
- Single column, no tables, no text boxes, no headers/footers containing contact info (some
  parsers drop header/footer content entirely)
- No graphics, icons, or photos
- Standard, widely-supported font (Arial)
- Standard section headers in caps ("EMPLOYMENT HISTORY", "SKILLS", "LINKS") — not creative
  alternatives; ATS parsers pattern-match on common headers
- Dates in a consistent, unambiguous format (e.g. "Jan 2024 – Present")
- Bullet points via real list formatting, not manually typed dashes/unicode bullets (see the
  docx skill's numbering config)
- One page unless the employment history genuinely doesn't fit
- File format: PDF is fine for Greenhouse/Lever/most modern ATS. Check the application
  form's "accepted file types" — if docx is preferred or unclear, offer both.

## 4. Draft the cover letter

What actually moves the needle here is backed by real hiring data, not folk wisdom — a
candidate is roughly twice as likely to land an interview when a cover letter is included,
but most recruiters give it well under two minutes, and a large share will drop an
applicant over a single obvious error. So the letter has to earn its two minutes fast, read
like it was written by a specific person about a specific job, and be flawless.

**Structure** — four to five short paragraphs, addressed "Dear Hiring Manager" unless a
name is known:
1. **Opening** — state the role, then the hook: why it caught the user's attention, ideally
   echoing a specific phrase or fact from the JD rather than generic enthusiasm. If there's
   a referral, note that generically ("I was referred to this opening by a current
   employee") — **do not name the referrer in the letter body** unless the user explicitly
   says to include the name. The referral source is already tracked through the
   application's own referral field/link.
2. **Proof, mapped to the JD** — 1–2 paragraphs translating real experience into the JD's
   own stated needs, with specifics and numbers, not adjectives about the candidate ("I'm a
   strong communicator" is a claim; "grew the practice to $1M revenue in 18 months" is
   proof). Use the JD's language back at it where truthful.
3. **Why this role/company specifically** — reference something concrete and *different
   from paragraph 1* — the actual problem they're solving, the team structure, the stage,
   something about the company itself — to prove this isn't a form letter. This paragraph
   must add new information, not restate the opening hook in different words.
4. **Close** — brief, confident, no groveling.

**Rules that actually correlate with getting read, not just sounding nice:**
- **Target 200–350 words total.** Longer doesn't read as more thorough, it reads as unedited.
- **Never restate the resume.** The cover letter's job is to connect dots the resume can't
  (motivation, referral, specific-fit narrative) — if a sentence could be a resume bullet,
  cut it or make it a story instead.
- **Kill clichés and corporate fluff** — "I am a hard worker," "I am passionate about,"
  "team player," "I am writing to express my interest" as an opener. These read as generic
  and are the fastest signal that the letter wasn't customized.
- **One repetition check before calling it done.** Read the letter end to end and flag any
  word or idea that shows up in more than one paragraph. If two paragraphs are making the
  same observation about the JD, cut one and give the other paragraph a genuinely different
  job to do.
- **Proofread like it matters, because it does.** Typos and small errors get letters tossed
  outright far more often than a mediocre-but-clean letter does. Read it once for content,
  once purely for typos/grammar.
- **Don't let it sound AI-generated.** Generic, evenly-hedged, adjective-heavy prose is
  recognizable and works against the candidate — specific numbers, specific project names,
  and a clear point of view read as human.

## 5. Compensation and screening-question consistency

Before answering a "desired compensation" or similar question, check
`{{PROJECT_ROOT}}/JobSearch/data/jobs.json` for other applications **at the same company**.
If the user already stated a figure to that company, anchor the new answer close to it
(same floor, modest upward adjustment only if the new role is genuinely more
senior/scoped) — a large unexplained gap between two live applications at the same employer
reads as inconsistent. Log any new figure back to jobs.json via `update_job.py --set` so
future applications (to this or other companies) stay consistent. See
`{{PROJECT_ROOT}}/Profile/feedback-log.md` for past reasoning on this.

Standing answers (already decided, don't re-litigate per application) live in
`master-profile.md`'s "Standing application policies" section — read them fresh in case
they've changed, and follow them exactly (e.g. education disclosure, work authorization,
voluntary self-ID questions).

## 6. Build and file the documents

1. Use the **docx skill** to build the resume and cover letter as `.docx`, following its
   rules (US Letter page size, real bullet numbering not unicode characters, Arial font,
   table/width rules if any tables are used — though this resume format shouldn't need
   tables).
2. Validate with the docx skill's validation step.
3. Convert to PDF (e.g. `soffice --headless --convert-to pdf`).
4. Render a page image (`pdftoppm`) and actually look at it before calling it done — check
   for overflow, awkward page breaks, and that the tailored summary reads naturally.
5. **File per application, not flat.** Every application gets its own folder:
   `{{PROJECT_ROOT}}/Applications/<Company> - <Role>/`. Use a clean, human-readable company
   name (not the full legal/ticker string from jobs.json — "Acme" not "Acme Inc. (NASDAQ:
   ACME)"). Inside that folder, save `Resume.pdf` and `Cover Letter.pdf` — the folder name
   already carries the company/role context, so the files themselves don't need to repeat
   it. If a document gets revised later, overwrite in place — the folder is the single
   source of truth for that application, don't leave stale flat copies elsewhere.
6. If this application is tracked in jobs.json, record the folder path in the job's record
   via `update_job.py --set '<id>' '{"documents_path":"Applications/<Company> - <Role>/"}'`
   so it's easy to find later.

## 6a. Verify the write actually landed — don't trust the bash exit code

Documents get built in the shell sandbox (needed for the docx skill/LibreOffice), but the
shell's view of a connected folder and the file tools' view of that same folder can be two
different execution contexts — a `cp`/`mv` that reports success inside the sandbox is not
proof the change reached the real, user-visible file.

Every single time a file is written or overwritten into a connected folder, before telling
the user it's done:
1. Use **Glob** (the host-side tool, not bash `ls`) to confirm the exact path exists.
2. Where practical, re-read the content back (e.g. re-extract the PDF text, or diff a
   checksum against the sandbox-side source file) to confirm it's actually the new version,
   not a stale one.
3. State the exact absolute path in the chat text itself — not just inside a file card —
   especially right after any folder reorganization, since the user may still be checking
   the old location out of habit.

Only after that verification passes, call `present_files` on the PDFs so the user can open
them directly. Do this for first drafts and for edits alike — a one-line fix still gets the
full verify-then-show treatment, not just a description of what changed.

## 7. Self-audit before calling it done

Go bullet by bullet, line by line, through both documents and check each factual claim
against `master-profile.md` / `github-projects.md`. Anything you can't point to a specific
line in those files for — a number, a technology, a claim of scope — either cut it or go
verify it with the user first. This step is not optional and is the whole point of this
skill existing.

## 8. Handling real gaps (the honest way to compete)

If the JD requires something genuinely not in the user's background, do not paper over it
with vague language designed to imply something untrue. Options, in order of preference:
- Omit it and let the strength of the matching qualifications carry the application
- Address it honestly in the cover letter as a fast-learner/adjacent-experience point, if
  there's a real adjacent story (e.g. "no direct telephony experience, but built X which
  required learning Y under similar constraints")
- Flag the gap to the user directly rather than silently deciding for them — a generic
  "degree required" line usually isn't a real fit risk, but a genuine hard-skills gap might
  be worth a heads-up before they spend time on the application

## 9. Never submit

Fill out the actual application form completely, but always leave the final "Submit" click
to the user — every time, regardless of how much prep work went into the application.
