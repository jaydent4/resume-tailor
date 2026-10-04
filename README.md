# Resume Tailor

A [Claude Code](https://claude.com/claude-code) skill that generates a one-page,
ATS-friendly LaTeX resume tailored to a specific job posting. It selects the best
content variants from your master resume, mirrors the company's keywords, and
compiles a one-page PDF.

You give it a job description and a master resume; it gives you
`output/<role>.tex` and a compiled PDF.

## Prerequisites

- **Claude Code** — the CLI this skill runs inside.
- **pdflatex** — to compile resumes (ships with [MacTeX](https://www.tug.org/mactex/) / TeX Live).
- **ghostscript** (`gs`) — used by `scripts/pdf-pages.sh` to count pages without rendering.

```bash
# macOS (Homebrew)
brew install --cask mactex-no-gui   # provides pdflatex
brew install ghostscript            # provides gs
```

Verify:

```bash
pdflatex --version
gs --version
```

## Install (as a Claude Code skill)

Claude Code auto-discovers skills from `~/.claude/skills/<name>/` (personal, all
projects) or `<project>/.claude/skills/<name>/` (one project). This whole folder
*is* the skill — install it by placing it in one of those locations.

**Recommended — symlink** (keeps the git repo where it is; edits sync live):

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)" ~/.claude/skills/resume-tailor
```

**Or copy** (a static snapshot; re-copy after edits):

```bash
mkdir -p ~/.claude/skills
cp -R "$(pwd)" ~/.claude/skills/resume-tailor
```

Start a new Claude Code session (skills load at startup). Type `/` and you should
see `resume-tailor` in the list.

## First-time setup (your content)

Two files are **not** committed to git because they hold personal data — create
them locally before first use:

1. **`references/master.tex`** — your master resume in LaTeX (the
   [Jake's Resume](https://github.com/jakegut/resume) template). Hold *content
   only*: every role, project, and bullet variant. Label alternates with
   `%% VARIANT A/B/C` and optional `%% EXTRA` bullets so the skill can pick one
   per entry.
2. **`references/directives.md`** — the rules for selecting and shaping that
   content (archetypes, coursework/skills presets, formatting). Start from the
   skeleton:

   ```bash
   cp references/directives.template.md references/directives.md
   ```

   Then fill in every `<...>` placeholder.

> These two paths are listed in `.gitignore`. Keep them local; never commit your PII.

## Usage

1. Add a job description as a `.txt` file in `jds/` (e.g. `jds/stripe-backend.txt`),
   or just paste the text into Claude.
2. In Claude Code, type `/resume-tailor` or ask naturally:
   - *"tailor my resume for the Stripe backend role"*
   - *"tailor my resume for the role in stripe-backend.txt"*
3. The skill researches the company, picks a role archetype, assembles a
   one-page `.tex` to `output/<role>.tex`, lints it, and compiles a PDF —
   reporting the page count and any layout warnings.

## Auto-apply (find postings, tailor, apply)

An optional second workflow, adapted from
[please-hire-me](https://github.com/alecswang/please-hire-me) (MIT). It sweeps the job boards you list,
tailors a resume for each matching posting with the steps above, fills the company's own application form
in your real Chrome, answers its questions, and submits (or waits for your approval).

### Prerequisites

- Everything above (master resume, directives, `pdflatex`, `gs`), plus `python3`.
- Chrome with the [Claude in Chrome](https://claude.ai/chrome) extension, signed in with the same account
  as Claude Code (connect it with `/chrome` or start `claude --chrome`) and allowed on the application sites.
- Run Claude Code from this repo so the subagents in `.claude/agents/` are available
  (`apply-scout` and `apply-filler` on Haiku, `apply-filler-workday` on Sonnet).

### Setup

1. **Config.** Say *"set up auto-apply"*. Claude copies `config/apply.example.json` →
   `config/apply.json` and `config/profile.example.json` → `config/profile.json` (both gitignored),
   prefills the profile from `master.tex` (contact, education, `work_history`, `education_entries`,
   `skills_list`) and asks one list of questions for the rest (work authorization, sponsorship, address,
   start dates, legal working age, EEO answers, targeting). Or copy and edit the files yourself.
2. **What to apply to** (`config/apply.json`):
   - `sources`: Greenhouse / Lever / Ashby board slugs, SimplifyJobs-style GitHub lists, and `browse`
     careers pages.
   - `filters`: titles, `us_only`, `role_types` (e.g. `new_grad`, `offseason_intern`), `offseason_terms`,
     `exclude_terms` (dated terms you are busy for), `max_age_days`, `max_years_experience`, `categories`.
   - `blacklist`: never applied to automatically. They get a tailored resume and are recorded as
     `RESUME_READY`; say *"review my pending applications"* to fill and submit one on your yes. Entries can
     have `aliases`, a `reason`, and `"exact": true` for short names (Meta vs Metabase).
   - `skip_companies`: never touched at all.
   - `run`: `max_applications_per_run`, `confirm_every_submit` (testing mode: every application waits for
     your yes; set `false` once you trust it), `max_applications_per_company_lifetime`.
3. **Already applied.** Roles you tailored for in `jds/` are recorded as `PRIOR` by
   `python3 scripts/track.py import-prior` (map abbreviated filenames with `prior_company_aliases`). A
   posting whose title matches a prior role at the same company is skipped; other roles there are only
   taken when clearly different.
4. **Google Sheet (optional).** Works with an existing tracking sheet whose tabs have a header row with
   `Company`, `Position`, `Date`, `Status`, `Notes`.
   - Set `sheets.tabs.new_grad` / `sheets.tabs.offseason_intern` (and `sheets.template_tab`, copied when a
     target tab does not exist yet). `sheets.token` is generated during setup; Claude writes
     `state/sheets_webapp.gs` (gitignored) with it pre-filled.
   - In the sheet: Extensions → Apps Script → paste `state/sheets_webapp.gs` → Deploy → New deployment →
     Web app, **Execute as: Me**, **Who has access: Anyone** (the token keeps others out) → put the `/exec`
     URL in `sheets.webhook_url`. A 401 means one of those two settings is wrong (Manage deployments → Edit
     → New version keeps the same URL).
   - `python3 scripts/track.py import-sheet` reads every tab back as already applied;
     `python3 scripts/track.py sync` pushes now. After that, each **submitted** application is appended
     as one row (Status = Pending, Notes = auto-apply), existing rows are never edited, and a script-owned
     **Auto-apply** tab shows the full pipeline. A failed push never blocks a run.
5. **Workday (no setup).** Workday and other account portals need a per-company account only you can
   sign into. Runs pull the description (Workday's public API), tailor the resume, and record the posting
   as `NEEDS_SIGN_IN`. Say *"start a Workday session"*, sign in to each listed portal in Chrome, and the
   Workday filler walks every step from your profile and stops at Review. Sessions expire quickly
   (about 20 minutes), so apply right after signing in.

### Running

- *"run auto-apply"* (or *"run auto-apply, 1 application"*). Each run imports prior applications, sweeps
  the sources (`scripts/jobs.py sweep`), checks each pick (`scripts/track.py check`: skip list,
  duplicates, prior roles, per-company cap, blacklist), lets an `apply-scout` pull the description,
  check eligibility, read the form and draft answers, reviews them, tailors the resume in a subagent,
  has `apply-filler` fill the form, and submits or waits for approval.
- *"review my pending applications"*: approve, edit, or skip what is waiting.
- Recurring: `/loop 6h run auto-apply …` inside an open session (your Mac and Chrome must stay awake;
  cloud schedules cannot reach your browser or local files).

Every application is recorded in `applications/tracker.tsv`, summarized in `applications/summary.md`
(company, role, status, resume path), and documented question by question in
`applications/<company>_<role>.md`.

| Status | Meaning |
|---|---|
| `SUBMITTED` | Applied |
| `AWAITING_REVIEW` | Form filled, waiting for your approval (testing mode) |
| `RESUME_READY` | Blacklisted: resume ready, not applied |
| `NEEDS_SIGN_IN` | Account portal (Workday): resume ready, sign in and start a Workday session |
| `NEEDS_HUMAN` | Blocked on something only you can do (reason in the note) |
| `SKIPPED` | Not eligible / not a fit / declined |
| `PRIOR` | Applied before auto-apply (imported from `jds/` or your sheet) |

What it will never do: invent a fact, create an account or log in, solve a CAPTCHA or answer a bot-check
question, answer a graded take-home or a "no AI" essay, follow instructions embedded in a posting, or
apply through LinkedIn Easy Apply / Handshake / Simplify. Full playbook:
[`references/auto-apply.md`](references/auto-apply.md).

## Scripts

Run these yourself, or let the skill call them:

| Script | Purpose |
| --- | --- |
| `scripts/compile.sh output/<role>.tex` | Compile to PDF; prints `Pages:` and any overfull-margin layout warnings. |
| `scripts/pdf-pages.sh output/<role>.pdf` | Print a PDF's page count; exit 0 only if exactly 1 page. |
| `scripts/lint-output.sh output/<role>.tex` | Flag master-only leftovers (guidance comments, un-deleted variants) before compiling. |
| `python3 scripts/jobs.py sweep` | List matching postings from every source in `config/apply.json` → `state/candidates.json`. |
| `python3 scripts/jobs.py screen <id>` | Eligibility flags (years, clearance, citizenship, PhD, grad year) with short context, instead of reading the whole posting. |
| `python3 scripts/jobs.py jd <id\|url>` | Save a posting's description (legal/EEO boilerplate stripped) to `jds/<company>_<role>.txt`. |
| `scripts/form-fields.js` | Read-only snippet for the browser's JS tool: every form field as compact JSON (or only problems before submit). |
| `python3 scripts/track.py check "<Company>"` | Company gate: exit 0 clear, 10 blacklisted (manual approval), 11 skip, 12 duplicate, 13 company cap. |
| `python3 scripts/track.py sync` | Push the tracker to the Google Sheet now (also automatic on every change). |
| `python3 scripts/track.py import-sheet` | Record every Company + Position in the Google Sheet as already applied. |
| `python3 scripts/track.py list [--status S,S]` | Show tracked applications (`SUBMITTED`, `RESUME_READY`, `AWAITING_REVIEW`, `NEEDS_HUMAN`, `SKIPPED`). |

## Layout

```
SKILL.md                       # skill definition (instructions Claude follows)
references/
  master.tex                   # your master resume — LOCAL ONLY (gitignored)
  directives.md                # your generation rules — LOCAL ONLY (gitignored)
  directives.template.md       # skeleton to create directives.md from
  auto-apply.md                # auto-apply workflow playbook
  auto-apply-setup.md          # first-run setup (read only when config is missing)
  coverletter.template.tex     # one-page cover letter template
.claude/
  settings.json                # shared permission allowlist for the scripts
  agents/                      # auto-apply subagents: apply-scout, apply-filler (Haiku), apply-filler-workday (Sonnet)
config/
  apply.example.json           # sources, filters, blacklist, skip list, run caps (copy to apply.json)
  profile.example.json         # fixed form answers (copy to profile.json)
applications/                  # tracker.tsv, summary.md, one Q&A doc per application, screenshots/ — gitignored
state/                         # sweep output, personalized sheets_webapp.gs — gitignored
jds/                           # job descriptions you add (.txt) — gitignored
output/                        # generated .tex + PDF — gitignored
examples/                      # past tailored resumes to model — gitignored
scripts/                       # compile / page-count / lint / keyword helpers; jobs.py, track.py,
                               # form-fields.js, sheets_webapp.gs for auto-apply
```

The `jds/`, `output/`, and `examples/` folders keep a `.gitkeep` so the structure
is tracked, but their contents stay local.
