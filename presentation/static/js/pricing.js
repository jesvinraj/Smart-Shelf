// Pricing page.
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

async function loadPricing() {
  const data = await api('/api/ai/pricing');
  const body = document.getElementById('pricingBody');
  clear(body);

  const avgDisc = data.length ? data.reduce((a, p) => a + p.recommended_discount_pct, 0) / data.length : 0;
  const critical = data.filter((p) => p.risk_level === 'CRITICAL').length;
  const maxSavings = data.reduce((a, p) => a + (p.unit_price - p.discounted_price) * p.quantity, 0);
  const kpis = document.getElementById('pricingKpis');
  clear(kpis);
  kpis.appendChild(kpi('At-risk batches', data.length, 'orange', '⚠️'));
  kpis.appendChild(kpi('Critical', critical, 'red', '🔴'));
  kpis.appendChild(kpi('Avg discount', avgDisc.toFixed(0) + '%', 'blue', '💸'));
  kpis.appendChild(kpi('Potential savings', inr(maxSavings), 'green', '💰'));

  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No at-risk stock.')).colSpan = 6;
    return;
  }
  data.forEach((p) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, p.product_name || ('Product ' + p.product_id)));
    const td = el('td');
    td.appendChild(pill(p.risk_level + ' (' + p.risk_score + ')', p.risk_level));
    tr.appendChild(td);
    tr.appendChild(el('td', null, inr(p.unit_price)));
    tr.appendChild(el('td', null, p.recommended_discount_pct + '%'));
    tr.appendChild(el('td', null, inr(p.discounted_price)));
    tr.appendChild(el('td', null, p.reason));
    body.appendChild(tr);
  });
}

loadPricing().catch((e) => console.error(e));
