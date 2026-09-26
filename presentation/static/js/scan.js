// SmartShelf Barcode Scanner & Quick Intake Controller
'use strict';

let html5QrCode = null;
let isScanning = false;
let currentCameraId = null;
let availableCameras = [];
let lastScannedCode = null;

// Audio beep feedback for scanner confirmation
function playBeep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, ctx.currentTime); // 880Hz (A5)
    gain.gain.setValueAtTime(0.15, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.12);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + 0.12);
  } catch (e) {
    // Audio context may be restricted before user gesture
  }
}

// -------------------------------------------------------------
// Scanner Lifecycle
// -------------------------------------------------------------
async function initScanner() {
  if (typeof Html5Qrcode === 'undefined') {
    updateStatus('Error: Barcode scanner library not loaded', 'red');
    return;
  }

  try {
    html5QrCode = new Html5Qrcode('reader');
    availableCameras = await Html5Qrcode.getCameras();
    if (availableCameras && availableCameras.length) {
      // Default to rear/back camera if found, otherwise first available
      const backCam = availableCameras.find(c =>
        c.label.toLowerCase().includes('back') || c.label.toLowerCase().includes('rear') || c.label.toLowerCase().includes('environment')
      );
      currentCameraId = backCam ? backCam.id : availableCameras[0].id;
      if (availableCameras.length > 1) {
        document.getElementById('toggleCameraBtn').style.display = 'inline-flex';
      }
    }
  } catch (err) {
    console.warn('Camera enumeration info:', err);
  }
}

async function startScanning() {
  if (!html5QrCode) await initScanner();
  if (!html5QrCode) return;

  const config = {
    fps: 10,
    qrbox: { width: 280, height: 180 },
    aspectRatio: 1.3333,
    formatsToSupport: [
      Html5QrcodeSupportedFormats.EAN_13,
      Html5QrcodeSupportedFormats.EAN_8,
      Html5QrcodeSupportedFormats.UPC_A,
      Html5QrcodeSupportedFormats.UPC_E,
      Html5QrcodeSupportedFormats.CODE_128,
      Html5QrcodeSupportedFormats.CODE_39,
      Html5QrcodeSupportedFormats.QR_CODE,
    ]
  };

  const cameraConfig = currentCameraId
    ? { deviceId: { exact: currentCameraId } }
    : { facingMode: 'environment' };

  try {
    document.getElementById('readerPlaceholder').style.display = 'none';
    await html5QrCode.start(
      cameraConfig,
      config,
      onBarcodeDecoded,
      (errorMessage) => {
        // Scanning frame without barcode - no action needed
      }
    );
    isScanning = true;
    updateStatus('Camera active · Scanning', 'green');
    document.getElementById('startScanBtn').style.display = 'none';
    document.getElementById('stopScanBtn').style.display = 'inline-flex';
  } catch (err) {
    console.error('Camera start error:', err);
    updateStatus('Camera access denied or unavailable', 'red');
    document.getElementById('readerPlaceholder').style.display = 'block';
    alert('Could not start camera. Please ensure camera permissions are granted in your browser, or use manual barcode entry.');
  }
}

async function stopScanning() {
  if (html5QrCode && isScanning) {
    try {
      await html5QrCode.stop();
    } catch (e) {
      console.warn('Error stopping scanner:', e);
    }
    isScanning = false;
    document.getElementById('readerPlaceholder').style.display = 'block';
    document.getElementById('startScanBtn').style.display = 'inline-flex';
    document.getElementById('stopScanBtn').style.display = 'none';
    updateStatus('Scanner paused', 'yellow');
  }
}

async function toggleCamera() {
  if (!availableCameras.length || availableCameras.length < 2) return;
  const currentIndex = availableCameras.findIndex(c => c.id === currentCameraId);
  const nextIndex = (currentIndex + 1) % availableCameras.length;
  currentCameraId = availableCameras[nextIndex].id;

  if (isScanning) {
    await stopScanning();
    await startScanning();
  }
}

function onBarcodeDecoded(decodedText, decodedResult) {
  if (!decodedText || decodedText === lastScannedCode) return;
  lastScannedCode = decodedText;

  playBeep();
  updateStatus(`Scanned: ${decodedText}`, 'blue');
  document.getElementById('manualBarcodeInput').value = decodedText;

  // Temporarily stop scanner stream so user can focus on batch entry
  stopScanning().catch(() => {});
  document.getElementById('restartScanBtn').style.display = 'inline-flex';

  triggerLookup(decodedText);
}

function updateStatus(text, tone) {
  const badge = document.getElementById('scanStatusBadge');
  if (!badge) return;
  badge.className = `pill ${tone || 'blue'}`;
  clear(badge);
  badge.appendChild(el('span', 'dot'));
  badge.appendChild(document.createTextNode(text));
}

// -------------------------------------------------------------
// Product Lookup & UI State Management
// -------------------------------------------------------------
async function triggerLookup(barcode) {
  const code = (barcode || '').trim();
  if (!code) return;

  updateStatus(`Looking up: ${code}...`, 'blue');

  try {
    const product = await api(`/api/products/lookup/${encodeURIComponent(code)}`);
    displayFoundProduct(product);
  } catch (err) {
    displayNotFound(code);
  }
}

function displayFoundProduct(p) {
  updateStatus(`Found: ${p.name}`, 'green');

  // Fill Product Card
  document.getElementById('resProdName').textContent = p.name;
  document.getElementById('resProdSku').textContent = p.sku;
  document.getElementById('resProdBarcode').textContent = p.barcode || '—';
  document.getElementById('resProdCat').textContent = p.category || 'General';
  document.getElementById('resProdStock').textContent = `${p.total_stock} ${p.unit || 'pcs'}`;

  const perishBadge = document.getElementById('prodPerishBadge');
  clear(perishBadge);
  if (p.is_perishable) {
    perishBadge.appendChild(pill('PERISHABLE', 'orange'));
  } else {
    perishBadge.appendChild(pill('NON-PERISHABLE', 'blue'));
  }

  // Auto-fill Inbound Batch Form
  document.getElementById('batchProductId').value = p.id;
  document.getElementById('batchCostInput').value = p.cost_price ? p.cost_price.toFixed(2) : '';

  // Auto-generate suggested batch code
  const todayStr = new Date().toISOString().slice(2, 10).replace(/-/g, '');
  const randCode = Math.floor(100 + Math.random() * 900);
  document.getElementById('batchCodeInput').value = `B-${todayStr}-${randCode}`;

  // Pre-calculate suggested expiry date if shelf life exists
  if (p.shelf_life_days && p.shelf_life_days > 0) {
    const exp = new Date();
    exp.setDate(exp.getDate() + p.shelf_life_days);
    document.getElementById('batchExpiryInput').value = exp.toISOString().slice(0, 10);
  } else {
    document.getElementById('batchExpiryInput').value = '';
  }

  // Set today as manufactured date
  document.getElementById('batchManufInput').value = new Date().toISOString().slice(0, 10);

  // Toggle visible cards
  document.getElementById('idleCard').style.display = 'none';
  document.getElementById('notFoundCard').style.display = 'none';
  document.getElementById('quickRegisterCard').style.display = 'none';
  document.getElementById('productResultCard').style.display = 'block';
  document.getElementById('batchEntryCard').style.display = 'block';

  // Focus quantity field
  setTimeout(() => {
    const qtyInput = document.getElementById('batchQtyInput');
    if (qtyInput) qtyInput.focus();
  }, 100);
}

function displayNotFound(barcode) {
  updateStatus(`Not Found: ${barcode}`, 'orange');

  document.getElementById('notFoundBarcode').textContent = barcode;
  document.getElementById('regBarcodeInput').value = barcode;
  document.getElementById('regNameInput').value = '';
  document.getElementById('regSkuInput').value = `SKU-${barcode.slice(-6)}`;

  document.getElementById('idleCard').style.display = 'none';
  document.getElementById('productResultCard').style.display = 'none';
  document.getElementById('batchEntryCard').style.display = 'none';
  document.getElementById('notFoundCard').style.display = 'block';
  document.getElementById('quickRegisterCard').style.display = 'none';
}

function showQuickRegister() {
  document.getElementById('notFoundCard').style.display = 'none';
  document.getElementById('quickRegisterCard').style.display = 'block';
  document.getElementById('regNameInput').focus();
}

function hideQuickRegister() {
  document.getElementById('quickRegisterCard').style.display = 'none';
  document.getElementById('notFoundCard').style.display = 'block';
}

function resetScanView() {
  lastScannedCode = null;
  document.getElementById('manualBarcodeInput').value = '';
  document.getElementById('productResultCard').style.display = 'none';
  document.getElementById('batchEntryCard').style.display = 'none';
  document.getElementById('notFoundCard').style.display = 'none';
  document.getElementById('quickRegisterCard').style.display = 'none';
  document.getElementById('idleCard').style.display = 'block';
  document.getElementById('restartScanBtn').style.display = 'none';
  updateStatus('Ready', 'blue');
}

// -------------------------------------------------------------
// Options & Form Submission
// -------------------------------------------------------------
async function loadDropdowns() {
  try {
    const [suppliers, locations, categories] = await Promise.all([
      api('/api/suppliers').catch(() => []),
      api('/api/locations').catch(() => []),
      api('/api/categories').catch(() => [])
    ]);

    const supSel = document.getElementById('batchSupplierSelect');
    if (supSel && suppliers && suppliers.length) {
      suppliers.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = `${s.name} (${s.contact_person || 'Supplier'})`;
        supSel.appendChild(opt);
      });
    }

    const locSel = document.getElementById('batchLocationSelect');
    if (locSel && locations && locations.length) {
      locations.forEach(l => {
        const opt = document.createElement('option');
        opt.value = l.id;
        opt.textContent = `${l.code} - ${l.name} (${l.zone || 'General'})`;
        locSel.appendChild(opt);
      });
    }

    const catSel = document.getElementById('regCatSelect');
    if (catSel && categories && categories.length) {
      categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name;
        catSel.appendChild(opt);
      });
    }
  } catch (e) {
    console.warn('Could not load select dropdown options:', e);
  }
}

// Quick Inbound Batch Form Submit
document.getElementById('quickBatchForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const payload = {
    product_id: parseInt(formData.get('product_id'), 10),
    batch_code: formData.get('batch_code'),
    quantity: parseInt(formData.get('quantity'), 10),
    cost_price: formData.get('cost_price') ? parseFloat(formData.get('cost_price')) : null,
    expiry_date: formData.get('expiry_date') || null,
    manufactured_date: formData.get('manufactured_date') || null,
    supplier_id: formData.get('supplier_id') ? parseInt(formData.get('supplier_id'), 10) : null,
    location_id: formData.get('location_id') ? parseInt(formData.get('location_id'), 10) : null,
    reference: formData.get('reference') || null,
    notes: 'Received via Barcode Scanner',
  };

  try {
    const res = await post('/api/inventory/receive', payload);
    alert(`Success! Received ${payload.quantity} units into batch ${payload.batch_code}.`);
    e.target.reset();
    resetScanView();
    // Offer to scan another
    document.getElementById('startScanBtn').click();
  } catch (err) {
    alert('Error receiving batch: ' + err.message);
  }
});

// Quick Register Form Submit
document.getElementById('quickRegisterForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  const payload = {
    name: formData.get('name'),
    sku: formData.get('sku'),
    barcode: formData.get('barcode') || null,
    category_id: formData.get('category_id') ? parseInt(formData.get('category_id'), 10) : null,
    unit: formData.get('unit') || 'pcs',
    unit_price: parseFloat(formData.get('unit_price') || 0),
    cost_price: parseFloat(formData.get('cost_price') || 0),
    shelf_life_days: formData.get('shelf_life_days') ? parseInt(formData.get('shelf_life_days'), 10) : null,
    storage_condition: formData.get('storage_condition') || 'AMBIENT',
    reorder_level: parseInt(formData.get('reorder_level') || 0, 10),
    is_perishable: formData.get('is_perishable') === 'on',
  };

  try {
    const newProduct = await post('/api/products', payload);
    alert(`Product "${newProduct.name}" registered successfully! Now enter inbound batch details.`);
    displayFoundProduct(newProduct);
  } catch (err) {
    alert('Error registering product: ' + err.message);
  }
});

// Manual Input Form Submit
document.getElementById('manualScanForm').addEventListener('submit', (e) => {
  e.preventDefault();
  const code = document.getElementById('manualBarcodeInput').value;
  triggerLookup(code);
});

// Event Listeners for Scanner Buttons
document.getElementById('startScanBtn').addEventListener('click', () => {
  startScanning();
});

document.getElementById('stopScanBtn').addEventListener('click', () => {
  stopScanning();
});

document.getElementById('toggleCameraBtn').addEventListener('click', () => {
  toggleCamera();
});

document.getElementById('restartScanBtn').addEventListener('click', () => {
  resetScanView();
  startScanning();
});

// Initial load
loadDropdowns();
initScanner();
