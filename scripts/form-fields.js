// Read-only form dump for the browser's javascript tool. Paste the whole file as the code to run.
// Returns compact JSON instead of a screenshot or full accessibility tree:
//   {iframes, files, fields: [[label, type, flags, value, options]]}
// flags: R = required, !  = aria-invalid, E = required but empty, M = value at maxLength (truncated)
// Set PROBLEMS_ONLY = true for the pre-submit check: it then returns only fields flagged ! E or M.
// Output is paged (the browser tool truncates long results, ~1.5KB): run with PAGE = 0, 1, ... until page + 1 = pages.
// Radio/checkbox groups are one row (they hide outside per-field wrappers on Ashby). Never writes to the page.
(() => {
  const PROBLEMS_ONLY = false, PAGE = 0, PER = 8;
  const txt = s => (s || '').replace(/\s+/g, ' ').trim();
  const vis = el => el.type === 'file' || !!(el.offsetParent || el.getClientRects().length);
  // The question wrapper used by Greenhouse, Lever, Ashby, Workday and most custom forms.
  const box = el => el.closest('fieldset, li, .application-question, [class*=question], [class*=field-entry], [class*=form-group], [class*=FormField], [data-automation-id*=formField]');
  // First line only: label blocks often carry helper text ("Attach", "Analyzing resume...") on later lines.
  const line1 = s => txt((s || '').split('\n').find(x => x.trim()));
  const head = el => { const b = box(el); return b && line1((b.querySelector('legend, label, [class*=label], [class*=title], .text') || b).innerText); };
  const labelOf = el => {
    const by = el.getAttribute('aria-labelledby');
    const l = (by && by.split(' ').map(id => document.getElementById(id)?.innerText).join(' '))
      || (el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`)?.innerText)
      || (el.type !== 'radio' && el.type !== 'checkbox' && el.closest('label')?.innerText)
      || el.getAttribute('aria-label') || head(el) || el.placeholder || el.name;
    return txt(l).slice(0, 70);
  };
  const out = [], groups = {};
  for (const el of document.querySelectorAll('input, textarea, select')) {
    const t = (el.type || el.tagName).toLowerCase();
    if (['hidden', 'submit', 'button', 'reset', 'image'].includes(t) || !vis(el)) continue;
    const req = el.required || el.getAttribute('aria-required') === 'true';
    if (t === 'radio' || t === 'checkbox') {
      const key = el.name || labelOf(el);
      // Options often sit in their own <li>, so look for the question wrapper above the option list.
      const list = el.closest('ul, ol, [role=radiogroup], [role=group]') || el;
      const g = groups[key] || (groups[key] = { label: txt(head(list) || el.name).slice(0, 70), type: t, req, opts: [], val: [] });
      const o = txt(el.closest('label')?.innerText || document.querySelector(`label[for="${CSS.escape(el.id || '_')}"]`)?.innerText || el.value).slice(0, 25);
      g.opts.push(o); if (el.checked) g.val.push(o); g.req = g.req || req;
      continue;
    }
    const val = t === 'file' ? [...el.files].map(f => f.name).join(',') : t === 'select-one' ? txt(el.selectedOptions[0]?.text) : el.value;
    const max = el.maxLength > 0 ? el.maxLength : 0;
    let flags = (req ? 'R' : '') + (el.getAttribute('aria-invalid') === 'true' ? '!' : '') + (req && !val ? 'E' : '') + (max && val.length >= max ? 'M' : '');
    const row = [labelOf(el), t + (max ? `/${max}` : ''), flags, txt(val).slice(0, 60)];
    if (el.tagName === 'SELECT') row.push([...el.options].slice(0, 8).map(o => txt(o.text).slice(0, 25)).concat(el.options.length > 8 ? [`+${el.options.length - 8}`] : []));
    out.push(row);
  }
  for (const g of Object.values(groups)) {
    const flags = (g.req ? 'R' : '') + (g.req && !g.val.length ? 'E' : '');
    out.push([g.label, g.type, flags, g.val.join(','), g.opts.slice(0, 8)]);
  }
  const all = PROBLEMS_ONLY ? out.filter(r => /[!EM]/.test(r[2])) : out;
  const pages = Math.max(1, Math.ceil(all.length / PER));
  return JSON.stringify({ page: PAGE, pages, total: all.length, iframes: document.querySelectorAll('iframe').length,
    files: document.querySelectorAll('input[type=file]').length, fields: all.slice(PAGE * PER, PAGE * PER + PER) });
})()
