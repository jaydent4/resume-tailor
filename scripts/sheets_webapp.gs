// Google Sheets bridge for the auto-apply workflow (scripts/track.py talks to it).
// Setup: in your existing sheet, Extensions -> Apps Script, paste this file, set TOKEN to sheets.token from
// config/apply.json, then Deploy -> New deployment -> Web app (Execute as: Me, Who has access: Anyone) and put
// the web app URL in config/apply.json (sheets.webhook_url).
//
// What it does to YOUR tabs: only adds rows. A submitted application becomes one new row (Company, Position,
// Date, Status = Pending, Notes = auto-apply) inside the tab's table, unless that Company + Position is already
// there. Existing rows are never edited or deleted. The only tab it rewrites is its own pipeline tab.
const TOKEN = 'PASTE_TOKEN_HERE';

const STATUS_COLORS = {
  SUBMITTED: '#d9ead3', RESUME_READY: '#cfe2f3', AWAITING_REVIEW: '#fff2cc',
  NEEDS_SIGN_IN: '#fce5cd', NEEDS_HUMAN: '#f4cccc', SKIPPED: '#efefef', FAILED: '#ea9999',
};

function doPost(e) {
  const b = JSON.parse(e.postData.contents);
  if (b.token !== TOKEN) return reply({ ok: false, error: 'bad token' });
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    if (b.action === 'read') return reply({ ok: true, rows: readAll(ss, b.pipeline_tab) });
    let added = 0;
    for (const s of b.submitted || []) if (appendIfMissing(ss, s, b.template_tab)) added++;
    if (b.pipeline_tab && b.pipeline) writePipeline(ss, b.pipeline_tab, b.pipeline);
    return reply({ ok: true, added });
  } finally {
    lock.releaseLock();
  }
}

// Locate the header row (the one containing "Company") and the table's columns.
function header(sh) {
  const rows = Math.min(5, sh.getLastRow()), cols = Math.min(26, sh.getLastColumn());
  if (rows < 1 || cols < 1) return null;
  const vals = sh.getRange(1, 1, rows, cols).getValues();
  for (let r = 0; r < vals.length; r++) {
    const h = vals[r].map(v => String(v).trim().toLowerCase());
    const c = h.indexOf('company');
    if (c < 0) continue;
    let last = c;
    while (last + 1 < h.length && h[last + 1]) last++;
    return { row: r + 1, first: c + 1, width: last - c + 1, names: h.slice(c, last + 1) };
  }
  return null;
}

function cell(hd, name) {
  const i = hd.names.indexOf(name);
  return i < 0 ? 0 : hd.first + i;
}

function dataRows(sh, hd) {
  const n = sh.getLastRow() - hd.row;
  return n > 0 ? sh.getRange(hd.row + 1, hd.first, n, hd.width).getValues() : [];
}

function iso(v) {
  return v instanceof Date ? Utilities.formatDate(v, Session.getScriptTimeZone(), 'yyyy-MM-dd') : String(v || '');
}

function readAll(ss, skip) {
  const out = [];
  for (const sh of ss.getSheets()) {
    if (sh.getName() === skip) continue;
    const hd = header(sh);
    if (!hd) continue;
    const at = n => hd.names.indexOf(n);
    for (const r of dataRows(sh, hd)) {
      const company = String(r[at('company')] || '').trim();
      if (!company) continue;
      out.push({ tab: sh.getName(), company, position: String(at('position') >= 0 ? r[at('position')] : '').trim(),
                 date: at('date') >= 0 ? iso(r[at('date')]) : '', status: at('status') >= 0 ? String(r[at('status')]) : '',
                 notes: at('notes') >= 0 ? String(r[at('notes')]) : '' });
    }
  }
  return out;
}

// New tab = copy of the template tab (keeps its table, dropdown chips and formatting) with the data removed.
function makeTab(ss, name, template) {
  const t = template && ss.getSheetByName(template);
  if (!t) {
    const sh = ss.insertSheet(name);
    sh.getRange(1, 1, 1, 7).setValues([['Company', 'Position', 'Date', 'Status', 'OA Status', 'OA Questions', 'Notes']]);
    sh.getRange(1, 1, 1, 7).setFontWeight('bold');
    return sh;
  }
  const sh = t.copyTo(ss).setName(name);
  const hd = header(sh);
  const last = sh.getLastRow();
  if (last > hd.row + 1) sh.deleteRows(hd.row + 2, last - hd.row - 1);
  sh.getRange(hd.row + 1, hd.first, 1, hd.width).clearContent();
  return sh;
}

function appendIfMissing(ss, s, template) {
  const sh = ss.getSheetByName(s.tab) || makeTab(ss, s.tab, template);
  const hd = header(sh);
  if (!hd) return false;
  const rows = dataRows(sh, hd);
  const ci = hd.names.indexOf('company'), pi = hd.names.indexOf('position');
  const norm = v => String(v || '').trim().toLowerCase();
  if (rows.some(r => norm(r[ci]) === norm(s.company) && (pi < 0 || norm(r[pi]) === norm(s.position)))) return false;

  // Prefer the first empty row inside the table; otherwise grow the table from the inside: insert a row above
  // the last one, move the last row up into it, and write the new entry in the (now freed) last row.
  let target = 0;
  for (let i = 0; i < rows.length; i++) if (!norm(rows[i][ci]) && (pi < 0 || !norm(rows[i][pi]))) { target = hd.row + 1 + i; break; }
  if (!target) {
    const last = hd.row + rows.length;
    if (rows.length === 0) {
      target = hd.row + 1;
    } else {
      sh.insertRowBefore(last);
      sh.getRange(last + 1, hd.first, 1, hd.width).copyTo(sh.getRange(last, hd.first, 1, hd.width));
      target = last + 1;
      sh.getRange(target, hd.first, 1, hd.width).clearContent();
    }
  }
  const set = (name, v) => { const c = cell(hd, name); if (c) sh.getRange(target, c).setValue(v); };
  set('company', s.company);
  set('position', s.position);
  if (s.date) set('date', new Date(s.date + 'T00:00:00'));
  set('status', 'Pending');
  set('notes', 'auto-apply');
  return true;
}

// The script's own tab. Refuses to touch a tab that does not carry its exact header.
function writePipeline(ss, name, rows) {
  let sh = ss.getSheetByName(name);
  if (sh && sh.getLastRow() > 0) {
    const h = sh.getRange(1, 1, 1, rows[0].length).getValues()[0].join('|');
    if (h !== rows[0].join('|')) return;
  }
  sh = sh || ss.insertSheet(name);
  sh.clear();
  sh.getRange(1, 1, rows.length, rows[0].length).setValues(rows);
  sh.getRange(1, 1, 1, rows[0].length).setFontWeight('bold');
  sh.setFrozenRows(1);
  const col = rows[0].indexOf('Status') + 1;
  if (col > 0 && rows.length > 1) {
    sh.getRange(2, col, rows.length - 1, 1).setBackgrounds(rows.slice(1).map(r => [STATUS_COLORS[r[col - 1]] || null]));
  }
  sh.autoResizeColumns(1, rows[0].length);
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
