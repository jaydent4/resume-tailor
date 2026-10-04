#!/usr/bin/env python3
"""Application tracker + company gate for the auto-apply workflow.

    python3 scripts/track.py check "<Company>" [--url URL] [--job-id ID] [--title "Role title"]
    python3 scripts/track.py import-prior   # record roles from jds/ applied to before auto-apply as PRIOR
    python3 scripts/track.py import-sheet   # record every Company + Position in the Google Sheet as PRIOR
    python3 scripts/track.py add --company C --role R --url U --status S [--job-id ID] [--resume P] [--doc P] [--note N]
    python3 scripts/track.py status <url-or-job-id> <STATUS> [--note N]
    python3 scripts/track.py list [--status STATUS[,STATUS]]
    python3 scripts/track.py summary     # rebuild applications/summary.md
    python3 scripts/track.py sync        # push the tracker to Google Sheets now (also automatic on every write)

`check` exit codes (run it BEFORE opening a tab for any posting):
    0   CLEAR          auto-apply allowed
    10  BLACKLIST      company is on the blacklist: tailor the resume, record RESUME_READY, never fill or submit
    11  SKIP           company is on skip_companies: never apply, do not prepare anything
    12  DUPLICATE      this exact posting (url or job id) is already in the tracker
    13  COMPANY CAP    run.max_applications_per_company_lifetime reached for this company

Statuses: SUBMITTED, RESUME_READY (blacklisted: resume tailored, not applied yet), NEEDS_SIGN_IN (account
portal such as Workday: resume ready, waiting for the user to sign in; note = host), AWAITING_REVIEW
(confirm mode: filled but not sent), NEEDS_HUMAN (blocked on something only the user can do),
SKIPPED (ineligible / not a fit), FAILED.

The tracker lives in applications/tracker.tsv (gitignored); every write also regenerates
applications/summary.md (company, role, status, resume path). Lists come from config/apply.json.
"""
import csv, datetime, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.environ.get('APPLY_CONFIG') or os.path.join(R, 'config', 'apply.json')
TRACKER = os.path.join(R, 'applications', 'tracker.tsv')
SUMMARY = os.path.join(R, 'applications', 'summary.md')
COLS = ['date', 'company', 'role', 'job_id', 'url', 'status', 'resume', 'doc', 'note']
STATUSES = {'SUBMITTED', 'PRIOR', 'RESUME_READY', 'NEEDS_SIGN_IN', 'AWAITING_REVIEW', 'NEEDS_HUMAN', 'SKIPPED', 'FAILED'}
# Statuses that count as "an application exists" for the duplicate and per-company cap checks.
COUNTED = {'SUBMITTED', 'RESUME_READY', 'NEEDS_SIGN_IN', 'AWAITING_REVIEW', 'NEEDS_HUMAN'}
# PRIOR = applied before auto-apply existed (imported from jds/). It blocks the same role, but does not count
# toward the per-company cap: those were hand-picked roles, often several per company.
MEANING = {'SUBMITTED': 'applied', 'PRIOR': 'applied before auto-apply (imported)', 'RESUME_READY': 'blacklisted: resume ready, not applied yet',
           'AWAITING_REVIEW': 'form filled, waiting for your approval',
           'NEEDS_SIGN_IN': 'resume ready; sign in to the portal (see note) to apply', 'NEEDS_HUMAN': 'blocked: needs you',
           'SKIPPED': 'not applying', 'FAILED': 'failed'}

CLEAR, BLACKLIST, SKIP, DUPLICATE, CAP = 0, 10, 11, 12, 13


def load_config():
    if not os.path.exists(CONFIG):
        sys.exit(f'missing {os.path.relpath(CONFIG, R)}: copy config/apply.example.json and fill it in')
    return json.load(open(CONFIG))


def norm(s):
    """Lowercase alphanumerics only, minus common legal suffixes: 'Jane Street Capital, LLC' -> 'janestreetcapital'."""
    s = re.sub(r'[^a-z0-9]', '', (s or '').lower())
    return re.sub(r'(incorporated|inc|llc|ltd|corp|corporation|co)$', '', s) or s


def entry_names(entry):
    """A list entry is either "Company" or {"company": "...", "aliases": [...], "reason": "...", "exact": bool}."""
    if isinstance(entry, str):
        return [entry], '', False
    return [entry.get('company', '')] + list(entry.get('aliases') or []), entry.get('reason', ''), bool(entry.get('exact'))


def match_list(company, entries):
    """Return (matched_name, reason) if company matches any entry. Prefix matches count (min 4 chars), so
    'Citadel' also catches 'Citadel Securities'; entries with "exact": true match only their names. False positives here only ever make the workflow MORE careful."""
    n = norm(company)
    for e in entries or []:
        names, reason, exact = entry_names(e)  # exact: no prefix matching ("Meta" must not catch "Metabase")
        for name in names:
            b = norm(name)
            if not b or not n:
                continue
            if n == b or (not exact and ((len(b) >= 4 and n.startswith(b)) or (len(n) >= 4 and b.startswith(n)))):
                return name, reason
    return None


def read_rows():
    if not os.path.exists(TRACKER):
        return []
    with open(TRACKER, newline='') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def write_rows(rows):
    os.makedirs(os.path.dirname(TRACKER), exist_ok=True)
    with open(TRACKER, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=COLS, delimiter='\t', extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    write_summary(rows)
    sync_sheet(rows)


def sheet_payload(rows, sheets):
    """Submitted applications for the user's cycle tabs (append-only on the sheet side) and the script-owned
    pipeline tab (everything except PRIOR)."""
    tabs = sheets.get('tabs') or {}
    submitted, pipeline = [], [['Date', 'Company', 'Role', 'Status', 'Meaning', 'Resume', 'Link', 'Note']]
    for r in sorted(rows, key=lambda r: r['date']):
        if r['status'] == 'PRIOR':
            continue
        if r['status'] == 'SUBMITTED':
            kind = role_kind(r['role'] + ' ' + r['note'])
            tab = tabs.get('offseason_intern') if kind.startswith('intern') else tabs.get('new_grad')
            if tab:
                submitted.append({'tab': tab, 'company': r['company'], 'position': r['role'], 'date': r['date']})
        pipeline.append([r['date'], r['company'], r['role'], r['status'], MEANING.get(r['status'], ''), r['resume'],
                         r['url'] if r['url'].startswith('http') else '', r['note']])
    pipeline[1:] = sorted(pipeline[1:], key=lambda x: x[0], reverse=True)
    return {'action': 'sync', 'submitted': submitted, 'pipeline_tab': sheets.get('pipeline_tab') or 'Auto-apply',
            'pipeline': pipeline, 'template_tab': sheets.get('template_tab', '')}


def sheet_call(payload, verbose=False):
    """POST to the user's Apps Script web app. Returns the parsed reply, or None (never raises)."""
    try:
        sheets = (load_config().get('sheets') or {})
    except SystemExit:
        return None
    url = sheets.get('webhook_url', '')
    if not url:
        if verbose:
            print('sheets.webhook_url is not set in config/apply.json; skipping', file=sys.stderr)
        return None
    import ssl, urllib.request
    try:
        try:
            import certifi
            ctx = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            ctx = ssl.create_default_context(cafile='/etc/ssl/cert.pem') if os.path.exists('/etc/ssl/cert.pem') else None
        req = urllib.request.Request(url, data=json.dumps({'token': sheets.get('token', ''), **payload}).encode(),
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            out = json.loads(resp.read().decode('utf-8', 'ignore') or '{}')
        if verbose or not out.get('ok'):
            print(f'sheet: {json.dumps(out)[:200]}', file=sys.stderr)
        return out if out.get('ok') else None
    except Exception as e:
        print(f'sheet call failed ({type(e).__name__}: {e}); tracker.tsv is unaffected', file=sys.stderr)
        return None


def sync_sheet(rows, verbose=False):
    """Mirror the tracker to Google Sheets (config: sheets.*). Never raises; tracker.tsv stays the source of truth."""
    try:
        sheets = (load_config().get('sheets') or {})
    except SystemExit:
        return False
    if not sheets.get('webhook_url'):
        if verbose:
            print('sheets.webhook_url is not set in config/apply.json; skipping sync', file=sys.stderr)
        return False
    return sheet_call(sheet_payload(rows, sheets), verbose) is not None


def import_sheet():
    """Record every Company + Position already in the user's sheet as PRIOR, so it is never applied to again."""
    sheets = (load_config().get('sheets') or {})
    out = sheet_call({'action': 'read', 'pipeline_tab': sheets.get('pipeline_tab') or 'Auto-apply'})
    if out is None:
        return 1
    rows = read_rows()
    have = {r['url'] for r in rows}
    mine = {(norm(r['company']), r['role'].strip().lower()) for r in rows if r['status'] != 'PRIOR'}
    added = 0
    for x in out.get('rows', []):
        if 'auto-apply' in x.get('notes', '').lower() or (norm(x['company']), x['position'].lower()) in mine:
            continue  # written by auto-apply itself
        key = f'sheet:{x["tab"]}:{x["company"]}:{x["position"]}'
        if key in have:
            continue
        tab = x['tab'].lower()
        kind = 'newgrad' if 'grad' in tab else 'intern-summer' if 'summer' in tab else \
            'intern-offseason' if re.search(r'off[ -]?(season|cycle)|winter|spring|fall', tab) else role_kind(x['position'])
        rows.append({'date': x.get('date') or datetime.date.today().isoformat(), 'company': x['company'],
                     'role': x['position'] or 'Unknown role', 'job_id': '', 'url': key, 'status': 'PRIOR',
                     'resume': '', 'doc': '', 'note': f'{kind}; sheet tab {x["tab"]}; {x.get("status", "")}'.strip('; ')})
        have.add(key)
        added += 1
    write_rows(rows)
    print(f'imported {added} application(s) from the Google Sheet as PRIOR')
    return 0


def write_summary(rows):
    """Human-readable view of the tracker, newest first. Regenerated on every write; never edit by hand."""
    cell = lambda v: (v or '').replace('|', '/').strip() or '-'
    counts = {}
    for r in rows:
        counts[r['status']] = counts.get(r['status'], 0) + 1
    lines = ['# Applications', '',
             'Generated by `scripts/track.py` from `applications/tracker.tsv`. Do not edit by hand.', '',
             ' · '.join(f'{k}: {v}' for k, v in sorted(counts.items())) or 'No applications yet.', '',
             '| Date | Company | Role | Status | Resume | Note |', '|---|---|---|---|---|---|']
    for r in sorted(rows, key=lambda r: r['date'], reverse=True):
        status = f'{r["status"]} ({MEANING.get(r["status"], "")})'
        lines.append('| ' + ' | '.join(cell(x) for x in (r['date'], r['company'], r['role'], status,
                                                           f'`{r["resume"]}`' if r['resume'] else '', r['note'])) + ' |')
    with open(SUMMARY, 'w') as f:
        f.write('\n'.join(lines) + '\n')


def clean_url(u):
    u = re.sub(r'[?&](utm_[^&]+|gh_src=[^&]+|lever-source[^&]*|ref=[^&]+|source=[^&]+)', '', u or '')
    return u.rstrip('?&/').lower().removesuffix('/application').removesuffix('/apply')


KIND_WORDS = {'new', 'grad', 'graduate', 'graduates', 'university', 'early', 'career', 'entry', 'level', 'intern',
              'internship', 'co', 'op', 'coop', 'junior', 'associate', 'i', '1', 'the', 'and', 'of', 'for', 'a', 'in',
              'winter', 'spring', 'summer', 'fall', 'autumn', 'program', 'emerging', 'professionals', 'campus'}


def role_kind(text):
    t = text.lower()
    if re.search(r'\bintern(ship)?s?\b|\bco-?op\b', t):
        m = re.search(r'\b(winter|spring|summer|fall)\b', t)
        if not m and re.search(r'off[ -]?(season|cycle)', t):
            return 'intern-offseason'
        return 'intern-' + (m.group(1) if m else '?')
    if re.search(r'new[ -]?grad|university grad|college grad|early[ -]career|entry[ -]level|recent grad|graduat', t):
        return 'newgrad'
    return 'fulltime'


def core_tokens(title):
    t = title.lower().replace('software development engineer', 'software engineer')
    t = re.sub(r'\b(swe|sde)\b', 'software engineer', t)
    t = re.sub(r'\bengineering\b|\bdeveloper\b', 'engineer', t)
    return {w for w in re.findall(r'[a-z0-9+#]+', t) if w not in KIND_WORDS and not re.fullmatch(r'20\d\d', w)}


def same_role(title, prior_title, prior_note=''):
    """Same kind of role (new grad / intern+season / full-time) and mostly the same title words."""
    if not title or not prior_title:
        return False
    k1, k2 = role_kind(title), role_kind(prior_title + ' ' + prior_note)
    offseason = {'intern-offseason', 'intern-winter', 'intern-spring', 'intern-fall'}
    if k1 != k2 and not ({k1, k2} <= {'newgrad', 'fulltime'}) and not ('intern-offseason' in (k1, k2) and {k1, k2} <= offseason):
        return False
    a, b = core_tokens(title), core_tokens(prior_title)
    return bool(a and b) and len(a & b) / len(a | b) >= 0.6


def gate(company, url='', job_id='', cfg=None, rows=None, title=''):
    """Return (code, message). Order matters: skip > duplicate > cap > blacklist > clear."""
    cfg = cfg if cfg is not None else load_config()
    rows = rows if rows is not None else read_rows()
    m = match_list(company, cfg.get('skip_companies'))
    if m:
        return SKIP, f'SKIP: "{company}" matches skip_companies entry "{m[0]}"' + (f' ({m[1]})' if m[1] else '')
    cu, jid = clean_url(url), str(job_id or '').strip()
    for r in rows:
        if r['status'] not in COUNTED:
            continue
        if (cu and clean_url(r['url']) == cu) or (jid and r['job_id'] == jid and norm(r['company']) == norm(company)):
            return DUPLICATE, f'DUPLICATE: already {r["status"]} on {r["date"]}: {r["company"]} / {r["role"]} ({r["url"]})'
    priors = [r for r in rows if r['status'] == 'PRIOR' and match_list(company, [r['company']])]
    for r in priors:
        if same_role(title, r['role'], r.get('note', '')):
            return DUPLICATE, f'DUPLICATE: matches a prior application: {r["company"]} / {r["role"]} ({r["url"]})'
    cap = int((cfg.get('run') or {}).get('max_applications_per_company_lifetime') or 0)
    prior = [r for r in rows if r['status'] in COUNTED and norm(r['company']) == norm(company)]
    if cap and len(prior) >= cap:
        roles = '; '.join(f'{r["role"]} ({r["status"]} {r["date"]})' for r in prior)
        return CAP, f'COMPANY CAP: {len(prior)} of {cap} applications already at {company}: {roles}'
    m = match_list(company, cfg.get('blacklist'))
    if m:
        earlier = ('. Earlier roles here: ' + '; '.join(r['role'] for r in priors[:8])) if priors else ''
        return BLACKLIST, (f'BLACKLIST: "{company}" matches blacklist entry "{m[0]}"' + (f' ({m[1]})' if m[1] else '') + earlier
                           + '. Tailor the resume and record RESUME_READY; do not fill or submit until the user approves.')
    note = f' ({len(prior)} prior application(s) at this company)' if prior else ''
    if priors:
        note += ('. Earlier roles here (confirm this posting is a DIFFERENT role): '
                 + '; '.join(r['role'] for r in priors[:8]) + (f' (+{len(priors) - 8} more)' if len(priors) > 8 else ''))
    return CLEAR, f'CLEAR: auto-apply allowed for "{company}"{note}'


# jds/ file prefixes -> company names come from config/apply.json `prior_company_aliases` (personal, gitignored),
# e.g. {"hrt": "Hudson River Trading", "oai": "OpenAI"}. Unmapped prefixes are title-cased ("stripe" -> "Stripe").
ROLE_WORDS = {'swe': 'Software Engineer', 'sys': 'Systems', 'eng': 'Engineer', 'ng': 'New Grad', 'qsd': 'Quant Software Developer',
              'mle': 'Machine Learning Engineer', 'dev': 'Developer', 'ui': 'UI', 'ai': 'AI', 'av': 'AV', 'iap': 'IAP'}


def import_prior():
    """Add every jds/*.txt written before auto-apply (no 'Company:' header) as a PRIOR row. Re-runnable."""
    import glob
    aliases = (load_config().get('prior_company_aliases') or {})
    rows = read_rows()
    have = {r['url'] for r in rows}
    added = 0
    for path in sorted(glob.glob(os.path.join(R, 'jds', '*.txt'))):
        rel = os.path.relpath(path, R)
        text = open(path, errors='ignore').read()
        if text.startswith('Company:') or f'prior:{rel}' in have:
            continue  # written by auto-apply itself, or already imported
        stem = os.path.basename(path)[:-4]
        key = max((k for k in aliases if stem == k or stem.startswith(k + '_')), key=len, default='')
        company = aliases[key] if key else stem.split('_')[0].title()
        rest = stem[len(key) + 1:] if key else '_'.join(stem.split('_')[1:])
        first = next((l.strip() for l in text.splitlines() if l.strip()), '')
        if len(first) < 90 and re.search(r'engineer|developer|intern|software|quant|analyst|scientist|swe', first, re.I) \
                and not first.lower().startswith('about'):
            title = first
        else:
            title = ' '.join(ROLE_WORDS.get(w, w.title()) for w in rest.split('_') if w) or 'Unknown role'
        kind_hint = role_kind(title + ' ' + stem.replace('_', ' ') + ' ' + text[:2500])
        pdfs = sorted(glob.glob(os.path.join(R, 'output', f'*_resume_{stem}.pdf')) + glob.glob(os.path.join(R, 'output', f'{stem}.pdf')))
        date = datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()
        rows.append({'date': date, 'company': company, 'role': title, 'job_id': '', 'url': f'prior:{rel}', 'status': 'PRIOR',
                     'resume': os.path.relpath(pdfs[0], R) if pdfs else '', 'doc': '', 'note': kind_hint})
        added += 1
    write_rows(rows)
    print(f'imported {added} prior role(s) from jds/ as PRIOR')
    return 0


def arg(args, flag, default=''):
    return args[args.index(flag) + 1] if flag in args and args.index(flag) + 1 < len(args) else default


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
        return 0
    cmd = a[0]
    if cmd == 'check':
        if len(a) < 2:
            sys.exit('usage: track.py check "<Company>" [--url URL] [--job-id ID]')
        code, msg = gate(a[1], arg(a, '--url'), arg(a, '--job-id'), title=arg(a, '--title'))
        print(msg)
        return code
    if cmd == 'add':
        status = arg(a, '--status').upper()
        if status not in STATUSES:
            sys.exit(f'--status must be one of {sorted(STATUSES)}')
        row = {'date': datetime.date.today().isoformat(), 'company': arg(a, '--company'), 'role': arg(a, '--role'),
               'job_id': arg(a, '--job-id'), 'url': arg(a, '--url'), 'status': status,
               'resume': arg(a, '--resume'), 'doc': arg(a, '--doc'), 'note': arg(a, '--note')}
        if not row['company'] or not row['url']:
            sys.exit('add needs at least --company and --url')
        rows = read_rows()
        cu = clean_url(row['url'])
        for r in rows:  # re-adding the same posting updates it instead of duplicating it
            if clean_url(r['url']) == cu:
                r.update({k: v for k, v in row.items() if v})
                write_rows(rows)
                print(f'updated: {r["company"]} / {r["role"]} -> {r["status"]}')
                return 0
        rows.append(row)
        write_rows(rows)
        print(f'added: {row["company"]} / {row["role"]} -> {status}')
        return 0
    if cmd == 'status':
        if len(a) < 3 or a[2].upper() not in STATUSES:
            sys.exit(f'usage: track.py status <url-or-job-id> <{"|".join(sorted(STATUSES))}> [--note N]')
        key, status, note = a[1], a[2].upper(), arg(a, '--note')
        rows = read_rows()
        bare = '/' not in key and len(key) >= 3  # a job id, which may also only live inside the url
        hits = [r for r in rows if clean_url(r['url']) == clean_url(key) or (r['job_id'] and r['job_id'] == key)
                or (bare and re.search(r'[/=]' + re.escape(key) + r'(\b|$)', r['url']))]
        if len(hits) != 1:
            sys.exit(f'{len(hits)} rows match "{key}"; pass the full url')
        hits[0]['status'] = status
        hits[0]['date'] = datetime.date.today().isoformat()
        if note:
            hits[0]['note'] = note
        write_rows(rows)
        print(f'{hits[0]["company"]} / {hits[0]["role"]} -> {status}')
        return 0
    if cmd == 'import-prior':
        return import_prior()
    if cmd == 'import-sheet':
        return import_sheet()
    if cmd == 'sync':
        return 0 if sync_sheet(read_rows(), verbose=True) else 1
    if cmd == 'summary':
        write_summary(read_rows())
        print(os.path.relpath(SUMMARY, R))
        return 0
    if cmd == 'list':
        want = {x for x in arg(a, '--status').upper().split(',') if x}
        rows = [r for r in read_rows() if not want or r['status'] in want]
        for r in rows:
            print('\t'.join(r.get(c, '') for c in ('date', 'status', 'company', 'role', 'url', 'doc', 'note')))
        print(f'({len(rows)} row(s))', file=sys.stderr)
        return 0
    sys.exit(f'unknown command {cmd!r}; see --help')


if __name__ == '__main__':
    sys.exit(main())
