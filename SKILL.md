---
name: resume-tailor
description: Tailors a one-page LaTeX resume (plus cover letter and application answers) to a job posting, and runs an auto-apply workflow that finds postings, tailors, fills, and submits applications (blacklisted companies wait for approval). Use for "tailor my resume for [ROLE]", "tailor my resume for the role in [FILE].txt", "apply to jobs", "run auto-apply", "review my pending applications", "set up auto-apply".
---

# Resume Tailor

Builds a one-page, ATS-friendly resume by selecting the best content variants from `references/master.tex` (content only, never edited) under the rules in `references/directives.md`, against a job description in `jds/`.

## Workflows

- **Tailor** (one role): Steps 1–4 below.
- **Auto-apply** ("apply to jobs", "run auto-apply", "review my pending applications", "set up auto-apply"): read `references/auto-apply.md` and follow it. It runs Steps 1–4 in pipeline mode per posting.

### Pipeline mode (Steps 1–4 called by auto-apply)

The caller gives a JD file, role slug, cover letter yes/no, and the form's free-text questions. Differences from a normal run:

- Use the given JD file and slug (`output/<name>_resume_<company>_<role>.tex`); never pick the newest file in `jds/`.
- Skip the Step 1 cover letter / question discovery; write a Step 4 response for **every** question given, labeled verbatim, within its limit.
- Step 2: if `output/` already has a resume for this company (`ls output/*_resume_<company>*.tex`), start from the closest one and re-check it against this JD instead of researching from scratch. Otherwise at most two quick searches for company keywords; no interview-report research.
- Never ask the user anything. Reply with the short report the caller asked for (paths, `Pages:` line, missing keywords, unanswerable questions), not the Step 3/4 user notes.
- All Rules still apply. Flag, never invent.

## Output

- `output/<name>_resume_<role>.tex` and its PDF. `<name>` = master header name lowercased with underscores (e.g. `jane_doe`); `<role>` = short role slug (directive 14).
- Cover letter (if the posting takes one): `output/<name>_resume_<role>-coverletter.tex` + PDF.
- Free-text answers (if any): `output/<name>_resume_<role>-responses.txt`.

## Step 1: Read the job posting

`cat jds/<ROLE NAME>.txt`. No file named → newest: `ls -t jds/*.txt | head -1 | xargs cat`. No files → ask the user to add one to `jds/`.

Gather: the role; required skills; preferred skills; whether it takes a cover letter; any other questions needing a written response.

## Step 2: Research

1. **Company:** search the product, mission, tech stack, and engineering culture. Note recurring keywords and values to mirror.
2. **Archetype:** pick A–G from the Role Archetype Selection Guide in `references/directives.md`.
3. **What gets interviews:** search interview reports and resume advice for this company/role (r/EngineeringResumes, Glassdoor, blogs). Use only as keyword/phrasing guidance; never import facts, metrics, or experiences.
4. **Past resumes:** `ls -t examples/*.tex output/*.tex 2>/dev/null | head -20`; reuse archetype/skills-preset choices from similar roles or the same company.

Capture: archetype, keywords to emphasize, any prior resume to model.

## Step 3: Tailor

Follow every rule in `references/directives.md`.

1. **Select by archetype:** its experiences, projects, coursework preset, and skills preset.
2. **One variant per entry:** the bullet variant that best matches the JD's required and preferred skills.
3. **Experience first** (§1.10): 3–4 experiences, 2–3 projects. Most relevant/recent experiences get their fullest bullet set (up to 4, at least 3 when strongly relevant); projects get 2 bullets (3 only for a flagship). Order by relevance; drop entries that do not map to the role.
4. **Mirror the JD:** prefer variants and skills that surface its keywords and required technologies. Aim to cover every required and preferred skill that exists in the master.
5. **Conditional sections:** MS entry only when the internship needs a grad date past the undergraduate one (§1.7). Tailor coursework and skills preset to the role.
6. **Write** a clean `.tex` (no master-only comments) to `output/<name>_resume_<role>.tex`.
7. **Lint:** `scripts/lint-output.sh <tex>` (exit 0 = clean). Fix anything reported.
8. **Keywords:** `scripts/keyword-check.sh <tex> "Go" "Kubernetes" ...` with the JD's required/preferred skills. Add a missing one only if it is in `master.tex` (another variant, an EXTRA bullet, or the skills preset); otherwise report the gap.
9. **Compile:** `scripts/compile.sh <tex>`. Trust its `Pages:` line and layout warnings; do not read the PDF.
   - **Over 1 page:** `scripts/overflow.sh <pdf>` prints the spilled text. Trim in §1.6 order (EXTRA bullets → clubs → coursework → a Skills row → a project's bullets → least relevant project → last, an experience bullet), recompile.
   - **Fill the page (§7):** build slightly rich so the first compile is at or just over one page, then trim to fit. If it fits with obvious empty space, add the next most valuable real bullet from the master (experience first, then projects) until one more would overflow.
   - Never shrink fonts or margins below template defaults unless it is the only way to fit all required skills and experiences. Render an image only if the layout looks structurally wrong after compile, overflow, and lint all pass.

Tell the user which variants/bullets were chosen and why, and any formatting changes.

## Step 4: Cover letter and free-text responses

Only when Step 1 found them. Ground every sentence in `master.tex`. Same voice as the resume.

1. **Cover letter:** `cp references/coverletter.template.tex output/<name>_resume_<role>-coverletter.tex`, replace every `<...>`, copy the header details verbatim from `master.tex`, tailor the body with the Step 2–3 keywords. `scripts/compile.sh` it and trim to one page.
2. **Responses** in `output/<name>_resume_<role>-responses.txt`, plain text: each answer labeled with the exact question, a blank line, then the answer. No markdown. One line per paragraph (no hard wraps), blank line between paragraphs. Include the cover letter text when the form has a text box for it. Respect word limits and note the count when one applies.

Tell the user what was produced and where, and flag any question that cannot be answered truthfully from the master.

## Rules

- NEVER invent projects, experiences, metrics, or technologies not in the master.
- No em dashes, no contractions, formal tone, pdflatex-compatible.
- URLs only for the GitHub profile and LinkedIn header.
- Jake's Resume template; exactly 1 page.
- Page priority: Experience > Projects > Skills/coursework/clubs (see Step 3.3 and the trim order).

## Reference

- `references/master.tex`, `references/directives.md` (+ `directives.template.md`), `references/coverletter.template.tex`
- `references/auto-apply.md` (+ `auto-apply-setup.md`) — auto-apply workflow
- `scripts/compile.sh` (build; prints `Pages:` and layout warnings, errors only on failure), `scripts/overflow.sh` (page-2 text), `scripts/lint-output.sh`, `scripts/keyword-check.sh`, `scripts/pdf-pages.sh`
- `scripts/jobs.py` (sweep / screen / jd), `scripts/track.py` (tracker + company gate), `scripts/form-fields.js` (compact form dump) — auto-apply
