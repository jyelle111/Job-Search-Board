#!/usr/bin/env python3
"""Build the job board artifact HTML: merges data/jobs.json into artifact/template.html.

Also computes ephemeral, board-only fields that are NOT written back to jobs.json:
  - resume_preview / cover_letter_preview: extracted text from the PDFs under
    documents_path (if any), truncated, so the board can show a read-only preview
    without needing local file:// links (the artifact sandbox can't reach them).
  - resume_host_path / cover_letter_host_path: the human-readable absolute path,
    for you to open the real file yourself.

Usage: build_board.py [output_path]
Default output: JobSearch/artifact/board.html
"""
import json, os, sys, subprocess, copy

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "..", "artifact", "template.html")
DATA = os.path.join(HERE, "..", "data", "jobs.json")

# EDIT THIS before first use: the absolute path to this project's root folder, exactly as
# it appears in Finder/Explorer on your computer (used to build "open this file yourself"
# links on the board, since the artifact sandbox can't open local files as links).
# Example: "/Users/yourname/Documents/job-search"
RESUME_ROOT_HOST = "/Users/YOURNAME/Documents/job-search"  # <-- change me

# JobSearch/scripts -> JobSearch -> project root (repo root as you see it in Finder)
RESUME_ROOT_LOCAL = os.path.join(HERE, "..", "..")  # local filesystem equivalent, for reading PDFs

PREVIEW_CHARS = 6000

def extract_pdf_text(path):
    if not os.path.isfile(path):
        return ""
    try:
        out = subprocess.run(["pdftotext", "-layout", path, "-"],
                              capture_output=True, text=True, timeout=20)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()[:PREVIEW_CHARS]
    except Exception:
        pass
    # fall back to pypdf if pdftotext is unavailable or produced nothing
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = "\n".join((p.extract_text() or "") for p in reader.pages)
        return text.strip()[:PREVIEW_CHARS]
    except Exception:
        return ""

def with_previews(job):
    """Return a shallow copy of job with ephemeral preview/path fields added."""
    dp = job.get("documents_path")
    if not dp:
        return job
    j = copy.copy(job)
    local_dir = os.path.normpath(os.path.join(RESUME_ROOT_LOCAL, dp))
    host_dir = dp.rstrip("/")
    resume_local = os.path.join(local_dir, "Resume.pdf")
    cover_local = os.path.join(local_dir, "Cover Letter.pdf")
    if os.path.isfile(resume_local):
        j["resume_preview"] = extract_pdf_text(resume_local)
        j["resume_host_path"] = RESUME_ROOT_HOST + "/" + host_dir + "/Resume.pdf"
    if os.path.isfile(cover_local):
        j["cover_letter_preview"] = extract_pdf_text(cover_local)
        j["cover_letter_host_path"] = RESUME_ROOT_HOST + "/" + host_dir + "/Cover Letter.pdf"
    return j

tpl = open(TPL).read()
db = json.load(open(DATA))
board_db = dict(db)
board_db["jobs"] = [with_previews(j) for j in db.get("jobs", [])]
payload = json.dumps(board_db, ensure_ascii=False).replace("</", "<\\/")
html = tpl.replace("__JOBBOARD_DATA__", payload)
if "__JOBBOARD_DATA__" in html:
    print("ERROR: placeholder still present after merge"); sys.exit(1)
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "artifact", "board.html")
open(out, "w").write(html)
print("BUILT", out, "jobs:", len(db.get("jobs", [])), "updated:", db.get("updated_at"))
