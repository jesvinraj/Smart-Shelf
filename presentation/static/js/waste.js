// Waste page.
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

async function loadWaste() {
  const data = await api('/api/wastage');
  const summary = await api('/api/wastage/summary');
  const kpis = document.getElementById('wasteKpis');
  clear(kpis);
  kpis.appendChild(kpi('Potential loss', inr(summary.potential_loss), 'red', '💸'));
  kpis.appendChild(kpi('Recovered revenue', inr(summary.recovered_revenue), 'green', '💰'));
  kpis.appendChild(kpi('Savings', inr(summary.savings_from_discount), 'blue', '💵'));
  kpis.appendChild(kpi('Net waste cost', inr(summary.net_waste_cost), 'orange', '♻️'));

  const body = document.getElementById('wasteBody');
  clear(body);
  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No waste recorded.')).colSpan = 7;
    return;
  }
  data.forEach((w) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, w.product_id));
    tr.appendChild(el('td', null, w.batch_id || '—'));
    tr.appendChild(el('td', null, w.quantity));
    tr.appendChild(el('td', null, w.reason));
    tr.appendChild(el('td', null, inr(w.potential_loss)));
    tr.appendChild(el('td', null, inr(w.recovered_revenue)));
    tr.appendChild(el('td', null, inr(w.savings)));
    body.appendChild(tr);
  });
}

document.getElementById('wasteForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await post('/api/wastage', Object.fromEntries(new FormData(e.target).entries()));
    document.getElementById('wasteModal').classList.add('hide');
    e.target.reset();
    loadWaste();
  } catch (err) { alert(err.message); }
});

loadWaste().catch((e) => console.error(e));
