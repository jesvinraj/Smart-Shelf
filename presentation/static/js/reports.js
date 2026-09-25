// Reports page.
'use strict';

let salesChart = null;

async function loadSales() {
  const data = await api('/api/reports/sales?days=30');
  if (salesChart) salesChart.destroy();
  salesChart = new Chart(document.getElementById('salesChart'), {
    type: 'bar',
    data: {
      labels: data.daily.map((r) => r.date),
      datasets: [
        { label: 'Revenue (₹)', data: data.daily.map((r) => r.revenue), backgroundColor: '#2563eb' },
        { label: 'Discounts (₹)', data: data.daily.map((r) => r.discounts), backgroundColor: '#ea7a1b' },
      ],
    },
    options: { responsive: true, plugins: { legend: { position: 'bottom' } } },
  });
}

async function loadInventory() {
  const data = await api('/api/reports/inventory');
  document.getElementById('inventoryMeta').textContent =
    `${data.total_stock} batches · total value ${inr(data.total_value)}`;
  const body = document.getElementById('inventoryBody');
  clear(body);
  data.items.forEach((it) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, it.product));
    tr.appendChild(el('td', null, it.batch));
    tr.appendChild(el('td', null, it.quantity));
    tr.appendChild(el('td', null, it.expiry ? it.expiry.slice(0, 10) : '—'));
    tr.appendChild(el('td', null, inr(it.cost_value)));
    body.appendChild(tr);
  });
}

async function loadWaste() {
  const data = await api('/api/reports/waste');
  document.getElementById('wasteMeta').textContent = `${data.count} records · potential loss ${inr(data.potential_loss)}`;
  const box = document.getElementById('wasteByReason');
  clear(box);
  Object.entries(data.by_reason || {}).forEach(([reason, count]) => {
    const item = el('div', 'alert-item');
    item.appendChild(el('span', 'severity', '♻️'));
    const b = el('div', 'body');
    b.appendChild(el('h4', null, reason));
    b.appendChild(el('p', null, `${count} record(s)`));
    item.appendChild(b);
    box.appendChild(item);
  });
}

async function loadPerformance() {
  const data = await api('/api/reports/performance');
  const body = document.getElementById('performanceBody');
  clear(body);
  data.forEach((p) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, p.name));
    tr.appendChild(el('td', null, p.total_sold));
    tr.appendChild(el('td', null, p.stock_on_hand));
    body.appendChild(tr);
  });
}

async function loadAll() {
  await Promise.all([loadSales(), loadInventory(), loadWaste(), loadPerformance()]).catch((e) => console.error(e));
}

loadAll();
