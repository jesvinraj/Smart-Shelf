// Dashboard.
'use strict';

let dashCharts = [];

function kpiCard(icon, label, value, tone) {
  const card = el('div', 'card kpi');
  card.appendChild(el('div', 'kpi-ico ' + tone, icon));
  const wrap = el('div');
  wrap.appendChild(el('div', 'kpi-val', value));
  wrap.appendChild(el('div', 'kpi-lab', label));
  card.appendChild(wrap);
  return card;
}

function renderRisk(data) {
  const row = document.getElementById('riskBody');
  clear(row);
  if (!data.top_risk.length) {
    row.appendChild(el('td', null, 'No high-risk stock')).colSpan = 5;
    return;
  }
  data.top_risk.forEach((r) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, r.product_name));
    tr.appendChild(el('td', null, r.batch_code || r.batch_id));
    const td = el('td');
    td.appendChild(pill(r.risk_level, r.risk_level));
    tr.appendChild(td);
    tr.appendChild(el('td', null, r.days_left === null ? '—' : r.days_left));
    tr.appendChild(el('td', null, inr(r.unit_price)));
    row.appendChild(tr);
  });
}

function renderLowStock(data) {
  const box = document.getElementById('lowStock');
  clear(box);
  if (!data.low_stock.length) {
    box.appendChild(el('p', 'muted skeleton', 'No low-stock items.'));
    return;
  }
  data.low_stock.forEach((p) => {
    const item = el('div', 'alert-item');
    item.appendChild(el('span', 'severity', '⚠️'));
    const body = el('div', 'body');
    body.appendChild(el('h4', null, p.name));
    body.appendChild(el('p', null, `${p.stock} on hand · reorder at ${p.reorder_level}`));
    item.appendChild(body);
    box.appendChild(item);
  });
}

async function renderKpis(k) {
  const row = document.getElementById('kpiRow');
  clear(row);
  const cards = [
    ['📦', 'Stock Units', k.stock_units + (k.expiring_count ? ` (${k.expiring_count} expiring)` : ''), 'blue'],
    ['💰', 'Inventory Value', inr(k.inventory_value), 'green'],
    ['🛒', 'Revenue (30d)', inr(k.revenue), 'blue'],
    ['📈', 'Sales (30d)', k.sales_count + ' sales', 'yellow'],
    ['♻️', 'Waste Value', inr(k.waste_value), 'red'],
    ['⚠️', 'Risk Items', k.risk_items, 'orange'],
  ];
  cards.forEach(([ico, lab, val, tone]) => row.appendChild(kpiCard(ico, lab, val, tone)));
}

function renderCharts(data) {
  dashCharts.forEach((c) => c.destroy());
  dashCharts = [];
  dashCharts.push(new Chart(document.getElementById('salesChart'), {
    type: 'line',
    data: {
      labels: data.sales_trend.map((r) => r.date),
      datasets: [{ label: 'Revenue (₹)', data: data.sales_trend.map((r) => r.revenue),
        borderColor: '#2563eb', backgroundColor: 'rgba(37,99,235,.1)', fill: true, tension: .3 }],
    },
    options: { responsive: true, plugins: { legend: { display: false } } },
  }));
  dashCharts.push(new Chart(document.getElementById('expiryChart'), {
    type: 'doughnut',
    data: {
      labels: ['OK', 'Expiring Soon', 'Expired'],
      datasets: [{
        data: [data.expiry_summary.OK, data.expiry_summary.EXPIRING_SOON, data.expiry_summary.EXPIRED],
        backgroundColor: ['#16a34a', '#eab308', '#dc2626'],
      }],
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  }));
}

async function loadDashboard() {
  const data = await api('/api/dashboard');
  renderKpis(data.kpis);
  renderRisk(data);
  renderLowStock(data);
  renderCharts(data);
}

async function refreshDash() {
  const btn = document.querySelector('.page-head .btn');
  btn.disabled = true;
  await loadDashboard();
  btn.disabled = false;
}

loadDashboard().catch((e) => console.error(e));
