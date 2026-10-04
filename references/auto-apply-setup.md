# Auto-Apply First-Run Setup

Read only when `config/apply.json` or `config/profile.json` is missing. Do not open a browser or apply
during setup.

1. Copy only what is missing, never overwrite: `cp -n config/apply.example.json config/apply.json; cp -n config/profile.example.json config/profile.json`
2. Prefill `profile.json` from `references/master.tex`: header and education (name, email, phone, links,
   school, degree, major, graduation, a later graduate degree as `graduation_ms`, GPA if present), plus
   `work_history` (every role, newest first; each description = one paragraph merging all of that role's
   bullets, variants and extras, without bullet markers or `< > [ ] " { } \`), `education_entries`, and
   `skills_list` (the whole Technical Skills section, most important first). Show the extracted values.
3. Ask everything else in **one** numbered list. Say the count up front, mark optional items, and give
   the default used for anything skipped. Never send a second round for something you forgot; take the
   template default and say so.
   - About them: personal (non-.edu) email, mailing address, work authorization, sponsorship now or
     later, citizenship (export-control questions), college start, earliest start / internship terms,
     relocation, legal working age, competing offer deadlines, transcript path, pronouns, and each EEO answer
     asked separately (default "Decline to self-identify"; never inferred from a name or resume).
   - Targeting (skip anything `config/apply.json` already sets, e.g. a filled blacklist): roles,
     internship vs new grad, locations, sources, the **blacklist** (manual approval before submit),
     companies to skip entirely, per-run cap.
4. Write both files, read back what was written, and note that `config/`, `applications/`, and
   `state/` stay local (gitignored). Run `python3 scripts/track.py import-prior` to record roles already
   applied to (from `jds/`; add `prior_company_aliases` for abbreviated filenames).
4b. Optional Google Sheet: offer the setup in README ("Google Sheet"). For an existing tracking sheet, ask
   which tabs new-grad and off-season submissions go to (`sheets.tabs`), generate `state/sheets_webapp.gs`
   from `scripts/sheets_webapp.gs` with `TOKEN` = `sheets.token` (create a random token if empty), and after
   the user pastes the web app URL run `track.py import-sheet` (shows tab counts) before the first `sync`.
4c. Optional Workday: explain that runs queue Workday postings as NEEDS_SIGN_IN and "start a Workday
   session" applies them after the user signs in; nothing to configure up front.
5. Offer a supervised first run: one application, stopping before submit for approval even if the
   company is CLEAR.
