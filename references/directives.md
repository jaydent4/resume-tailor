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
3. **Limit scope to keep one page:** 3–4 experiences and 2–3 projects. Cut the
   least relevant entries first.
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
8. **Use the Technical Skills preset that matches the archetype** (§4), trimming
   categories that do not apply to the role.
9. **Use the coursework preset that matches the archetype** (§3).
10. **Emphasize experience over projects:** aim for 3 bullets on the most
    relevant experiences and 2 bullets on projects or less-related experiences.
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

Replace the master skills block with the preset matching the archetype. Each
preset leads with the role's primary languages and trims unrelated stacks.

### General SWE (default)
- **Languages:** Python, JavaScript/TypeScript, Java, C++, Go, C, Bash, SQL
- **Cloud & DevOps:** AWS, GCP, Docker, Kubernetes, Linux, Git, GitHub Actions, CI/CD
- **Backend / APIs:** Node.js, Express, Flask, FastAPI, GraphQL, gRPC, REST
- **Databases:** PostgreSQL, MySQL, MongoDB, Redis, Firebase, DynamoDB, SQLite
- **Frontend:** React, Next.js, TypeScript, TailwindCSS, HTML, CSS
- **ML / Data:** PyTorch, TensorFlow, NumPy, Pandas, scikit-learn
- **Testing / Observability:** Jest, Pytest, Playwright, Selenium, OpenTelemetry

### Web / Product SWE
- **Languages:** TypeScript/JavaScript, Python, Go, Java, SQL, Bash
- **Frontend:** React, Next.js, TailwindCSS, shadcn/ui, Vite, HTML, CSS
- **Backend / APIs:** Node.js, Express, Flask, FastAPI, GraphQL, gRPC, REST
- **Cloud & DevOps:** AWS, GCP, Cloudflare Workers/D1/R2, Terraform, Docker, Kubernetes, Linux, Git, GitHub Actions, CI/CD
- **Databases:** PostgreSQL, MySQL, MongoDB, Redis, Firebase, SQLite
- **Libraries:** BetterAuth, NextAuth, Kysely, Drizzle, Zod, SWR, TanStack Query
- **Testing:** Jest, Pytest, Playwright, Selenium

### Systems / Infra
- **Languages:** C++, Go, Python, C, Rust, Bash, SQL, Java
- **Systems & HPC:** CUDA, OpenMP, Linux, Docker, Kubernetes, Nginx
- **Cloud:** AWS (Lambda, DynamoDB, S3, EC2), GCP, Terraform, Cloudflare Workers
- **Backend / APIs:** gRPC, Protobuf, Kafka, RabbitMQ, Flask, FastAPI, REST
- **Databases:** PostgreSQL, MySQL, Redis, DynamoDB, SQLite, Elasticsearch
- **Observability:** pprof, OpenTelemetry, Prometheus, Grafana
- **Tools:** Git, GitHub Actions, CI/CD, Jenkins

### AI / ML
- **Languages:** Python, C++, Go, Java, JavaScript/TypeScript, Bash, SQL
- **ML / Data:** PyTorch, TensorFlow, scikit-learn, NumPy, Pandas, Hugging Face, RAG, LangChain, Optuna, Weights and Biases, ONNX, CUDA
- **Cloud & DevOps:** AWS, GCP, Docker, Kubernetes, Linux, Git, GitHub Actions, CI/CD
- **Backend / APIs:** Node.js, Flask, FastAPI, gRPC, REST, Kafka, Celery
- **Databases:** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch

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
- If the page overflows, trim in this order: EXTRA bullets, then coursework and
  clubs, then skills categories, then a least-relevant project. Do **not** shrink
  font size or margins below the template defaults.
