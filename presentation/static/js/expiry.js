// Expiry page.
'use strict';

function kpi(label, value, tone, icon) {
  const card = el('div', 'card kpi');
  card.appendChild(el('div', 'kpi-ico ' + tone, icon));
  const w = el('div');
  w.appendChild(el('div', 'kpi-val', value));
  w.appendChild(el('div', 'kpi-lab', label));
  card.appendChild(w);
  return card;
}

async function loadExpiry() {
  const scan = await api('/api/expiry/scan');
  const alerts = await api('/api/expiry/alerts');
  const kpis = document.getElementById('expiryKpis');
  clear(kpis);
  kpis.appendChild(kpi('Expired', scan.expired_count, 'red', '⛔'));
  kpis.appendChild(kpi('Expiring soon', scan.expiring_soon_count, 'orange', '⏳'));
  kpis.appendChild(kpi('Healthy', alerts.length > 0 ? '—' : 'All OK', 'green', '✅'));

  const body = document.getElementById('expiryBody');
  clear(body);
  if (!alerts.length) {
    body.appendChild(el('td', 'muted skeleton', 'No batches expiring soon.')).colSpan = 5;
    return;
  }
  alerts.forEach((b) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, b.batch_code || b.batch_id));
    tr.appendChild(el('td', null, b.product_id));
    tr.appendChild(el('td', null, b.quantity));
    tr.appendChild(el('td', null, b.expiry_date ? b.expiry_date.slice(0, 10) : '—'));
    const td = el('td');
    td.appendChild(pill(b.status, b.status === 'EXPIRED' ? 'red' : 'orange'));
    tr.appendChild(td);
    body.appendChild(tr);
  });
}

async function scanExpiry() {
  await api('/api/alerts/scan');
  loadExpiry();
}

loadExpiry().catch((e) => console.error(e));
