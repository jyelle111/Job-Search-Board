---
name: job-board-refresh
description: On-demand — rebuild the job board artifact from the latest jobs.json (wired to the board's "Refresh board data" button).
---

Rebuild the job board artifact from the latest data. Before first use, replace
`{{SANDBOX_MOUNT}}` and `{{SANDBOX_MOUNT_OUTPUTS}}` with your real paths (see
`job-search-morning.md`'s intro for how to find them).

Steps:
1. Run via `mcp__workspace__bash`:
   `python3 {{SANDBOX_MOUNT}}/JobSearch/scripts/build_board.py /tmp/board.html`
   (If the sandbox mount path differs, locate it: `ls -d /sessions/*/mnt/*`)
2. Copy the built file into your own outputs/scratch directory so the artifact tool can
   read it (e.g. `cp /tmp/board.html {{SANDBOX_MOUNT_OUTPUTS}}/board.html` — or use the
   Read/Write tools with your session's outputs path).
3. Call `mcp__cowork__update_artifact` with the board artifact's id, `html_path` pointing
   at the copied file, and `update_summary` "Data refresh from jobs.json".
4. Do NOT modify jobs.json or any other file. If a step fails, report the exact error briefly.

Final output: one line — "Board refreshed: N jobs, updated <timestamp>" (values printed by
`build_board.py`).
