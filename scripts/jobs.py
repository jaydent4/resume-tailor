#!/usr/bin/env python3
"""Find job postings on the sources in config/apply.json and pull their descriptions into jds/.

    python3 scripts/jobs.py sweep [--source stripe] [--limit 40|--all]  # -> state/candidates.json + compact rows
    python3 scripts/jobs.py screen <id>     # eligibility flags with short context, instead of reading the whole JD
    python3 scripts/jobs.py jd <id|url> [--name stripe_swe_intern]      # write jds/<name>.txt (boilerplate stripped)

Source types (config/apply.json -> sources[]):
    greenhouse  {"type": "greenhouse", "slug": "stripe", "company": "Stripe"}
    lever       {"type": "lever", "slug": "palantir", "company": "Palantir"}
    ashby       {"type": "ashby", "slug": "notion", "company": "Notion"}
    simplify    {"type": "simplify", "repo": "SimplifyJobs/Summer2027-Internships"}   (GitHub listings.json feed)
    browse      {"type": "browse", "url": "https://...", "company": "..."}            (no API: the agent visits
                                                                                        it in the browser)

Every candidate is filtered by filters.* (title, location, age) and annotated with the company gate from
scripts/track.py: SKIP and DUPLICATE/CAP rows are dropped, BLACKLIST rows are kept and marked so the agent
never submits them unattended. Descriptions are screened for eligibility flags (years, clearance, citizenship,
degree, grad year); a years minimum >= filters.max_years_experience + 2 is dropped outright. Stdout is kept
compact on purpose (no URLs, no descriptions): everything else is in state/candidates.json, keyed by id.
Run in the FOREGROUND; it stops itself after DEADLINE seconds.
"""
import concurrent.futures as cf, datetime, html, json, os, re, ssl, sys, time, urllib.error, urllib.request
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import track  # noqa: E402

R = track.R
OUT = os.path.join(R, 'state', 'candidates.json')
JDS = os.path.join(R, 'jds')
DEADLINE = 240
UTC = datetime.timezone.utc
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36'


def _ctx():
    """A verifying SSL context that also works with a python.org python that never ran Install Certificates."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        pass
    if os.path.exists('/etc/ssl/cert.pem'):
        return ssl.create_default_context(cafile='/etc/ssl/cert.pem')
    return ssl.create_default_context()


CTX = _ctx()
ERRORS = {}


def get(url, tag=''):
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            ERRORS[f'{tag} HTTP{e.code}'] = ERRORS.get(f'{tag} HTTP{e.code}', 0) + 1
            if e.code != 429 or attempt == 2:
                return None
            time.sleep(3)
        except Exception as e:
            ERRORS[f'{tag} {type(e).__name__}'] = ERRORS.get(f'{tag} {type(e).__name__}', 0) + 1
            if attempt == 2:
                return None
            time.sleep(1)


class _Text(HTMLParser):
    """HTML -> readable plain text: paragraphs and list items on their own lines."""
    BLOCK = {'p', 'div', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'tr', 'section'}

    def __init__(self):
        super().__init__()
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag == 'li':
            self.out.append('\n- ')
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in self.BLOCK:
            self.out.append('\n')

    def handle_data(self, d):
        self.out.append(d)


def html_to_text(s):
    p = _Text()
    p.feed(html.unescape(s or ''))  # Greenhouse double-escapes its content
    t = re.sub(r'[ \t\xa0]+', ' ', ''.join(p.out))
    return re.sub(r'\n\s*\n\s*\n+', '\n\n', t).strip()


def ts(s):
    try:
        d = datetime.datetime.fromisoformat(str(s).replace('Z', '+00:00'))
        return d if d.tzinfo else d.replace(tzinfo=UTC)
    except Exception:
        return None


# ---------- per-source fetchers: each returns a list of candidate dicts ----------

def cand(source, company, title, location, url, apply_url, posted, job_id='', ats='', slug='', desc='', extra=''):
    return {'source': source, 'company': company, 'title': title.strip(), 'location': location, 'url': url,
            'apply_url': apply_url or url, 'posted': posted.isoformat()[:10] if posted else '', 'job_id': str(job_id),
            'ats': ats, 'slug': slug, 'description': desc, 'extra': extra}


def fetch_greenhouse(s):
    slug = s['slug']
    d = get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true', 'greenhouse')
    out = []
    for j in (d or {}).get('jobs', []):
        jid = j.get('id')
        out.append(cand(slug, s.get('company') or j.get('company_name') or slug, j.get('title', ''),
                        (j.get('location') or {}).get('name', ''), j.get('absolute_url', ''),
                        f'https://job-boards.greenhouse.io/{slug}/jobs/{jid}', ts(j.get('first_published') or j.get('updated_at')),
                        jid, 'greenhouse', slug, html_to_text(j.get('content', ''))))
    return out


def fetch_lever(s):
    slug = s['slug']
    d = get(f'https://api.lever.co/v0/postings/{slug}?mode=json', 'lever')
    out = []
    for j in d or []:
        c = j.get('categories') or {}
        loc = ' | '.join(x for x in [c.get('location') or ''] + (c.get('allLocations') or []) if x)
        desc = (j.get('descriptionPlain') or '') + '\n\n' + '\n\n'.join(
            f"{x.get('text', '')}\n{html_to_text(x.get('content', ''))}" for x in j.get('lists') or []) + '\n\n' + (j.get('additionalPlain') or '')
        posted = datetime.datetime.fromtimestamp((j.get('createdAt') or 0) / 1000, UTC)
        sr = j.get('salaryRange') or {}
        comp = f"{sr.get('currency', '')} {sr.get('min')}-{sr.get('max')} {sr.get('interval', '')}".strip() if sr else ''
        out.append(cand(slug, s.get('company') or slug, j.get('text', ''), loc, j.get('hostedUrl', ''),
                        j.get('applyUrl', ''), posted, j.get('id', ''), 'lever', slug, desc.strip(), comp))
    return out


def fetch_ashby(s):
    slug = s['slug']
    d = get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true', 'ashby')
    out = []
    for j in (d or {}).get('jobs', []):
        if not j.get('isListed', True):
            continue
        loc = ' | '.join(x for x in [j.get('location') or ''] + [x.get('location', '') for x in j.get('secondaryLocations') or []] if x)
        if j.get('isRemote'):
            loc += ' | Remote'
        comp = (j.get('compensation') or {}).get('compensationTierSummary') or ''
        url = j.get('jobUrl', '')
        out.append(cand(slug, s.get('company') or slug, j.get('title', ''), loc, url, j.get('applyUrl') or (url + '/application'),
                        ts(j.get('publishedAt')), j.get('id', ''), 'ashby', slug, j.get('descriptionPlain') or '', comp))
    return out


ATS_URL = [
    ('greenhouse', re.compile(r'(?:job-boards|boards)(?:\.eu)?\.greenhouse\.io/(?:embed/job_app\?for=)?([A-Za-z0-9_-]+)(?:/jobs/|&token=)(\d+)')),
    ('lever', re.compile(r'jobs\.lever\.co/([A-Za-z0-9._-]+)/([0-9a-f-]{36})')),
    ('ashby', re.compile(r'jobs\.ashbyhq\.com/([A-Za-z0-9._%-]+)/([0-9a-f-]{36})')),
    ('greenhouse', re.compile(r'()[?&]gh_jid=(\d+)')),  # Greenhouse embedded on a company site; slug unknown
]


def parse_ats(url):
    for ats, rx in ATS_URL:
        m = rx.search(url or '')
        if m:
            return ats, m.group(1), m.group(2)
    return '', '', ''


def fetch_simplify(s):
    repo = s['repo']
    d = get(f'https://raw.githubusercontent.com/{repo}/{s.get("branch", "dev")}/.github/scripts/listings.json', 'simplify')
    out = []
    for x in d or []:
        if not x.get('active') or not x.get('is_visible', True):
            continue
        url = re.sub(r'[?&](utm_[^&]+|ref=[^&]+)', '', x.get('url', '')).rstrip('?&')
        ats, slug, jid = parse_ats(url)
        posted = datetime.datetime.fromtimestamp(x.get('date_posted') or 0, UTC)
        extra = '; '.join(v for v in [x.get('sponsorship', '') if x.get('sponsorship') != 'Other' else '',
                                      ', '.join(x.get('terms') or [])] if v)
        c = cand(s.get('label') or repo, x.get('company_name', ''), x.get('title', ''), '; '.join(x.get('locations') or []),
                 url, url, posted, jid, ats, slug, '', extra)
        c['category'] = x.get('category') or ''
        c['feed_kind'] = s.get('kind') or ('new_grad' if 'new-grad' in repo.lower() or 'newgrad' in repo.lower() else '')
        out.append(c)
    return out


FETCH = {'greenhouse': fetch_greenhouse, 'lever': fetch_lever, 'ashby': fetch_ashby, 'simplify': fetch_simplify}


# ---------- filters ----------

def compile_any(words):
    """Plain entries match as whole words, case-insensitive; an entry starting with "re:" is a raw regex."""
    words = [w for w in words or [] if w]
    if not words:
        return None
    return re.compile('|'.join(w[3:] if w.startswith('re:') else r'\b' + re.escape(w) + r'\b' for w in words), re.I)


US_STATES = ('Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|'
             'Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|'
             'Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|'
             'Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|'
             'West Virginia|Wisconsin|Wyoming|District of Columbia')
US_RX = re.compile(r'united states|\bu\.?s\.?a?\b|\bamericas?\b|\bnyc\b|\bsf\b|bay area|silicon valley|\b(?:' + US_STATES + r')\b'
                   r'|,\s*(?-i:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY|DC)\b'
                   r'|san francisco|los angeles|seattle|chicago|boston|austin|denver|atlanta|miami|palo alto|mountain view|menlo park'
                   r'|sunnyvale|san jose|santa clara|redwood city|cupertino|san mateo|oakland|berkeley|redmond|bellevue|kirkland'
                   r'|brooklyn|manhattan|jersey city|pittsburgh|philadelphia|san diego|irvine|costa mesa|hawthorne|el segundo'
                   r'|santa monica|culver city|portland|salt lake|raleigh|durham|nashville|dallas|houston|phoenix|minneapolis', re.I)
NON_US_RX = re.compile(r'canada|toronto|vancouver|montr[eé]al|waterloo|ottawa|calgary|edmonton|ontario|british columbia|qu[eé]bec'
                       r'|alberta|kitchener|winnipeg|halifax|,\s*(?-i:ON|BC|QC|AB|MB|NS)\b|mexico|brazil|london|united kingdom|\buk\b'
                       r'|europe|emea|apac|latam|india|singapore|japan|tokyo|australia|sydney|israel|ireland|dublin|germany|berlin'
                       r'|france|paris|netherlands|amsterdam|poland|spain|switzerland|zurich|china|hong kong|korea|taiwan', re.I)


def us_ok(loc):
    """True if any listed location is in the US. A bare "Remote" (no country) passes; the agent confirms it from
    the posting. "Remote in Canada", "Toronto, ON", "London" alone fail; "New York; Toronto" passes."""
    parts = [p.strip() for p in re.split(r'[;|]|\s/\s|\n', loc or '') if p.strip()]
    if not parts:
        return True
    for p in parts:
        if US_RX.search(p) and not (NON_US_RX.search(p) and not re.search(r'united states|\busa?\b', p, re.I)):
            return True
        if re.fullmatch(r'(?:fully |100% )?remote(?: ?\(?(?:global|anywhere|worldwide)\)?)?', p, re.I) and not NON_US_RX.search(p):
            return True
    return False


INTERN_RX = re.compile(r'\bintern(?:ship)?s?\b|\bco-?op\b', re.I)
NEWGRAD_RX = re.compile(r'new[ -]?grad|new graduate|university grad|college grad|recent grad|early[ -]career|entry[ -]level'
                        r'|\bgrad(?:uate)? (?:software|engineer)|class of 20\d\d|20\d\d (?:new )?grad|university hire|early talent'
                        r'|\bcampus\b|engineer,? (?:i|1)\b|\bassociate software engineer', re.I)
NEWGRAD_DESC_RX = re.compile(r'new[ -]grad|new graduates?|recent(?:ly)? graduat|early[ -]career|graduating (?:in|by|between)'
                             r'|\b0\s*(?:-|to)\s*[12]\+? years', re.I)
# A season in the description must carry a year ("Spring 2027"), or "Spring Boot" would count.
SEASON_RX = re.compile(r'\b(winter|spring|summer|fall|autumn)\b(?:\s*(?:/|or|and|&)\s*(winter|spring|summer|fall|autumn)\b)?\s*\'?(?:20)?\d\d\b', re.I)
SEASON_WORD_RX = re.compile(r'\b(winter|spring|summer|fall|autumn)\b', re.I)


TERM_RX = re.compile(r'\b(winter|spring|summer|fall|autumn)\s*\'?(20\d\d|\d\d)\b', re.I)


def role_kind(c, offseason, excluded=()):
    """'new_grad', 'offseason_intern', 'intern:<seasons>' (in-season, undated, or only excluded terms), or 'other'.
    Dated terms ("Winter 2027") are checked against `excluded`; bare seasons ("Winter Intern") cannot be."""
    t = c['title']
    if INTERN_RX.search(t):
        norm_s = lambda x: 'fall' if x.lower() == 'autumn' else x.lower()
        excl = {e.lower() for e in excluded}
        dated = {(norm_s(m.group(1)), m.group(2) if len(m.group(2)) == 4 else '20' + m.group(2))
                 for m in TERM_RX.finditer(t + ' ' + c['extra'])}
        if not dated:
            dated = {(norm_s(m.group(1)), m.group(2) if len(m.group(2)) == 4 else '20' + m.group(2))
                     for m in TERM_RX.finditer(c['description'] or '')}
        if dated:
            ok = {d for d in dated if d[0] in offseason and f'{d[0]} {d[1]}' not in excl}
            if ok:
                return 'offseason_intern'
            if any(d[0] in offseason for d in dated):
                return 'intern:excluded-term'
            return 'intern:' + '/'.join(sorted(f'{a} {b}' for a, b in dated))
        seasons = {norm_s(m) for m in SEASON_WORD_RX.findall(t + ' ' + c['extra'])}
        if re.search(r'off[ -]?(?:cycle|season)', t + ' ' + (c['description'] or '')[:3000], re.I):
            seasons.add('offcycle')
        return 'offseason_intern' if seasons & (set(offseason) | {'offcycle'}) else 'intern:' + ('/'.join(sorted(seasons)) or 'undated')
    if c.get('feed_kind') == 'new_grad' or NEWGRAD_RX.search(t) or NEWGRAD_DESC_RX.search(c['description'] or ''):
        return 'new_grad'
    return 'other'


def keep(c, f, cutoff, sponsor_needed, citizen):
    t, loc, desc = c['title'], c['location'], c['description']
    inc, exc = compile_any(f.get('title_include')), compile_any(f.get('title_exclude'))
    if inc and not inc.search(t):
        return 'title'
    # "Member of Technical Staff" is a title we want even though "staff" is a seniority word.
    if exc and exc.search(re.sub(r'technical staff', '', t, flags=re.I)):
        return 'title'
    # Feed categories (Simplify: Software, AI/ML/Data, Quant, Hardware, Product). Outside the list, a title matching
    # category_rescue_titles still passes ("Embedded Software Intern" filed under Hardware).
    cats = [x.lower() for x in f.get('categories') or []]
    if cats and c.get('category') and c['category'].lower() not in cats:
        rescue = compile_any(f.get('category_rescue_titles'))
        if not (rescue and rescue.search(t)):
            return 'category'
    if f.get('us_only') and not us_ok(loc):
        return 'non-us'
    if f.get('role_types'):
        c['kind'] = role_kind(c, [x.lower() for x in f.get('offseason_terms') or ['winter', 'spring']], f.get('exclude_terms') or ())
        if c['kind'] not in f['role_types']:
            return {'other': 'not-newgrad', 'intern:undated': 'undated-intern',
                    'intern:excluded-term': 'excluded-term'}.get(c['kind'], 'in-season-intern')
    linc, lexc = compile_any(f.get('locations_include')), compile_any(f.get('locations_exclude'))
    if linc and loc and not linc.search(loc):
        return 'location'
    # An excluded place wins over a generic include ("Remote in Canada"); only a specific include
    # term (a city, "united states") rescues it ("New York; London").
    specific = compile_any([w for w in f.get('locations_include') or [] if w.lower() not in ('remote', 'hybrid', 'anywhere')])
    if lexc and loc and lexc.search(loc) and not (specific and specific.search(loc)):
        return 'location'
    if cutoff and c['posted'] and c['posted'] < cutoff:
        return 'age'
    if sponsor_needed and re.search(r'does not offer sponsorship', c['extra'], re.I):
        return 'sponsorship'
    if not citizen and re.search(r'citizenship is required', c['extra'], re.I):
        return 'citizenship'
    return ''


FLAGS = [  # (flag, pattern) screened over the description; context is printed by `screen`
    ('yrs', re.compile(r'(\d{1,2})\s*\+?\s*(?:-|to)?\s*\d{0,2}\s*\+?\s*years?\b[^.\n]{0,40}\bexperience|(?:minimum|at least) (?:of )?(\d{1,2}) years', re.I)),
    ('clearance', re.compile(r'security clearance|\bTS/SCI\b|secret clearance|clearance (?:is )?required', re.I)),
    ('citizen', re.compile(r'u\.?s\.? citizen|\bus person|\bitar\b|export control', re.I)),
    ('phd', re.compile(r'\bph\.?d\b', re.I)),
    ('grad', re.compile(r'(?:graduat\w*|class of)[^.\n]{0,40}?\b(20\d\d)\b', re.I)),
]


def screen_flags(desc):
    """Short eligibility flags like ['3yrs', 'citizen', 'grad2026'] so most postings are triaged without reading them."""
    out = []
    for name, rx in FLAGS:
        ms = list(rx.finditer(desc or ''))
        if not ms:
            continue
        if name == 'yrs':
            yrs = [int(g) for m in ms for g in m.groups() if g]
            out.append(f'{min(yrs)}yrs' if yrs else 'yrs')
        elif name == 'grad':
            out.append('grad' + '/'.join(sorted({m.group(1) for m in ms})))
        else:
            out.append(name)
    return out


def sweep(args):
    cfg = track.load_config()
    f = cfg.get('filters') or {}
    el = cfg.get('eligibility') or {}
    only = track.arg(args, '--source').lower()
    sources = [s for s in cfg.get('sources') or [] if not only or only in json.dumps(s).lower()]
    days = int(f.get('max_age_days') or 0)
    cutoff = (datetime.datetime.now(UTC) - datetime.timedelta(days=days)).date().isoformat() if days else ''
    rows = track.read_rows()

    api = [s for s in sources if s.get('type') in FETCH]
    browse = [s for s in sources if s.get('type') == 'browse']
    unknown = [s for s in sources if s.get('type') not in FETCH and s.get('type') != 'browse']
    raw, t0 = [], time.time()
    with cf.ThreadPoolExecutor(8) as ex:
        futs = {ex.submit(FETCH[s['type']], s): s for s in api}
        try:
            for fu in cf.as_completed(futs, timeout=DEADLINE):
                s = futs[fu]
                got = fu.result()
                if not got:
                    print(f'  ! {s["type"]} {s.get("slug") or s.get("repo")}: no postings (bad slug, empty board, or network)', file=sys.stderr)
                raw += got
        except cf.TimeoutError:
            print(f'  ! stopped at the {DEADLINE}s deadline; results are partial', file=sys.stderr)

    dropped, kept, seen = {}, [], set()
    for c in raw:
        why = keep(c, f, cutoff, el.get('needs_sponsorship'), el.get('us_citizen_or_permanent_resident', True))
        if not why:
            keys = {track.clean_url(c['url'])} | ({track.norm(c['company']) + ':' + c['job_id']} if c['job_id'] else set())
            if keys & seen:
                why = 'repeat'
            seen |= keys
        if not why:
            c['flags'] = screen_flags(c['description'])
            yrs = next((int(x[:-3]) for x in c['flags'] if x[:-3].isdigit()), 0)
            if yrs and yrs >= int(f.get('max_years_experience') or 99) + 2:
                why = 'years'
        if not why:
            code, msg = track.gate(c['company'], c['url'], c['job_id'], cfg, rows, title=c['title'])
            if code in (track.SKIP, track.DUPLICATE, track.CAP):
                why = {track.SKIP: 'skip-list', track.DUPLICATE: 'already-tracked', track.CAP: 'company-cap'}[code]
            else:
                c['gate'] = 'BLACKLIST' if code == track.BLACKLIST else 'CLEAR'
        if why:
            dropped[why] = dropped.get(why, 0) + 1
            continue
        kept.append(c)

    kept.sort(key=lambda c: c['posted'], reverse=True)
    for i, c in enumerate(kept, 1):
        c['id'] = i
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(kept, open(OUT, 'w'), indent=1)

    limit = len(kept) if '--all' in args else int(track.arg(args, '--limit') or 40)
    print(f'postings {len(raw)}  candidates {len(kept)}  dropped {dropped}  {time.time() - t0:.0f}s  -> {os.path.relpath(OUT, R)}')
    print('id|gate|posted|company|title|location|flags  (B = blacklist; NG = new grad; OFF = off-season intern; nodesc = description only via jd/browser)')
    for c in kept[:limit]:
        kind = {'new_grad': 'NG', 'offseason_intern': 'OFF'}.get(c.get('kind', ''), '')
        flags = ','.join(([kind] if kind else []) + c['flags'] + ([] if c['description'] else ['nodesc']) + ([c['extra'][:30]] if c['extra'] else []))
        print('|'.join(str(x) for x in (c['id'], 'B' if c['gate'] == 'BLACKLIST' else '', c['posted'][5:], c['company'][:24],
                                        c['title'][:70], c['location'][:32], flags)))
    if len(kept) > limit:
        print(f'... {len(kept) - limit} more in {os.path.relpath(OUT, R)} (--all to print them)')
    if browse:
        print('\n--- BROWSE SOURCES (no API; visit each in the browser and apply the same filters by hand):')
        for s in browse:
            print(f'\t{s.get("company", "")}\t{s["url"]}\t{s.get("note", "")}')
    if unknown:
        print('\n--- UNKNOWN SOURCE TYPES (fix config/apply.json):', [s.get('type') for s in unknown])
    if ERRORS:
        print('--- request errors:', ERRORS, file=sys.stderr)
    return 0


BOILERPLATE = re.compile(
    r'equal (?:employment )?opportunity|\beeo\b|regardless of (?:race|age|sex)|without regard to|reasonable accommodation'
    r'|e-verify|privacy (?:policy|notice)|applicant privacy|fair chance|arrest (?:and|or) conviction|recruitment agenc'
    r'|unsolicited resume|pay transparency|beware of|phishing|ccpa|gdpr', re.I)


def strip_boilerplate(desc):
    """Drop legal/EEO/privacy paragraphs (often 20-40% of a posting). Paragraphs with a pay figure are kept."""
    paras = re.split(r'\n\s*\n', desc)
    return '\n\n'.join(p for p in paras if '$' in p or not BOILERPLATE.search(p)).strip()


def load_cand(key):
    if key.isdigit() and os.path.exists(OUT):
        return next((x for x in json.load(open(OUT)) if x.get('id') == int(key)), None)
    return None


def screen(args):
    c = load_cand(args[1]) if len(args) > 1 else None
    if not c:
        sys.exit('usage: jobs.py screen <candidate-id> (from the last sweep)')
    print(f'{c["company"]} | {c["title"]} | {c["location"][:60]} | {c["extra"]}')
    if not c['description']:
        print('no description in the feed: run `jobs.py jd` and grep the file, or read the posting page')
        return 0
    for name, rx in FLAGS:
        for m in list(rx.finditer(c['description']))[:3]:
            a, b = max(0, m.start() - 90), min(len(c['description']), m.end() + 90)
            print(f'[{name}] ...' + re.sub(r'\s+', ' ', c['description'][a:b]) + '...')
    if not any(rx.search(c['description']) for _, rx in FLAGS):
        print('no eligibility flags found')
    return 0


def slugify(*parts):
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', '_'.join(p for p in parts if p).lower())).strip('_')[:60]


def jd(args):
    if len(args) < 2:
        sys.exit('usage: jobs.py jd <candidate-id|url> [--name file_stem]')
    key = args[1]
    c = load_cand(key)
    if c is None:
        ats, slug, jid = parse_ats(key)
        c = {'company': slug, 'title': '', 'url': key, 'apply_url': key, 'ats': ats, 'slug': slug, 'job_id': jid,
             'description': '', 'location': '', 'extra': ''}
    desc, title, loc = c.get('description', ''), c.get('title', ''), c.get('location', '')
    if not desc and c.get('ats') and c.get('job_id'):
        a, s, j = c['ats'], c['slug'], c['job_id']
        if a == 'greenhouse':
            s = s or track.norm(c.get('company', ''))
            d = get(f'https://boards-api.greenhouse.io/v1/boards/{s}/jobs/{j}', 'greenhouse') or {}
            desc, title = html_to_text(d.get('content', '')), title or d.get('title', '')
            loc = loc or (d.get('location') or {}).get('name', '')
        elif a == 'lever':
            d = get(f'https://api.lever.co/v0/postings/{s}/{j}', 'lever') or {}
            desc = (d.get('descriptionPlain') or '') + '\n\n' + '\n\n'.join(
                f"{x.get('text', '')}\n{html_to_text(x.get('content', ''))}" for x in d.get('lists') or [])
            title = title or d.get('text', '')
        elif a == 'ashby':
            d = get(f'https://api.ashbyhq.com/posting-api/job-board/{s}', 'ashby') or {}
            hit = next((x for x in d.get('jobs', []) if x.get('id') == j), {})
            desc, title = hit.get('descriptionPlain') or '', title or hit.get('title', '')
    if not desc.strip() and 'myworkdayjobs.com' in c['url']:
        # Workday's public JSON endpoint: https://<tenant>.wdN.myworkdayjobs.com/wday/cxs/<tenant>/<site>/job/...
        m = re.match(r'https?://(([^./]+)\.wd\d+\.myworkdayjobs\.com)/(?:[a-z]{2}-[A-Z]{2}/)?([^/]+)(/job/[^?#]+)', c['url'])
        if m:
            d = get(f'https://{m.group(1)}/wday/cxs/{m.group(2)}/{m.group(3)}{m.group(4)}', 'workday') or {}
            info = d.get('jobPostingInfo') or {}
            desc = html_to_text(info.get('jobDescription', ''))
            title = title or info.get('title', '')
            loc = loc or ' | '.join(x for x in [info.get('location', '')] + list(info.get('additionalLocations') or []) if x)
    if not desc.strip():
        print(f'NO_API_DESCRIPTION: {c["url"]}\nOpen it in the browser, read the page text, and save it to jds/<name>.txt yourself.')
        return 2
    desc = strip_boilerplate(desc)
    name = track.arg(args, '--name') or slugify(c.get('company', ''), title)
    path = os.path.join(JDS, name + '.txt')
    os.makedirs(JDS, exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(f'Company: {c.get("company", "")}\nRole: {title}\nLocation: {loc}\nPosting: {c["url"]}\n'
                 f'Apply: {c.get("apply_url", "")}\n' + (f'Notes: {c["extra"]}\n' if c.get('extra') else '') + '\n' + desc.strip() + '\n')
    print(os.path.relpath(path, R))
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
        sys.exit(0)
    sys.exit({'sweep': sweep, 'screen': screen, 'jd': jd}.get(a[0], lambda _: sys.exit(f'unknown command {a[0]!r}'))(a))
