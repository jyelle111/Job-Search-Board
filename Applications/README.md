# Applications

Each application gets its own folder, created automatically the first time a job moves to
"interested": `Applications/<Company> - <Role>/`, containing `Resume.pdf` and
`Cover Letter.pdf` for that specific application.

This folder is intentionally excluded from git (see `../.gitignore`) — application
documents contain your personal information and shouldn't be committed to a shared or
public repo.

Nothing to set up here manually; the `resume-cover-letter-writer` skill creates these
folders as it drafts documents.
