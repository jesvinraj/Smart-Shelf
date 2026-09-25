// Alerts page.
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

async function loadAlerts() {
  const data = await api('/api/notifications');
  const kpis = document.getElementById('alertKpis');
  clear(kpis);
  const unread = data.filter((n) => !n.is_read).length;
  kpis.appendChild(kpi('Unread', unread, 'orange', '🔔'));
  kpis.appendChild(kpi('Total', data.length, 'blue', '📋'));
  kpis.appendChild(kpi('Expiry', data.filter((n) => n.type === 'NEAR_EXPIRY' || n.type === 'EXPIRED').length, 'red', '⏳'));
  kpis.appendChild(kpi('Low stock', data.filter((n) => n.type === 'LOW_STOCK').length, 'yellow', '⚠️'));

  const list = document.getElementById('alertList');
  clear(list);
  list.appendChild(el('div', 'sect-title', 'Notifications'));
  if (!data.length) {
    list.appendChild(el('p', 'muted skeleton', 'No notifications.'));
    return;
  }
  data.forEach((n) => {
    const tone = n.severity === 'CRITICAL' ? 'red' : (n.severity === 'WARNING' ? 'orange' : 'blue');
    const item = el('div', 'alert-item border-left-' + tone);
    item.appendChild(el('span', 'severity', n.severity === 'CRITICAL' ? '⛔' : (n.severity === 'WARNING' ? '⚠️' : 'ℹ️')));
    const b = el('div', 'body');
    b.appendChild(el('h4', null, n.title + (n.is_read ? '' : ' · NEW')));
    b.appendChild(el('p', null, n.message));
    item.appendChild(b);
    item.appendChild(el('span', 'muted', n.created_at ? n.created_at.slice(0, 16) : ''));
    if (!n.is_read) {
      const btn = el('button', 'btn sm outline', 'Read');
      btn.onclick = async () => { await post('/api/notifications/' + n.id + '/read'); loadAlerts(); };
      item.appendChild(btn);
    }
    list.appendChild(item);
  });
}

async function generateAlerts() {
  await api('/api/alerts/generate', { method: 'POST' });
  loadAlerts();
}

async function readAll() {
  await post('/api/notifications/read-all');
  loadAlerts();
}

loadAlerts().catch((e) => console.error(e));
