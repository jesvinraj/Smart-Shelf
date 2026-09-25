// Settings & Security page: account, password, 2FA, login history.
'use strict';

async function loadAccount() {
  const data = await api('/api/auth/me');
  const u = data.user;
  const box = document.getElementById('accountInfo');
  clear(box);
  const item = el('div', 'alert-item');
  item.appendChild(el('span', 'severity', '👤'));
  const b = el('div', 'body');
  b.appendChild(el('h4', null, u.full_name || u.username));
  b.appendChild(el('p', null, `${u.username} · ${u.email}`));
  item.appendChild(b);
  const role = el('span');
  role.appendChild(pill(u.role, u.role === 'ADMIN' ? 'red' : 'blue'));
  item.appendChild(role);
  box.appendChild(item);

  document.getElementById('pwPolicyHint').textContent =
    '8+ chars: uppercase, lowercase, digit and a special character. Not a common password.';
  renderTwoFA(u);
}

// ----------------------- Change password -----------------------
const pwForm = document.getElementById('pwForm');
const pwMsg = document.getElementById('pwMsg');
const pwText = document.getElementById('pwText');

function showPw(err) {
  pwText.textContent = err;
  pwMsg.classList.remove('hide');
}

pwForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  pwMsg.classList.add('hide');
  const oldPw = document.getElementById('old_password').value;
  const newPw = document.getElementById('new_password').value;
  const newPw2 = document.getElementById('new_password2').value;
  if (newPw !== newPw2) { showPw('New passwords do not match.'); return; }
  try {
    await post('/api/auth/change-password', {
      old_password: oldPw,
      new_password: newPw,
    });
    pwForm.reset();
    pwMsg.classList.remove('border-left-red');
    pwMsg.classList.add('border-left-green');
    showPw('Password updated successfully.');
  } catch (err) {
    pwMsg.classList.remove('border-left-green');
    pwMsg.classList.add('border-left-red');
    showPw(err.message);
  }
});

// ----------------------- Two-factor auth -----------------------
let twofaData = null;

function renderTwoFA(u) {
  const view = document.getElementById('twofaView');
  clear(view);

  if (!u.totp_enabled) {
    const p = el('p', 'muted', 'Two-factor authentication is OFF.');
    view.appendChild(p);
    const btn = el('button', 'btn', 'SET UP 2FA');
    btn.onclick = () => setupTwoFA();
    view.appendChild(btn);
    return;
  }

  const p = el('p', 'muted', 'Two-factor authentication is ON. You will be asked for a code at login.');
  view.appendChild(p);
  const form = el('form');
  form.innerHTML = `
    <div class="field">
      <label for="twofa_pw">Current password (required to disable)</label>
      <input id="twofa_pw" type="password" autocomplete="current-password" required>
    </div>`;
  const disBtn = el('button', 'btn danger', 'DISABLE 2FA');
  disBtn.type = 'button';
  disBtn.onclick = () => disableTwoFA(document.getElementById('twofa_pw').value);
  form.appendChild(disBtn);
  view.appendChild(form);
}

async function setupTwoFA() {
  const view = document.getElementById('twofaView');
  clear(view);
  const msg = document.getElementById('twofaMsg');
  msg.classList.add('hide');

  const data = await api('/api/auth/2fa/setup');
  twofaData = data;

  const step = el('div');
  step.appendChild(el('p', 'muted', 'Scan the QR in your authenticator app, or enter this secret manually:'));
  step.appendChild(el('p', 'secret-code', data.secret));
  step.appendChild(el('p', 'muted', 'Secret URI (otpauth): ' + data.otpauth_uri));

  const form = el('form');
  form.innerHTML = `
    <div class="field">
      <label for="twofa_code">Enter the 6-digit code from your app</label>
      <input id="twofa_code" type="text" autocomplete="one-time-code" maxlength="6" required>
    </div>`;
  const verifyBtn = el('button', 'btn', 'ENABLE 2FA');
  verifyBtn.type = 'button';
  verifyBtn.onclick = async () => {
    try {
      await post('/api/auth/2fa/enable', { code: document.getElementById('twofa_code').value.trim() });
      await loadAccount();
    } catch (err) {
      showTwoFA(err.message);
    }
  };
  form.appendChild(verifyBtn);
  step.appendChild(form);
  view.appendChild(step);
}

async function disableTwoFA(password) {
  try {
    await post('/api/auth/2fa/disable', { password });
    await loadAccount();
  } catch (err) {
    showTwoFA(err.message);
  }
}

function showTwoFA(err) {
  document.getElementById('twofaText').textContent = err;
  document.getElementById('twofaMsg').classList.remove('hide');
}

// ----------------------- Login history -----------------------
async function loadLoginHistory() {
  const rows = await api('/api/auth/login-history');
  const box = document.getElementById('loginHistory');
  clear(box);
  if (!rows.length) {
    box.appendChild(el('p', 'muted', 'No login activity recorded yet.'));
    return;
  }
  const table = el('table', 'tbl');
  const thead = el('thead');
  const hr = el('tr');
  ['When', 'IP Address', 'Method', 'Result', 'User-Agent'].forEach((h) => {
    hr.appendChild(el('th', null, h));
  });
  thead.appendChild(hr);
  table.appendChild(thead);
  const tbody = el('tbody');
  rows.forEach((r) => {
    const tr = el('tr');
    tr.appendChild(el('td', null, r.created_at ? new Date(r.created_at).toLocaleString() : '-'));
    tr.appendChild(el('td', null, r.ip_address || '-'));
    tr.appendChild(el('td', null, r.method || 'PASSWORD'));
    tr.appendChild(el('td', null, r.success ? '✅ Success' : '❌ Failed'));
    tr.appendChild(el('td', 'muted', (r.user_agent || '-').slice(0, 60)));
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  box.appendChild(table);
}

// ----------------------- User management (MANAGER+) -----------------------
// Lets Admin/Manager assign the position/role and approve or deactivate
// accounts. New self-registrations stay inactive until an admin verifies them.
const MY_ROLE = window.SMARTSHELF_ROLE || 'STAFF';
const ME_ID = Number(window.SMARTSHELF_ME) || 0;
const ROLE_NAMES = {
  ADMIN: 'Admin', MANAGER: 'Manager', BILLER: 'Biller',
  CASHIER: 'Cashier', STAFF: 'Staff', USER: 'User',
};

function roleColor(r) {
  return { ADMIN: 'red', MANAGER: 'orange', BILLER: 'yellow',
           CASHIER: 'green', STAFF: 'blue', USER: 'blue' }[r] || 'blue';
}

function roleOptions(selected) {
  const order = MY_ROLE === 'ADMIN'
    ? ['USER', 'STAFF', 'CASHIER', 'BILLER', 'MANAGER', 'ADMIN']
    : ['USER', 'STAFF', 'CASHIER', 'BILLER', 'MANAGER'];
  return order
    .map((r) => `<option value="${r}"${r === selected ? ' selected' : ''}>${ROLE_NAMES[r]}</option>`)
    .join('');
}

function usersMsg(text, ok) {
  const box = document.getElementById('usersMsg');
  document.getElementById('usersText').textContent = text;
  box.classList.remove('hide');
  box.classList.toggle('border-left-red', !ok);
  box.classList.toggle('border-left-green', ok);
}

async function loadUsers() {
  const data = await api('/api/auth/users');
  const box = document.getElementById('usersList');
  clear(box);
  if (!data.items.length) {
    box.appendChild(el('p', 'muted', 'No users yet.'));
    return;
  }
  const table = el('table', 'tbl');
  const thead = el('thead');
  const hr = el('tr');
  ['User', 'Position', 'Status', 'Last Login', 'Actions'].forEach((h) => hr.appendChild(el('th', null, h)));
  thead.appendChild(hr);
  table.appendChild(thead);
  const tbody = el('tbody');
  data.items.forEach((u) => tbody.appendChild(userRow(u)));
  table.appendChild(tbody);
  box.appendChild(table);
}

function userRow(u) {
  const isMe = u.id === ME_ID;
  const tr = el('tr');

  const nameCell = el('td');
  nameCell.appendChild(el('strong', null, u.full_name || u.username));
  nameCell.appendChild(el('p', 'muted', `@${u.username}${u.email ? ' · ' + u.email : ''}${isMe ? ' · you' : ''}`));
  tr.appendChild(nameCell);

  const roleCell = el('td');
  roleCell.appendChild(pill(u.role, roleColor(u.role)));
  tr.appendChild(roleCell);

  const statusCell = el('td');
  if (u.is_active) statusCell.appendChild(pill('Active', 'green'));
  else if (u.must_change_password) statusCell.appendChild(pill('Pending', 'orange'));
  else statusCell.appendChild(pill('Disabled', 'red'));
  tr.appendChild(statusCell);

  tr.appendChild(el('td', null, u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Never'));

  const actions = el('td');
  const btns = el('div');
  btns.style.display = 'flex';
  btns.style.gap = '.35rem';
  btns.style.flexWrap = 'wrap';
  btns.style.alignItems = 'center';
  if (isMe) {
    btns.appendChild(el('span', 'muted', 'This is your account'));
  } else {
    const sel = el('select');
    sel.innerHTML = roleOptions(u.role);
    btns.appendChild(sel);
    const saveBtn = el('button', 'btn', 'SAVE ROLE');
    saveBtn.style.padding = '.3rem .55rem';
    saveBtn.style.fontSize = '.72rem';
    saveBtn.onclick = () => saveRole(u.id, sel.value);
    btns.appendChild(saveBtn);

    const actBtn = u.is_active ? el('button', 'btn danger', 'DEACTIVATE') : el('button', 'btn', 'APPROVE');
    actBtn.style.padding = '.3rem .55rem';
    actBtn.style.fontSize = '.72rem';
    actBtn.onclick = () => setActive(u.id, !u.is_active);
    btns.appendChild(actBtn);

    if (MY_ROLE === 'ADMIN') {
      const disBtn = el('button', 'btn danger', 'DISABLE');
      disBtn.style.padding = '.3rem .55rem';
      disBtn.style.fontSize = '.72rem';
      disBtn.onclick = () => del('/api/auth/users/' + u.id).then(loadUsers);
      btns.appendChild(disBtn);
    }
  }
  actions.appendChild(btns);
  tr.appendChild(actions);
  return tr;
}

async function saveRole(id, role) {
  try {
    await put('/api/auth/users/' + id, { role });
    usersMsg('Position updated.', true);
    await loadUsers();
  } catch (err) {
    usersMsg(err.message, false);
  }
}

async function setActive(id, is_active) {
  try {
    await put('/api/auth/users/' + id, { is_active });
    usersMsg(is_active ? 'Account approved - the user can now log in.' : 'Account deactivated.', true);
    await loadUsers();
  } catch (err) {
    usersMsg(err.message, false);
  }
}

const addUserForm = document.getElementById('addUserForm');
if (addUserForm) {
  addUserForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(addUserForm);
    const body = {
      username: fd.get('u_username').trim(),
      full_name: (fd.get('u_full_name') || '').trim(),
      email: (fd.get('u_email') || '').trim(),
      password: fd.get('u_password'),
      role: fd.get('u_role'),
    };
    try {
      await post('/api/auth/users', body);
      addUserForm.reset();
      usersMsg('User created.', true);
      await loadUsers();
    } catch (err) {
      usersMsg(err.message, false);
    }
  });
}

loadAccount().catch((e) => console.error(e));
loadLoginHistory().catch((e) => console.error(e));
if (document.getElementById('usersList')) {
  loadUsers().catch((e) => console.error(e));
}
