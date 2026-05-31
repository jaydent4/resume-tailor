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

## Scripts

Run these yourself, or let the skill call them:

| Script | Purpose |
| --- | --- |
| `scripts/compile.sh output/<role>.tex` | Compile to PDF; prints `Pages:` and any overfull-margin layout warnings. |
| `scripts/pdf-pages.sh output/<role>.pdf` | Print a PDF's page count; exit 0 only if exactly 1 page. |
| `scripts/lint-output.sh output/<role>.tex` | Flag master-only leftovers (guidance comments, un-deleted variants) before compiling. |

## Layout

```
SKILL.md                       # skill definition (instructions Claude follows)
references/
  master.tex                   # your master resume — LOCAL ONLY (gitignored)
  directives.md                # your generation rules — LOCAL ONLY (gitignored)
  directives.template.md       # skeleton to create directives.md from
jds/                           # job descriptions you add (.txt) — gitignored
output/                        # generated .tex + PDF — gitignored
examples/                      # past tailored resumes to model — gitignored
scripts/                       # compile / page-count / lint helpers
```

The `jds/`, `output/`, and `examples/` folders keep a `.gitkeep` so the structure
is tracked, but their contents stay local.
