// Sales page.
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

async function loadSales() {
  const data = await api('/api/sales');
  const body = document.getElementById('salesBody');
  clear(body);
  const kpis = document.getElementById('saleKpis');
  clear(kpis);
  const revenue = data.reduce((a, s) => a + (s.total_amount || 0), 0);
  const discounts = data.reduce((a, s) => a + (s.discount_amount || 0), 0);
  kpis.appendChild(kpi('Sales (recent)', data.length, 'blue', '🛒'));
  kpis.appendChild(kpi('Revenue', inr(revenue), 'green', '💰'));
  kpis.appendChild(kpi('Discounts given', inr(discounts), 'orange', '💸'));

  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No sales yet.')).colSpan = 7;
    return;
  }
  data.forEach((s) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, s.invoice_number || s.id));
    tr.appendChild(el('td', null, s.sale_date ? s.sale_date.slice(0, 16) : '—'));
    tr.appendChild(el('td', null, s.payment_method || '—'));
    tr.appendChild(el('td', null, inr(s.subtotal)));
    tr.appendChild(el('td', null, inr(s.discount_amount)));
    tr.appendChild(el('td', null, inr(s.total_amount)));
    const td = el('td');
    td.appendChild(pill(s.status, s.status === 'COMPLETED' ? 'green' : 'yellow'));
    tr.appendChild(td);
    body.appendChild(tr);
  });
}

document.getElementById('saleForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const payload = {
    items: [{ product_id: +f.get('product_id'), quantity: +f.get('quantity'),
      unit_price: f.get('unit_price') ? +f.get('unit_price') : undefined }],
    payment_method: f.get('payment_method'),
  };
  try {
    await post('/api/sales', payload);
    document.getElementById('saleModal').classList.add('hide');
    e.target.reset();
    loadSales();
    alert('Sale recorded (FEFO applied).');
  } catch (err) { alert(err.message); }
});

loadSales().catch((e) => console.error(e));
