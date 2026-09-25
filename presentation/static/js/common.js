// SmartShelf shared helpers.
'use strict';

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (res.status === 401) {
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Request failed: ' + path);
  return data;
}

function post(path, body) {
  return api(path, { method: 'POST', body: JSON.stringify(body || {}) });
}

function put(path, body) {
  return api(path, { method: 'PUT', body: JSON.stringify(body || {}) });
}

function del(path) {
  return api(path, { method: 'DELETE' });
}

function el(tag, cls, text) {
  const n = document.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined) n.textContent = text;
  return n;
}

function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}

// Money / number formatting (INR).
function inr(value) {
  const num = Number(value) || 0;
  return '₹' + num.toLocaleString('en-IN', { maximumFractionDigits: 2 });
}

function riskColor(level) {
  return { CRITICAL: 'red', HIGH: 'orange', MEDIUM: 'yellow', LOW: 'green' }[level] || 'blue';
}

function pill(label, level) {
  const cls = riskColor(level);
  const p = el('span', 'pill ' + cls);
  p.appendChild(el('span', 'dot'));
  p.appendChild(document.createTextNode(label));
  return p;
}
