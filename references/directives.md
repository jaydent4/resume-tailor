# Resume Generation Directives — SWE Internship Edition

These rules govern how a tailored one-page resume is assembled from
`master.tex`. `master.tex` holds **content only** (every role, project, and
bullet variant); this file holds **the rules** for selecting and shaping that
content. Read this file before generating.

---

## 1. Generation Directives (MUST follow)

When generating a tailored resume from `master.tex`, you MUST:

1. **Output a single compilable one-page LaTeX file** with all master-only
   comments removed (no `%% VARIANT`, `%% EXTRA`, `%% Repo`, `%% Stack`, or
   guidance comments). The preamble and custom commands carry over unchanged.
2. **Include exactly ONE bullet variant per role/project**, chosen by the role
   archetype in §2. Never emit two variants for the same entry.
3. **Fill exactly one page.** Use 3–4 experiences and 2–3 projects, and make the
   content fill the *full* page (reaching the bottom margin) without overflowing
   — an under-full page wastes the candidate's strongest real estate. When over,
   cut the least-relevant entries first; when under, add real `master.tex`
   bullets, experience first. See §7 for the budget and the fill method.
4. **Pin the incoming Everpure entry to the TOP of Experience** as a single
   bullet (it is chronologically in the future but leads the section).
5. **Order remaining experiences by recency** (most recent first).
6. **Order projects by RELEVANCE to the target role**, not by date.
7. **Include the MS Education entry only when the internship needs a graduation
   date past the undergraduate one (June 2027).** The MS (September 2027 -- June
   2028) pushes the expected graduation back to June 2028, keeping the candidate
   an eligible student for internships whose required/expected graduation falls
   after June 2027 (e.g. a Fall 2027, Winter/Spring 2028, or Summer 2028
   internship, or a JD stating "graduating December 2027 or later"). If the
   internship is satisfied by the June 2027 undergraduate date, omit the MS
   entry. When in doubt, omit it.
8. **Use the Technical Skills preset that matches the archetype** (§4), rendered
   in the default four-bucket layout (Languages / Frameworks / Developer Tools /
   Libraries), one line per bucket.
9. **Use the coursework preset that matches the archetype** (§3).
10. **Prioritize Experience over Projects and Skills.** Experience is the most
    valuable real estate on the page; spend the page budget on it first. When the
    page is tight, protect experience bullets and cut from Projects, Skills,
    coursework, and clubs before touching Experience (see §7). Standard SWE
    resume guidance is 3–5 bullets per role, with the most recent and most
    relevant roles getting the most.
    - **Maximize experience bullets whenever they fit:** give the most relevant
      and most recent experiences their full available bullet set (up to 4), and
      keep at least 3 on any experience that maps strongly to the role. Only drop
      to 2 on the least-relevant experience, and only when needed to hold one page.
    - **Keep projects leaner than experience:** 2 bullets each is the default,
      3 only for a flagship project that is central to the role. Projects never
      get more bullets than a relevant experience.
11. **Never fabricate.** Do not invent projects, experiences, metrics, dates, or
    technologies that do not appear in `master.tex`. If asked to add unbuilt
    work, refuse.
12. **Do not include URLs** except the GitHub profile and LinkedIn links in the
    header. Never link private or inaccessible repos.
13. **Follow the Jake's Resume template** already encoded in `master.tex`; do not
    restyle the document.

---

## 2. Role Archetype Selection Guide

Pick the single archetype that best matches the target role, then use its
experiences, projects, coursework preset, and skills preset. When a role spans
two archetypes, choose the one matching the JD's required (not preferred) skills.

### (A) General SWE Intern
*Google, Meta, Microsoft, Amazon SDE, Bloomberg, LinkedIn, Atlassian, most rotational programs*
- **Experiences:** Everpure + PSS Lab Variant A + UCLA TA Variant A + Redline
- **Projects:** Sharded KV Store, sojournal, JobBot
- **Coursework:** General SWE preset
- **Skills:** General SWE preset

### (B) Full-Stack / Product SWE
*Stripe, Notion, Datadog, Sentry, Asana, Airbnb, Discord, Vercel, Cloudflare, Plaid, Ramp*
- **Experiences:** Everpure + UCLA TA Variant A or C + PSS Lab Variant A + Redline
- **Projects:** sojournal, BruinDen, JobBot
- **Coursework:** Full-stack / Product preset
- **Skills:** Web / Product SWE preset

### (C) Systems / Infra / Platform SWE
*Pure Storage, Nutanix, Verkada, Cisco, Cloudflare infra, Databricks runtime, Snowflake, Confluent, Scale infra*
- **Experiences:** Everpure + PSS Lab Variant B + Security Lab + UCLA TA Variant B
- **Projects:** Sharded KV Store, Reliable Transport Protocol, JobBot
- **Coursework:** Systems / Infra preset
- **Skills:** Systems / Infra preset

### (D) Distributed Systems / Backend
*Confluent, MongoDB, Redis, Anthropic backend, OpenAI backend, Uber, Lyft, DoorDash backend, Square backend*
- **Experiences:** Everpure + PSS Lab Variant B or C + UCLA TA Variant B + Security Lab
- **Projects:** Sharded KV Store, sojournal, Reliable Transport Protocol
- **Coursework:** Systems / Infra preset
- **Skills:** Systems / Infra preset (Go/C++ forward)

### (E) ML / AI Engineering SWE
*Anthropic, OpenAI applied, Meta AI, Google DeepMind, Hugging Face, Cohere, Scale AI, NVIDIA ML*
- **Experiences:** Everpure + PSS Lab Variant A + UCLA TA Variant A + Redline
- **Projects:** EMG Keystroke Decoding, Protein Classifier, sojournal
- **Coursework:** ML preset
- **Skills:** AI / ML preset

### (F) Networking / Low-Level SWE
*Cisco, Arista, Juniper, network teams at hyperscalers, kernel teams*
- **Experiences:** Everpure + Security Lab + PSS Lab Variant B + UCLA TA Variant B
- **Projects:** Reliable Transport Protocol, Sharded KV Store, JobBot
- **Coursework:** Systems / Infra preset
- **Skills:** Systems / Infra preset

### (G) Startup / Early-Stage SWE
*YC startups, seed-stage, generalist roles*
- **Experiences:** Everpure + UCLA TA Variant A or C + PSS Lab Variant A + Redline
- **Projects:** sojournal, JobBot, BruinDen
- **Coursework:** Full-stack / Product preset
- **Skills:** Web / Product SWE preset

---

## 3. Coursework Presets

Replace the master coursework line with the preset matching the archetype.

- **General SWE:** Distributed Systems, Algorithms, Databases, Operating Systems, Computer Networking, Programming Languages, Computer Architecture, Software Engineering
- **Full-stack / Product:** Software Engineering, Databases, Algorithms, Computer Networking, Operating Systems, Programming Languages
- **Systems / Infra:** Distributed Systems, Operating Systems, Computer Architecture, Computer Networking, Algorithms, Databases
- **ML:** Machine Learning, Deep Learning, Algorithms, Linear Algebra, Probability and Statistics, Databases

---

## 4. Technical Skills Presets

Replace the master skills block with the preset matching the archetype. Render it
in the **default four-bucket layout** — the standard Jake's Resume format and the
most common on SWE resumes: one line each for **Languages / Frameworks /
Developer Tools / Libraries** (~4 lines total). Skills is the lowest-priority
section; keep every bucket to a single line. Lead each bucket with the role's
primary tools, surface JD keywords, and never list a technology not in
`master.tex`.

Bucket guide (fold any other categories into these four):
- **Languages:** programming languages.
- **Frameworks:** web/app frameworks and backend/API stacks (React, Next.js,
  Node.js, Express, Flask, FastAPI, GraphQL, gRPC, REST, ...).
- **Developer Tools:** cloud, DevOps, and infrastructure (AWS, GCP, Docker,
  Kubernetes, Linux, Git, GitHub Actions, CI/CD, Terraform, Nginx, ...).
- **Libraries:** databases, ML/data, and testing/observability (PostgreSQL,
  Redis, MongoDB, PyTorch, Pandas, scikit-learn, Pytest, ...).

LaTeX block (four rows, each one line):

```
\section{Technical Skills}
\begin{itemize}[leftmargin=0.15in, label={}]
  \small{
    \item{
      \textbf{Languages:} ... \\
      \textbf{Frameworks:} ... \\
      \textbf{Developer Tools:} ... \\
      \textbf{Libraries:} ... \\
    }
  }
\end{itemize}
```

### General SWE (default)
- **Languages:** Python, JavaScript/TypeScript, Java, C++, Go, C, Bash, SQL
- **Frameworks:** React, Next.js, Node.js, Express, Flask, FastAPI, GraphQL, gRPC, REST
- **Developer Tools:** AWS, GCP, Docker, Kubernetes, Linux, Git, GitHub Actions, CI/CD
- **Libraries:** PostgreSQL, MySQL, MongoDB, Redis, DynamoDB, PyTorch, Pandas, scikit-learn, Pytest, Jest

### Web / Product SWE
- **Languages:** TypeScript/JavaScript, Python, Go, Java, SQL, Bash
- **Frameworks:** React, Next.js, Node.js, Express, FastAPI, REST, TailwindCSS, shadcn/ui, Vite
- **Developer Tools:** AWS, GCP, Cloudflare Workers/D1/R2, Terraform, Docker, Kubernetes, Linux, Git, CI/CD
- **Libraries:** PostgreSQL, MySQL, MongoDB, Redis, Firebase, Drizzle, Kysely, Zod, TanStack Query, Playwright

### Systems / Infra
- **Languages:** C++, Go, Python, C, Rust, Bash, SQL, Java
- **Frameworks:** gRPC, Protobuf, REST, Flask, FastAPI, Kafka, RabbitMQ
- **Developer Tools:** AWS, GCP, Terraform, Docker, Kubernetes, Linux, Nginx, Git, CI/CD, Jenkins
- **Libraries:** PostgreSQL, Redis, DynamoDB, Elasticsearch, CUDA, OpenMP, pprof, OpenTelemetry, Prometheus, Grafana

### AI / ML
- **Languages:** Python, C++, Go, Java, JavaScript/TypeScript, Bash, SQL
- **Frameworks:** Flask, FastAPI, Node.js, gRPC, REST, Kafka, Celery
- **Developer Tools:** AWS, GCP, Docker, Kubernetes, Linux, Git, GitHub Actions, CI/CD
- **Libraries:** PyTorch, TensorFlow, scikit-learn, NumPy, Pandas, Hugging Face, LangChain, CUDA, PostgreSQL, Redis

---

## 5. Bullet Variant Selection

For each role/project in `master.tex`:

- Variants are labeled `%% VARIANT A/B/C` with a one-line note on when each fits.
  Choose the variant called out by the archetype; if the archetype offers a
  choice (e.g. "Variant A or C"), pick the one whose technologies overlap most
  with the JD's required skills.
- `%% EXTRA bullets to mix and match` are optional swaps. Use them to surface a
  JD keyword that the chosen variant omits, but never exceed the bullet count in
  directive 10, and never mix bullets that duplicate the same achievement.
- The active (uncommented) variant in `master.tex` is the default; uncomment a
  different variant and re-comment the default when the archetype calls for it.

---

## 6. Formatting Conventions

- One page, strict. `pdflatex`-compatible.
- No em dashes. No contractions. Formal tone. Past tense for completed work;
  "Incoming" only for the Everpure entry.
- Quantify with the metrics already in `master.tex`; do not round or invent.
- If the page overflows, trim in this order (experience is protected until the
  very end): (1) EXTRA bullets, (2) clubs line, (3) coursework, (4) trim the
  longest Skills row (Libraries or Developer Tools), (5) a project's bullets,
  (6) the least-relevant project entirely, (7) only as a last resort, a single
  bullet from the least-relevant experience. Do **not** shrink font size or
  margins below the template defaults.

---

## 7. One-Page Content Budget

Use this to size the resume correctly on the FIRST compile so the trim-and-recompile
loop stays short. Build to this budget, then verify with `scripts/compile.sh`
(page count) and `scripts/overflow.sh` (shows what spilled, as text). These
figures assume the Jake's Resume template defaults in `master.tex`.

- **Baseline that fits one page:** 4 experiences + 2 projects + a 5-row Skills
  block + Education (coursework line; clubs optional).
- **The MS Education entry costs roughly one project's worth of height.** When it
  is included, plan for **4 experiences + 2 projects** and drop the clubs line.
  When it is omitted, you have room for a 3rd project or the clubs line.
- **Skills uses the four-bucket layout by default (~4 lines):** Languages,
  Frameworks, Developer Tools, Libraries (§4). Keep each row to one line (roughly
  <= 110 characters); if a row wraps it costs a full line, so trim its longest
  list first (Libraries and Developer Tools are the usual offenders).
- **Long, metric-dense bullets wrap to two printed lines.** Budget for this in
  ML/research/distributed-systems bullets; three long bullets can equal five
  short ones in height.
- **Experience is funded first** (directive 10). If the budget is tight, the
  adjustments come from Projects/Skills/coursework/clubs, not from cutting
  experience bullets.
- **Do not read a rendered image to check fit.** Trust `compile.sh` (Pages line +
  overfull warnings), `scripts/overflow.sh` (page-2 text), and
  `scripts/lint-output.sh`. Only render an image if the layout looks structurally
  wrong after those pass.

### Fill the full page (experience-first)

A one-page resume should FILL the page: content should reach the bottom margin
with no large empty band. An under-full page wastes the candidate's strongest
real estate. Aim for full but not overflowing.

Get there token-efficiently by converging from ABOVE, not below:

1. **Build deliberately rich.** Max out experience bullets (up to 4-5 on the most
   relevant and recent roles, using their variant + EXTRA bullets) and include
   enough projects so the FIRST compile is at or slightly over one page.
2. **If it overflows, trim down** with `scripts/overflow.sh` per the §6 order
   until it just fits. Trimming from slightly-over lands a full page
   automatically, and overflow.sh shows what to cut as text (no image read).
3. **If it compiles to one page with obvious empty space, add the next bullet**
   and recompile. Repeat until adding one more would overflow.

When filling (step 3), add in this priority — the mirror of the trim order:
- First, more **EXPERIENCE** bullets: restore a variant/EXTRA bullet on an
  already-included experience, or add a relevant 4th experience.
- Then a project bullet, or an additional relevant project.
- Coursework, clubs, and Skills rows are last — they pad, they do not sell.

Fill ONLY with real content from `master.tex` (other variant bullets, EXTRA
bullets, or another genuine entry). Never invent or pad with filler.
