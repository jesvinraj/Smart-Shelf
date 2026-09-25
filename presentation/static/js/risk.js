// Risk Analysis page.
'use strict';

let riskData = [];

function kpiCard(label, value, tone, icon) {
  const card = el('div', 'card kpi');
  card.appendChild(el('div', 'kpi-ico ' + tone, icon || '⚠️'));
  const wrap = el('div');
  wrap.appendChild(el('div', 'kpi-val', value));
  wrap.appendChild(el('div', 'kpi-lab', label));
  card.appendChild(wrap);
  return card;
}

function renderKpis(data) {
  const row = document.getElementById('riskKpis');
  clear(row);
  const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  let max = 0, maxBatch = null;
  data.forEach((r) => {
    counts[r.risk_level] = (counts[r.risk_level] || 0) + 1;
    if (r.risk_score > max) { max = r.risk_score; maxBatch = r.batch_id; }
  });
  row.appendChild(kpiCard('Critical', counts.CRITICAL, 'red', '🔴'));
  row.appendChild(kpiCard('High', counts.HIGH, 'orange', '🟠'));
  row.appendChild(kpiCard('Medium', counts.MEDIUM, 'yellow', '🟡'));
  row.appendChild(kpiCard('Low', counts.LOW, 'green', '🟢'));
}

function renderTable(data) {
  const body = document.getElementById('riskBody');
  clear(body);
  const filter = document.getElementById('riskFilter').value;
  data.forEach((r) => {
    if (filter !== 'ALL' && r.risk_level !== filter) return;
    const tr = el('tr');
    tr.appendChild(el('td', null, r.batch_id));
    tr.appendChild(el('td', null, r.product_id));
    tr.appendChild(el('td', null, ''));
    tr.appendChild(el('td', null, r.days_to_expiry === null ? '—' : r.days_to_expiry));
    tr.appendChild(el('td', null, `${r.risk_score}/100`));
    const td = el('td');
    td.appendChild(pill(r.risk_level, r.risk_level));
    tr.appendChild(td);
    body.appendChild(tr);
  });
  if (!body.childNodes.length) body.appendChild(el('td', 'muted skeleton', 'No batches match.')).colSpan = 6;
}

async function loadRisk() {
  riskData = await api('/api/ai/risk');
  renderKpis(riskData);
  renderTable(riskData);
}

document.getElementById('riskFilter').addEventListener('change', () => renderTable(riskData));
loadRisk().catch((e) => console.error(e));
