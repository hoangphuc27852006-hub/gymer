/* ============================================================
   main.js — Client-side interactions for Gym Management System
   ============================================================ */

'use strict';

// ── DOM Ready ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  // Auto-dismiss flash alerts after 5 seconds
  initAlertAutoDismiss();

  // Sidebar mobile toggle
  initMobileToggle();

  // Confirm dangerous actions
  initConfirmActions();

  // Package info preview on buy page
  initPackagePreview();

  // Account role/linked-entity form
  initAccountForm();

  // Active sidebar link highlight
  highlightActiveNav();

  // Checkin page live clock
  initLiveClock();

  // Body stat chart (if canvas exists)
  initBodyStatChart();

  updateDurations();
  setInterval(updateDurations, 1000);

});


// ── Flash alerts auto-dismiss ────────────────────────────────
function initAlertAutoDismiss() {
  const alerts = document.querySelectorAll('.alert-auto-dismiss');
  alerts.forEach(el => {
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(el);
      bsAlert.close();
    }, 5000);
  });
}


// ── Mobile sidebar ───────────────────────────────────────────
function initMobileToggle() {
  const toggler = document.getElementById('sidebar-toggler');
  const sidebar = document.getElementById('sidebar');
  if (!toggler || !sidebar) return;

  toggler.addEventListener('click', () => sidebar.classList.toggle('show'));

  // Close sidebar on outside click
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !toggler.contains(e.target)) {
      sidebar.classList.remove('show');
    }
  });
}


// ── Confirm dangerous actions ────────────────────────────────
function initConfirmActions() {
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', function (e) {
      const msg = this.dataset.confirm || 'Bạn có chắc chắn muốn thực hiện thao tác này?';
      if (!confirm(msg)) {
        e.preventDefault();
        e.stopPropagation();
      }
    });
  });

  // Forms with data-confirm
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', function (e) {
      const msg = this.dataset.confirm || 'Bạn có chắc chắn?';
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
}


// ── Package buy page: show package info ─────────────────────
function initPackagePreview() {
  const goiSelect = document.getElementById('ma_goi');
  const infoBox   = document.getElementById('goi-info-box');
  if (!goiSelect || !infoBox) return;

  // Embed package data as JSON in the page via data-packages attribute
  const packagesData = JSON.parse(goiSelect.dataset.packages || '[]');

  goiSelect.addEventListener('change', function () {
    const id  = parseInt(this.value);
    const goi = packagesData.find(g => g.id === id);

    if (goi) {
      infoBox.innerHTML = `
        <div class="alert alert-info border-0" style="border-radius:10px;">
          <div class="row g-2">
            <div class="col-6">
              <small class="text-muted">Thời hạn</small>
              <div class="fw-600">${goi.thoi_han} ngày</div>
            </div>
            <div class="col-6">
              <small class="text-muted">Giá tiền</small>
              <div class="fw-600 text-danger">${formatVND(goi.gia_tien)}</div>
            </div>
            <div class="col-6">
              <small class="text-muted">Số buổi PT kèm</small>
              <div class="fw-600">${goi.so_buoi_pt} buổi</div>
            </div>
          </div>
        </div>
      `;
      infoBox.style.display = 'block';
    } else {
      infoBox.style.display = 'none';
    }
  });
}


// ── Account form: show/hide fields by role ───────────────────
function initAccountForm() {
  const vaiTroSelect = document.getElementById('vai_tro');
  if (!vaiTroSelect) return;

  const groups = {
    hoivien:  document.getElementById('group-hv'),
    nhanvien: document.getElementById('group-nv'),
    pt:       document.getElementById('group-pt'),
  };

  function updateGroups() {
    const val = vaiTroSelect.value;
    Object.entries(groups).forEach(([key, el]) => {
      if (!el) return;
      el.style.display = key === val ? 'block' : 'none';
      // Remove required from hidden selects
      const sel = el.querySelector('select');
      if (sel) sel.required = key === val && val !== 'admin';
    });
  }

  vaiTroSelect.addEventListener('change', updateGroups);
  updateGroups();
}


// ── Highlight active sidebar link ────────────────────────────
function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('#sidebar .nav-link').forEach(link => {
    if (link.getAttribute('href') && path.startsWith(link.getAttribute('href'))) {
      link.classList.add('active');
    }
  });
}


// ── Live clock on check-in page ──────────────────────────────
function initLiveClock() {
  const clock = document.getElementById('live-clock');
  if (!clock) return;

  function tick() {
    const now  = new Date();
    const time = now.toLocaleTimeString('vi-VN');
    const dt   = now.toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    clock.textContent = `${dt} — ${time}`;
  }

  tick();
  setInterval(tick, 1000);
}


// ── Body stat chart (Chart.js) ───────────────────────────────
function initBodyStatChart() {
  const canvas = document.getElementById('body-stat-chart');
  if (!canvas) return;

  const raw = JSON.parse(canvas.dataset.stats || '[]');
  if (!raw.length) return;

  const labels    = raw.map(r => r.date);
  const canNang   = raw.map(r => r.can_nang);
  const phanTramMo = raw.map(r => r.phan_tram_mo);

  new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Cân nặng (kg)',
          data: canNang,
          borderColor: '#c0392b',
          backgroundColor: 'rgba(192,57,43,.1)',
          tension: .4,
          yAxisID: 'y',
        },
        {
          label: '% Mỡ cơ thể',
          data: phanTramMo,
          borderColor: '#e67e22',
          backgroundColor: 'rgba(230,126,34,.1)',
          tension: .4,
          yAxisID: 'y1',
        }
      ]
    },
    options: {
      responsive: true,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { position: 'top' },
        tooltip: { callbacks: {
          label: ctx => ctx.dataset.label + ': ' + ctx.parsed.y
        }}
      },
      scales: {
        y:  { type: 'linear', display: true, position: 'left',  title: { display: true, text: 'Cân nặng (kg)' }},
        y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: '% Mỡ' },
               grid: { drawOnChartArea: false }}
      }
    }
  });
}


// ── Utility ──────────────────────────────────────────────────
function formatVND(value) {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency', currency: 'VND', minimumFractionDigits: 0
  }).format(value);
}


// ── Duration display (checkin duration) ─────────────────────
function parseCheckinTime(str) {
  if (!str) return null;
  const parsed = new Date(str);
  if (!isNaN(parsed.getTime())) return parsed;
  const fallback = new Date(String(str).replace(' ', 'T'));
  return isNaN(fallback.getTime()) ? null : fallback;
}

function updateDurations() {
  document.querySelectorAll('[data-checkin-time]').forEach(el => {
    const checkin = parseCheckinTime(el.dataset.checkinTime);
    if (!checkin) return;
    const mins = Math.max(0, Math.floor((Date.now() - checkin.getTime()) / 60000));
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    const text = h > 0 ? `${h}g ${m}p` : `${m} phút`;
    el.innerHTML = `<i class="fa-solid fa-clock"></i> ${text}`;
  });
}
