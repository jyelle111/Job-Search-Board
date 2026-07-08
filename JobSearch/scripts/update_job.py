#!/usr/bin/env python3
"""Safely update a job's status in jobs.json (atomic write + backup).

Usage:
  update_job.py <job_id> <new_status> [reason]
  update_job.py --add '<json object for one job>'
  update_job.py --answer <question_id> '<answer text>'
  update_job.py --note <job_id> '<note text>'
  update_job.py --set <job_id> '<json object of fields to merge>'
  update_job.py --add-interview <job_id> '<json object for one interview round>'
  update_job.py --interview-set <job_id> <interview_id> '<json object of fields to merge>'
  update_job.py --interview-note <job_id> <interview_id> '<note text>'

Valid statuses: new, interested, plan_pending, drafts_ready, approved_to_submit,
                applied, interviewing, offer, rejected, passed, skipped, expired
"""
import json, sys, os, tempfile, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "jobs.json")
VALID = {"new", "interested", "plan_pending", "drafts_ready",
         "approved_to_submit", "applied", "interviewing", "offer", "rejected",
         "passed", "skipped", "expired"}

def now():
    return datetime.datetime.now().isoformat(timespec="seconds")

def load():
    with open(DATA) as f:
        return json.load(f)

def save(db):
    db["updated_at"] = now()
    d = os.path.dirname(DATA)
    # backup last good copy
    try:
        os.replace(DATA, os.path.join(d, "jobs.backup.json"))
    except OSError:
        pass
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    os.replace(tmp, DATA)

def log(db, msg):
    db.setdefault("activity_log", []).insert(0, {"at": now(), "event": msg})
    db["activity_log"] = db["activity_log"][:200]

def find_job(db, job_id):
    for j in db["jobs"]:
        if j["id"] == job_id:
            return j
    return None

def main(argv):
    db = load()
    if argv[0] == "--add":
        job = json.loads(argv[1])
        ids = {j["id"] for j in db["jobs"]}
        if job["id"] in ids:
            print("DUPLICATE_ID"); return 1
        job.setdefault("status", "new")
        job.setdefault("date_found", now())
        db["jobs"].insert(0, job)
        log(db, f"added {job['id']} ({job.get('company')} — {job.get('title')})")
    elif argv[0] == "--note":
        job_id, text = argv[1], argv[2]
        hit = False
        for j in db["jobs"]:
            if j["id"] == job_id:
                j.setdefault("notes", []).append({"at": now(), "note": text})
                hit = True
        if not hit:
            print(f"NOT_FOUND {job_id}"); return 1
        log(db, f"note added to {job_id}")
    elif argv[0] == "--set":
        job_id, fields = argv[1], json.loads(argv[2])
        PROTECTED = {"id", "status", "notes"}
        hit = False
        for j in db["jobs"]:
            if j["id"] == job_id:
                for k, v in fields.items():
                    if k not in PROTECTED:
                        j[k] = v
                hit = True
        if not hit:
            print(f"NOT_FOUND {job_id}"); return 1
        log(db, f"fields set on {job_id}: {', '.join(fields.keys())}")
    elif argv[0] == "--answer":
        qid, answer = argv[1], argv[2]
        for q in db.get("daily_questions", []):
            if q["id"] == qid:
                q["answer"], q["answered_at"] = answer, now()
        log(db, f"answered question {qid}")
    elif argv[0] == "--add-interview":
        job_id, fields = argv[1], json.loads(argv[2])
        job = find_job(db, job_id)
        if not job:
            print(f"NOT_FOUND {job_id}"); return 1
        interview_id = fields.get("id") or ("int-" + str(int(datetime.datetime.now().timestamp() * 1000)))
        interviews = job.setdefault("interviews", [])
        if any(i.get("id") == interview_id for i in interviews):
            print("DUPLICATE_ID"); return 1
        record = {
            "id": interview_id,
            "round": fields.get("round", ""),
            "date": fields.get("date", ""),
            "format": fields.get("format", ""),
            "interviewers": fields.get("interviewers", ""),
            "added_at": now(),
            "prep": {"study_notes": "", "best_practices": "", "recommended_questions": ""},
            "my_notes": [],
        }
        interviews.append(record)
        # first interview scheduled moves the job into the interviewing stage,
        # but never downgrade a job that's already further along (offer/rejected).
        if job.get("status") not in ("interviewing", "offer", "rejected"):
            job["status"], job["status_changed_at"] = "interviewing", now()
        log(db, f"interview {interview_id} added to {job_id} ({record.get('round')})")
        print("OK")
        print(interview_id)
        save(db)
        return 0
    elif argv[0] == "--interview-set":
        job_id, interview_id, fields = argv[1], argv[2], json.loads(argv[3])
        job = find_job(db, job_id)
        if not job:
            print(f"NOT_FOUND {job_id}"); return 1
        hit = False
        PROTECTED = {"id", "my_notes"}
        for i in job.get("interviews", []):
            if i["id"] == interview_id:
                for k, v in fields.items():
                    if k == "prep" and isinstance(v, dict):
                        i.setdefault("prep", {}).update(v)
                    elif k not in PROTECTED:
                        i[k] = v
                hit = True
        if not hit:
            print(f"NOT_FOUND {interview_id}"); return 1
        log(db, f"interview {interview_id} on {job_id} updated: {', '.join(fields.keys())}")
    elif argv[0] == "--interview-note":
        job_id, interview_id, text = argv[1], argv[2], argv[3]
        job = find_job(db, job_id)
        if not job:
            print(f"NOT_FOUND {job_id}"); return 1
        hit = False
        for i in job.get("interviews", []):
            if i["id"] == interview_id:
                i.setdefault("my_notes", []).append({"at": now(), "note": text})
                hit = True
        if not hit:
            print(f"NOT_FOUND {interview_id}"); return 1
        log(db, f"note added to interview {interview_id} on {job_id}")
    else:
        job_id, status = argv[0], argv[1]
        reason = argv[2] if len(argv) > 2 else ""
        if status not in VALID:
            print(f"INVALID_STATUS {status}"); return 1
        hit = False
        for j in db["jobs"]:
            if j["id"] == job_id:
                j["status"], j["status_changed_at"] = status, now()
                if reason:
                    j.setdefault("notes", [])
                    j["notes"].append({"at": now(), "note": reason})
                hit = True
        if not hit:
            print(f"NOT_FOUND {job_id}"); return 1
        log(db, f"{job_id} -> {status}" + (f" ({reason})" if reason else ""))
    save(db)
    print("OK")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
