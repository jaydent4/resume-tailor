---
name: resume-tailor
description: Creates a tailored resume using LaTeX and the job posting. Use when the user asks to "tailor my resume for [ROLE NAME]" or "tailor my resume for the role in [FILE NAME].txt". Works from a job description as text file and a master resume as a LaTeX file.
---

# Resume Tailor

## Overview

Generates a one-page, ATS-friendly LaTeX resume tailored to a specific role by selecting the best content variants from the master resume at `references/master.tex` and compiling them against a target job description.

## Inputs

- **Job description** — a `.txt` file in `jds/` (or pasted text).
- **Master resume** — `references/master.tex` (resume content only; never edited).
- **Directives** — `references/directives.md` (generation rules, archetype selection, coursework/skills presets).

## Output

- A single compilable `.tex` file written to `output/<role>.tex`, and a PDF via `scripts/compile.sh output/<role>.tex`.
- If the posting takes a cover letter: `output/<role>-coverletter.tex` (from `references/coverletter.template.tex`) and its compiled PDF.
- If the posting has any free-text fields (cover letter body, "why this company", essays, etc.): `output/<role>-responses.txt` holding every written response in plain, copy-pasteable text.

## Instructions

### Step 1: Get Job Posting Information

Read the job description from the text file specified by the user. All job descriptions are held in the `jds` directory:

```bash
cat jds/<ROLE NAME>.txt
```

If this fails or the user did not provide a file name, grab the most recently added or updated job description:

```bash
ls -t jds/*.txt 2>/dev/null | head -1 | xargs cat
```

If there is no job description files in `jds`, inform the user to add a job description in `jds`.

Gather:

- What is the role?
- What skills or experiences is the job description asking for?
- What are the skills that are required for the role?
- What are the skills that are optional but preferred for the role?
- Does the job posting take a cover letter?
- Does the job posting have any other questions that require a response (e.g. Why do you want to work at [COMPANY NAME]?)?

### Step 2: Research the Company's Values, Work, and Past Resumes

Build context beyond the job description so the resume speaks the company's language.

1. **Company research.** Search the web for the company's product, mission, tech stack, and engineering culture. Note recurring keywords and values (e.g "ownership", "customer obsession", specific languages/frameworks) to mirror in bullet selection and phrasing.
2. **Map to an archetype.** Use the findings plus the JD to pick the role archetype (A–G) from the Role Archetype Selection Guide in `references/directives.md`.
3. **Research what gets interviews.** Search the web for interview reports, offer write-ups, and resume advice for this company/role (e.g. r/EngineeringResumes, Glassdoor, blog posts). Extract the skills and signals they screen for, not resumes to copy. Treat anything found as phrasing/keyword guidance only; never import facts, metrics, or experiences from it.
4. **Review past tailored resumes.** Check `examples/` for resumes targeting similar roles or companies, and reuse variant/skills-preset choices that worked:

```bash
ls -t examples/*.tex 2>/dev/null
```

Capture: the chosen archetype, the company keywords to emphasize, and any prior example worth modeling.

### Step 3: Tailor the Master Resume for the Role

Using the archetype, keywords, and JD requirements gathered above, assemble a one-page resume from `references/master.tex`, following every rule in `references/directives.md`.

1. **Select content by archetype.** Follow the archetype's recommended experiences, projects, coursework preset, and Technical Skills preset from `references/directives.md`.
2. **Pick one variant per entry.** For each chosen experience and project, include exactly ONE bullet variant, the one that best matches the JD's required and preferred skills.
3. **Prioritize Experience, then trim.** Experience outranks Projects and Skills for page space (directive §1.10). Keep 3–4 experiences and 2–3 projects, give the most relevant and recent experiences their fullest bullet set (up to 4, at least 3 when strongly relevant), and keep projects leaner (2 bullets, 3 only for a flagship). When tight, cut from Projects/Skills/coursework/clubs before touching experience bullets. Order the most relevant experiences and projects highest; drop entries that do not map to the role.
4. **Mirror the JD's language.** Prefer the variants and skills that surface the company's keywords and required technologies, without inventing anything not in the master. Try to get in all keywords in the resume, including all skills and experiences required or preferred.
5. **Conditional sections.** Include the MS education entry only when the internship needs a graduation date past the undergraduate one (the MS pushes the expected grad date back); follow directive §1.7 in `references/directives.md`. Tailor coursework and the skills preset to the role.
6. **Write the output.** Save a clean, compilable `.tex` (no master-only comments) to `output/<role>.tex`.
7. **Lint the output.** Confirm the exported `.tex` has no master-only leftovers (guidance comments, un-deleted alternate variants) without re-reading it:

```bash
scripts/lint-output.sh output/<role>.tex
```

Fix anything it reports before compiling. It exits 0 when clean.

8. **Check keyword coverage.** Confirm the JD's required and preferred skills/technologies actually landed in the resume, by passing them to:

```bash
scripts/keyword-check.sh output/<role>.tex "Go" "Kubernetes" "GitHub Actions" "GCP"
```

For each keyword reported missing: add it only if it exists in `references/master.tex` (surface it via a different variant, an EXTRA bullet, or the skills preset). If a missing keyword is not in the master, do not invent it; note the gap to the user instead.

9. **Compile and verify (text-first, no images).** Build the PDF and confirm it fits on exactly one page. `compile.sh` prints a `Pages:` line (rely on it instead of reading the PDF) and flags any overfull-margin layout warnings:

```bash
scripts/compile.sh output/<role>.tex
```

If `Pages:` is more than 1, do NOT render the PDF to an image. Run the overflow diagnostic, which prints the spilled content as plain text so you can see exactly what to trim:

```bash
scripts/overflow.sh output/<role>.pdf
```

Trim per the order in directive §1.6 (EXTRA bullets → clubs → coursework → a Skills row → a project's bullets → least-relevant project → only last, an experience bullet), then recompile. Build to the one-page budget in directive §7 up front to keep this loop short. Never shrink fonts or margins below the template defaults unless it is absolutely needed to fit all required skills and experiences. Only render an image to read if the layout looks structurally wrong after `compile.sh`, `overflow.sh`, and `lint-output.sh` all pass.

Notify the user of which variants or bullet points are chosen with justification and of any formatting changes.

### Step 4: Cover Letter and Free-Text Responses

Only do this when Step 1 found the posting takes a cover letter or asks free-text questions. Ground every sentence in `references/master.tex`; never invent facts. Use the same voice as the resume: formal, no contractions, no em dashes.

1. **Cover letter (if the posting takes one).** Copy the template and fill it in:

```bash
cp references/coverletter.template.tex output/<role>-coverletter.tex
```

Replace every `<...>` placeholder. Copy the header personal details (name, phone, email, links) verbatim from the header block in `references/master.tex` so the letter matches the resume. Tailor the body to the company and role using the keywords and archetype from Steps 2–3. Keep it to one page, then compile and verify:

```bash
scripts/compile.sh output/<role>-coverletter.tex
```

`compile.sh` prints a `Pages:` line and flags overfull-margin warnings, same as for the resume. Trim until it is one page.

2. **Free-text responses.** Write every written response to `output/<role>-responses.txt` as plain text so the user can paste it straight into the application:
   - No markdown, no headings styling, no decoration.
   - Label each answer with the exact question, then a blank line, then the answer.
   - Each paragraph is one continuous line (no hard mid-paragraph line wraps) so it reflows cleanly in a web form textarea. Separate paragraphs with one blank line.
   - Include the cover letter text here too (in addition to the compiled PDF) when the form has an "enter manually" cover-letter box.
   - Respect any stated word limits on a question; note the word count if a limit applies.

Tell the user which responses were produced and where, and flag any application question you could not answer truthfully from the master resume.

## Rules

- NEVER invent projects, experiences, metrics, or technologies not in the master.
- No em dashes, no contractions, formal tone, pdflatex-compatible.
- Trim coursework/clubs/skills before shrinking fonts or margins.
- Do not include URLs except for Github profile links or Linkedin headers.
- Follow Jake's Resume template in `references`.
- Final resumes must be exactly 1 page.
- Prioritize Experience over Projects and Skills for page space. Maximize experience bullets whenever they fit (up to 4 on the most relevant/recent, at least 3 when strongly relevant); keep projects to 2 bullets (3 only for a flagship). When over a page, trim Projects/Skills/coursework/clubs before cutting any experience bullet.

## Reference

- `references/master.tex` — master resume content (all roles, projects, bullet variants)
- `references/directives.md` — generation rules, archetype selection, coursework/skills presets
- `references/directives.template.md` — reusable skeleton for writing a directives file
- `references/coverletter.template.tex` — reusable one-page cover letter LaTeX template (matches the resume header)
- `scripts/lint-output.sh` — check an exported `.tex` for master-only leftovers without reading it
- `scripts/keyword-check.sh` — confirm the JD's required/preferred keywords made it into the resume
- `scripts/compile.sh` — compile a tailored `.tex` to PDF (reports page count and layout warnings)
- `scripts/pdf-pages.sh` — report a PDF's page count to check the 1-page rule without reading the PDF
- `scripts/overflow.sh` — when a resume overflows, print the spilled page-2 text (so you trim without reading a rendered image)
