// FEFO page.
'use strict';

function fefoCard(item) {
  const cls = item.label === 'SELL_FIRST' ? 'first' : (item.label === 'SELL_NEXT' ? 'next' : 'normal');
  const card = el('div', 'fefo-card ' + cls);
  const label = item.label === 'SELL_FIRST' ? 'SELL FIRST 🚩' : (item.label === 'SELL_NEXT' ? 'SELL NEXT' : 'NORMAL');
  card.appendChild(el('span', 'rank', '#' + item.rank));
  card.appendChild(el('h4', null, item.batch_code || ('Batch ' + item.batch_id)));
  card.appendChild(el('div', 'exp', item.expiry_date ? 'Expiry ' + item.expiry_date : 'No expiry'));
  const meta = el('div', 'fefo-meta');
  const days = el('span');
  days.appendChild(document.createTextNode(item.days_left === null ? '—' : item.days_left + 'd'));
  days.appendChild(el('small', null, 'days left'));
  const qty = el('span');
  qty.appendChild(document.createTextNode(String(item.quantity)));
  qty.appendChild(el('small', null, 'qty'));
  const pri = el('span');
  pri.appendChild(document.createTextNode(label));
  pri.appendChild(el('small', null, 'priority'));
  meta.appendChild(days); meta.appendChild(qty); meta.appendChild(pri);
  card.appendChild(meta);
  return card;
}

async function loadFefo() {
  const data = await api('/api/fefo');
  const flow = document.getElementById('fefoFlow');
  clear(flow);
  if (!data.items.length) {
    flow.appendChild(el('p', 'muted skeleton', 'No usable (non-expired) stock.'));
    return;
  }
  data.items.forEach((item, i) => {
    flow.appendChild(fefoCard(item));
    if (i < data.items.length - 1) flow.appendChild(el('div', 'fefo-arrow', '⇣'));
  });
}

loadFefo().catch((e) => console.error(e));
