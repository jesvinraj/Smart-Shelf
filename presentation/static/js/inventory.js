// Inventory page.
'use strict';

async function loadInventory() {
  const data = await api('/api/inventory');
  const body = document.getElementById('inventoryBody');
  clear(body);
  if (!data.items.length) {
    body.appendChild(el('td', 'muted skeleton', 'No stock recorded.')).colSpan = 7;
    return;
  }
  data.items.forEach((b) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, b.batch_code || '—'));
    tr.appendChild(el('td', null, b.product_id));
    tr.appendChild(el('td', null, b.quantity));
    tr.appendChild(el('td', null, b.location_id || '—'));
    tr.appendChild(el('td', null, b.supplier_id || '—'));
    tr.appendChild(el('td', null, b.expiry_date ? b.expiry_date.slice(0, 10) : '—'));
    const td = el('td');
    const tone = b.status === 'EXPIRED' ? 'red' : (b.status === 'EXPIRING_SOON' ? 'orange' : 'green');
    td.appendChild(pill(b.status, tone));
    tr.appendChild(td);
    body.appendChild(tr);
  });
}

async function loadLocations() {
  const data = await api('/api/locations');
  const box = document.getElementById('locationList');
  clear(box);
  if (!data.length) { box.appendChild(el('span', 'muted skeleton', 'No locations.')); return; }
  data.forEach((l) => {
    const chip = el('span', 'chip', `${l.code} · ${l.name} (${l.zone})`);
    box.appendChild(chip);
  });
}

document.getElementById('receiveForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  try {
    await post('/api/inventory/receive', Object.fromEntries(new FormData(e.target).entries()));
    e.target.reset();
    loadInventory();
    alert('Stock received.');
  } catch (err) { alert(err.message); }
});

document.getElementById('locForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  await post('/api/locations', Object.fromEntries(new FormData(e.target).entries()));
  e.target.reset();
  loadLocations();
});

loadInventory().catch((e) => console.error(e));
loadLocations().catch((e) => console.error(e));
