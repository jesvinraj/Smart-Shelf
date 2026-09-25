// Products page.
'use strict';

async function loadProducts() {
  const data = await api('/api/products');
  const body = document.getElementById('productBody');
  clear(body);
  if (!data.items.length) {
    body.appendChild(el('td', 'muted skeleton', 'No products.')).colSpan = 8;
    return;
  }
  data.items.forEach((p) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, p.name));
    tr.appendChild(el('td', null, p.sku));
    tr.appendChild(el('td', null, p.category_id || '—'));
    tr.appendChild(el('td', null, p.unit || '—'));
    tr.appendChild(el('td', null, inr(p.unit_price)));
    const stock = el('td');
    const level = p.total_stock <= p.reorder_level ? 'red' : 'green';
    stock.appendChild(pill(p.total_stock + (p.total_stock <= p.reorder_level ? ' · low' : ''), level));
    tr.appendChild(stock);
    tr.appendChild(el('td', null, p.is_perishable ? 'Perishable' : 'Non-perishable'));
    const td = el('td');
    const btn = el('button', 'icon-btn', '🗑');
    btn.title = 'Deactivate';
    btn.onclick = async () => { await del('/api/products/' + p.id); loadProducts(); };
    td.appendChild(btn);
    tr.appendChild(td);
    body.appendChild(tr);
  });
}

document.getElementById('addForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const f = new FormData(e.target);
  const payload = Object.fromEntries(f.entries());
  if (f.has('is_perishable')) payload.is_perishable = true;
  await post('/api/products', payload);
  document.getElementById('addModal').classList.add('hide');
  e.target.reset();
  loadProducts();
});

loadProducts().catch((e) => console.error(e));
