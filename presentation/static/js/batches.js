// Batches page.
'use strict';

async function loadBatches() {
  const data = await api('/api/batches');
  const body = document.getElementById('batchBody');
  clear(body);
  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No batches.')).colSpan = 7;
    return;
  }
  data.forEach((b) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, b.batch_code || b.batch_number || '—'));
    tr.appendChild(el('td', null, b.product_id));
    tr.appendChild(el('td', null, b.quantity));
    tr.appendChild(el('td', null, b.location_id || '—'));
    tr.appendChild(el('td', null, b.supplier_id || '—'));
    tr.appendChild(el('td', null, b.manufactured_date ? b.manufactured_date.slice(0, 10) : '—'));
    tr.appendChild(el('td', null, b.expiry_date ? b.expiry_date.slice(0, 10) : '—'));
    body.appendChild(tr);
  });
}

loadBatches().catch((e) => console.error(e));
