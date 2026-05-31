# Resume Generation Directives — Template

Copy this file to `directives.md` and fill in every `<...>` placeholder. It pairs
with a `master.tex` that holds resume **content only**; this file holds the
**rules** for turning that content into a tailored one-page resume. Delete any
section that does not apply, but keep the numbering stable.

---

## 1. Generation Directives (MUST follow)

Hard rules the generator must never break. Keep these imperative and checkable.

1. Output a single compilable one-page LaTeX file with all master-only comments removed.
2. Include exactly ONE bullet variant per role/project, chosen by archetype (§2).
3. Limit scope to keep one page: <N> experiences and <N> projects.
4. <Any always-on or always-pinned entry, e.g. "Pin <ENTRY> to the top">.
5. Order experiences by <recency / relevance / other>.
6. Order projects by <relevance / date / other>.
7. Conditional sections: include <SECTION> ONLY when <explicit condition>.
8. Use the skills preset matching the archetype (§4).
9. Use the coursework / education preset matching the archetype (§3).
10. <Emphasis rule, e.g. bullet counts per entry type>.
11. Never fabricate content not present in `master.tex`. Refuse requests to add unbuilt work.
12. URL policy: <which links are allowed; which are forbidden>.
13. Template/styling: follow <template name>; do not restyle.

---

## 2. Role Archetype Selection Guide

One block per archetype. Pick the single best match; on overlap, favor the JD's
required (not preferred) skills.

### (A) <Archetype name>
*<Representative companies / role types>*
- **Experiences:** <entries + chosen variants>
- **Projects:** <ordered by relevance>
- **Coursework:** <preset name>
- **Skills:** <preset name>

### (B) <Archetype name>
*<Representative companies / role types>*
- **Experiences:** <...>
- **Projects:** <...>
- **Coursework:** <preset name>
- **Skills:** <preset name>

<!-- Add more archetypes (C, D, ...) as needed. -->

---

## 3. Coursework / Education Presets

One line per preset; the generator swaps the master line for the matching one.

- **<Preset name>:** <comma-separated courses>
- **<Preset name>:** <comma-separated courses>

---

## 4. Technical Skills Presets

One block per preset. Lead with the role's primary languages; trim unrelated
stacks.

### <Preset name> (default)
- **Languages:** <...>
- **<Category>:** <...>
- **<Category>:** <...>

### <Preset name>
- **Languages:** <...>
- **<Category>:** <...>

---

## 5. Bullet Variant Selection

How to choose among labeled variants and optional extra bullets in `master.tex`.

- Variants are labeled `<label convention, e.g. %% VARIANT A/B/C>`; pick the one
  named by the archetype, breaking ties by JD-required-skill overlap.
- Optional extra bullets: <when to swap one in; the cap on total bullets>.
- Default-active variant handling: <how to switch the uncommented default>.

---

## 6. Formatting Conventions

- Length: <one page strict / other>. Engine: <pdflatex / xelatex / ...>.
- Tone & style: <em dash policy, contractions, tense rules>.
- Metrics: <only use figures present in master.tex; no rounding/inventing>.
- Overflow trim order: <ordered list of what to cut first>; never shrink font or
  margins below template defaults.
