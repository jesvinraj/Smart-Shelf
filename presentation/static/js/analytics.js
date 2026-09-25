// Analytics page.
'use strict';

function movementPill(cls) {
  const tone = cls === 'FAST' ? 'green' : (cls === 'SLOW' ? 'red' : 'blue');
  return pill(cls, tone);
}

async function loadVelocity() {
  const data = await api('/api/ai/velocity');
  const body = document.getElementById('velocityBody');
  clear(body);
  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No sales data yet.')).colSpan = 4;
    return;
  }
  data.forEach((p) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, p.product_name || p.product_id));
    tr.appendChild(el('td', null, p.total_quantity));
    tr.appendChild(el('td', null, p.velocity_per_day));
    const td = el('td');
    td.appendChild(movementPill(p.movement_class));
    tr.appendChild(td);
    body.appendChild(tr);
  });
}

async function loadDemand() {
  const data = await api('/api/ai/demand-analysis?days=30');
  const box = document.getElementById('demandList');
  clear(box);
  if (!data.length) { box.appendChild(el('p', 'muted skeleton', 'No demand data.')); return; }
  data.forEach((d) => {
    const item = el('div', 'alert-item');
    item.appendChild(el('span', 'severity', '📈'));
    const b = el('div', 'body');
    b.appendChild(el('h4', null, 'Product ' + d.product_id));
    b.appendChild(el('p', null, `${d.quantity} units · ${d.velocity_per_day}/day`));
    item.appendChild(b);
    box.appendChild(item);
  });
}

async function loadForecast() {
  const pid = document.getElementById('forecastPid').value;
  const data = await api('/api/ai/forecast/' + pid + '?horizon=7');
  const box = document.getElementById('forecastBox');
  clear(box);
  if (!data.forecast.length) {
    box.appendChild(el('p', 'muted skeleton', 'No history for this product.'));
    return;
  }
  box.appendChild(el('p', 'muted', `Model: ${data.model} · confidence ${Math.round(data.confidence * 100)}%`));
  data.forecast.forEach((f) => {
    const item = el('div', 'alert-item');
    item.appendChild(el('span', 'severity', '📅'));
    const b = el('div', 'body');
    b.appendChild(el('h4', null, 'Day ' + f.day));
    b.appendChild(el('p', null, `≈ ${f.qty} units`));
    item.appendChild(b);
    box.appendChild(item);
  });
}

loadVelocity().catch((e) => console.error(e));
loadDemand().catch((e) => console.error(e));
loadForecast().catch((e) => console.error(e));
