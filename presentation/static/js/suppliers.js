// Suppliers page.
'use strict';

async function loadSuppliers() {
  const data = await api('/api/suppliers');
  const body = document.getElementById('supplierBody');
  clear(body);
  if (!data.length) {
    body.appendChild(el('td', 'muted skeleton', 'No suppliers.')).colSpan = 7;
    return;
  }
  data.forEach((s) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, s.name));
    tr.appendChild(el('td', null, s.contact_person || '—'));
    tr.appendChild(el('td', null, s.phone || '—'));
    tr.appendChild(el('td', null, s.email || '—'));
    tr.appendChild(el('td', null, s.address || '—'));
    const td = el('td');
    td.appendChild(pill(s.is_active ? 'ACTIVE' : 'INACTIVE', s.is_active ? 'green' : 'red'));
    tr.appendChild(td);
    const a = el('td');
    const btn = el('button', 'icon-btn', '🗑');
    btn.title = 'Deactivate';
    btn.onclick = async () => { await del('/api/suppliers/' + s.id); loadSuppliers(); };
    a.appendChild(btn);
    tr.appendChild(a);
    body.appendChild(tr);
  });
}

document.getElementById('addForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  await post('/api/suppliers', Object.fromEntries(new FormData(e.target).entries()));
  document.getElementById('addModal').classList.add('hide');
  e.target.reset();
  loadSuppliers();
});

loadSuppliers().catch((e) => console.error(e));
