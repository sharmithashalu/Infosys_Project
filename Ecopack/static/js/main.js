/* =====================================================
   EcoInsight Pro — Main JavaScript
   ===================================================== */

const API_URL = '/api';
const INR_RATE = 83.5; // Conversion rate: 1 USD = 83.5 INR

/* ── Theme Toggle ── */
const html       = document.documentElement;
const themeBtn   = document.getElementById('themeToggle');
const iconSun    = document.getElementById('icon-sun');
const iconMoon   = document.getElementById('icon-moon');

function applyTheme(theme) {
  html.setAttribute('data-theme', theme);
  localStorage.setItem('ecoTheme', theme);
  if (iconSun && iconMoon) {
    iconSun.style.display  = theme === 'dark' ? 'none'  : '';
    iconMoon.style.display = theme === 'dark' ? ''      : 'none';
  }
  // Re-render Plotly charts if on dashboard
  if (window.__lastDashData) renderCharts(window.__lastDashData);
}

// Restore saved theme
applyTheme(localStorage.getItem('ecoTheme') || 'light');

themeBtn?.addEventListener('click', () => {
  applyTheme(html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
});

/* ── Hamburger ── */
document.getElementById('hamburger')?.addEventListener('click', () => {
  document.getElementById('navLinks')?.classList.toggle('open');
});

/* ── Range Sliders ── */
function initRangeSlider(id, displayId, suffix, min, max) {
  const slider  = document.getElementById(id);
  const display = document.getElementById(displayId);
  if (!slider || !display) return;

  function update() {
    const pct = ((slider.value - min) / (max - min)) * 100;
    slider.style.setProperty('--pct', pct + '%');
    display.textContent = slider.value + (suffix || '');
  }

  slider.addEventListener('input', update);
  update();
}

initRangeSlider('weight',    'weightVal',    ' kg', 0.1, 50);
initRangeSlider('durability','durabilityVal', '',    1,  10);

/* ── Form Submit → AI Recommendation ── */
document.getElementById('recommendationForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const runBtn  = document.getElementById('runBtn');
  const payload = {
    product_name:      document.getElementById('productName').value  || 'My Product',
    industry:          document.getElementById('industry').value,
    weight_kg:         parseFloat(document.getElementById('weight').value),
    durability_needed: parseInt(document.getElementById('durability').value)
  };

  // Loading state
  runBtn.classList.add('loading');

  const container = document.getElementById('resultsContainer');
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon" style="animation:spin 1.2s linear infinite;border-style:solid;border-width:4px;border-color:rgba(34,197,94,0.25);border-top-color:#22c55e;background:transparent;width:60px;height:60px;"></div>
      <h3 style="margin-top:1.2rem">AI Evaluating Materials…</h3>
      <p>Analysing 500+ sustainable options across cost, CO₂ & recyclability</p>
    </div>`;

  try {
    const res  = await fetch(`${API_URL}/recommend`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload)
    });
    const data = await res.json();

    if (data.status === 'success') {
      displayRecommendations(data.recommendations, payload.product_name);
    } else {
      showError(container, data.error || 'Unknown error from API');
    }
  } catch (err) {
    showError(container, 'Cannot reach server. Make sure Flask backend is running on port 5001.');
  } finally {
    runBtn.classList.remove('loading');
  }
});

function showError(container, msg) {
  container.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon" style="background:rgba(239,68,68,0.10);border-color:rgba(239,68,68,0.25)">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="1" fill="#ef4444"/>
        </svg>
      </div>
      <h3 style="color:#ef4444">Analysis Failed</h3>
      <p>${msg}</p>
    </div>`;
}

/* ── Display Recommendation Cards ── */
function displayRecommendations(recs, productName) {
  const container = document.getElementById('resultsContainer');

  if (!recs || recs.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r="1" fill="#f59e0b"/></svg></div>
        <h3>No Matches Found</h3>
        <p>Try reducing the weight or durability requirements to see material options.</p>
      </div>`;
    return;
  }

  let html = `
    <div class="results-header">
      <span class="results-title">AI Recommendations · <em>${escHtml(productName)}</em></span>
      <span class="results-count">${recs.length} materials found</span>
    </div>
    <div class="rec-cards-list">`;

  recs.forEach((item, i) => {
    const score     = Math.min(10, parseFloat(item.suitability_score || 0));
    const displayS  = score.toFixed(1);
    const scoreCls  = score >= 7 ? 'score-high' : score >= 4 ? 'score-medium' : 'score-low';
    const scoreColor= score >= 7 ? '#22c55e'   : score >= 4 ? '#f59e0b'      : '#ef4444';

    // SVG ring: circumference of r=26 circle ≈ 163.36
    const r   = 26;
    const circ= 2 * Math.PI * r;          // 163.36
    const pct = (score / 10) * circ;
    const gap = circ - pct;

    // Normalise metrics to 0-100 for progress bars
    const recycPct    = Math.min(100, parseFloat(item.recyclability   || 0));
    const strengthPct = Math.min(100, (parseFloat(item.strength || 0) / 2000) * 100);
    const costNorm    = Math.min(100, Math.max(0, 100 - (parseFloat(item.cost || 50) / 100) * 100));
    const co2Norm     = Math.min(100, Math.max(0, 100 - (parseFloat(item.co2_emission || 300) / 600) * 100));

    const rankLabels = ['#1 Top Pick', '#2 Runner-up', '#3 Recommended', '#4 Good Option', '#5 Alternative'];

    html += `
      <div class="rec-card ${scoreCls}" style="animation-delay:${i * 0.08}s">
        <!-- Top row -->
        <div class="rec-card-top">
          <div class="rec-card-info">
            <div class="rec-rank">${rankLabels[i] || `#${i+1}`}</div>
            <div class="rec-name">${escHtml(item.material)}</div>
            <div class="rec-industry">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="margin-right:3px"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/></svg>
              ${escHtml(item.industry)} · Capacity: ${item.weight_capacity}kg
            </div>
          </div>

          <!-- Circular Eco Score -->
          <div class="eco-score-ring ${scoreCls}">
            <svg viewBox="0 0 62 62">
              <circle class="eco-ring-bg" cx="31" cy="31" r="${r}"/>
              <circle class="eco-ring-fill"
                cx="31" cy="31" r="${r}"
                stroke-dasharray="${pct} ${gap}"
                stroke-dashoffset="0"
                style="stroke:${scoreColor}"
              />
            </svg>
            <div class="eco-score-val">
              <span class="eco-score-num" style="color:${scoreColor}">${displayS}</span>
              <span class="eco-score-label">/ 10</span>
            </div>
          </div>
        </div>

        <!-- Metric Boxes -->
        <div class="rec-metrics">
          <div class="metric">
            <div class="metric-icon">💰</div>
            <div class="metric-val">₹${(parseFloat(item.cost) * INR_RATE).toFixed(2)}</div>
            <div class="metric-key">Cost</div>
          </div>
          <div class="metric">
            <div class="metric-icon">🌿</div>
            <div class="metric-val">${parseFloat(item.co2_emission).toFixed(1)} kg</div>
            <div class="metric-key">CO₂</div>
          </div>
          <div class="metric">
            <div class="metric-icon">💪</div>
            <div class="metric-val">${parseFloat(item.strength || 0).toFixed(0)} psi</div>
            <div class="metric-key">Strength</div>
          </div>
          <div class="metric">
            <div class="metric-icon">♻️</div>
            <div class="metric-val">${parseFloat(item.recyclability).toFixed(0)}%</div>
            <div class="metric-key">Recyclable</div>
          </div>
        </div>

        <!-- Progress Bars -->
        <div class="rec-bars">
          ${bar('Recyclability', recycPct,    '#22c55e')}
          ${bar('Eco Score',     score * 10,  scoreColor)}
          ${bar('Cost Eff.',     costNorm,    '#3b82f6')}
          ${bar('Low CO₂',       co2Norm,     '#10b981')}
        </div>

        <!-- Tags -->
        <div class="rec-tags">
          ${item.recyclability >= 70 ? '<span class="rec-tag green">♻️ Highly Recyclable</span>' : ''}
          ${item.co2_emission   <  200 ? '<span class="rec-tag green">🌿 Low Emission</span>'     : ''}
          ${item.cost           <  20  ? '<span class="rec-tag green">💰 Budget Friendly</span>'  : ''}
          <span class="rec-tag">Cap: ${item.weight_capacity}kg</span>
          <span class="rec-tag">Dur: ${item.durability}/10</span>
        </div>
      </div>`;
  });

  html += `</div>`;
  container.innerHTML = html;

  // Animate progress bars after paint
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      container.querySelectorAll('.bar-fill[data-w]').forEach(el => {
        el.style.width = el.dataset.w + '%';
      });
    });
  });
}

function bar(label, pct, color) {
  const p = Math.min(100, Math.max(0, pct)).toFixed(1);
  return `
    <div class="bar-row">
      <span class="bar-label">${label}</span>
      <div class="bar-track">
        <div class="bar-fill" data-w="${p}" style="background:${color};width:0%"></div>
      </div>
      <span class="bar-pct">${Math.round(p)}%</span>
    </div>`;
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* ===================================================
   DASHBOARD
   =================================================== */
async function loadDashboardData() {
  const btn = document.getElementById('refreshBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Syncing…'; }

  try {
    const res  = await fetch(`${API_URL}/analytics`);
    const data = await res.json();
    window.__lastDashData = data;

    setText('matCount', data.total_materials);
    setText('co2Red',   data.co2_reduction  + '%');
    setText('costSav',  data.cost_savings   + '%');
    setText('avgCost',  '₹' + (parseFloat(data.total_avg_cost) * INR_RATE).toFixed(2));

    renderCharts(data);
  } catch (err) {
    console.error('Dashboard load failed:', err);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/></svg> Sync Data`; }
  }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ── Plotly Charts ── */
function renderCharts(data) {
  const dark     = html.getAttribute('data-theme') === 'dark';
  const fontCol  = dark ? '#86efac' : '#4b7a52';
  const gridCol  = dark ? 'rgba(34,197,94,0.08)' : 'rgba(34,197,94,0.12)';
  const bgTransp = 'transparent';
  const font     = { family: 'Inter, Poppins, sans-serif', color: fontCol, size: 12 };
  const paperBg  = bgTransp;
  const plotBg   = bgTransp;

  const baseLayout = {
    paper_bgcolor: paperBg,
    plot_bgcolor:  plotBg,
    font,
    margin: { t: 20, b: 55, l: 55, r: 20 },
    xaxis: { gridcolor: gridCol, zeroline: false, tickfont: { size: 11 } },
    yaxis: { gridcolor: gridCol, zeroline: false }
  };
  const cfg = { responsive: true, displayModeBar: false };

  // CO2 Bar Chart
  Plotly.react('co2Chart', [{
    x: Object.keys(data.avg_co2_by_type),
    y: Object.values(data.avg_co2_by_type),
    type: 'bar',
    marker: {
      color: Object.values(data.avg_co2_by_type).map((_, i) =>
        `rgba(34,${140 + i * 18},94,0.85)`),
      line: { color: '#22c55e', width: 1 }
    },
    hovertemplate: '<b>%{x}</b><br>CO₂: %{y:.1f} kg<extra></extra>'
  }], {
    ...baseLayout,
    yaxis: { ...baseLayout.yaxis, title: { text: 'Avg CO₂ (kg)', font: { size: 11 } } }
  }, cfg);

  // Cost Donut Chart
  Plotly.react('costChart', [{
    labels: Object.keys(data.avg_cost_by_industry),
    values: Object.values(data.avg_cost_by_industry).map(v => v * INR_RATE),
    type:   'pie',
    hole:   0.55,
    marker: {
      colors: ['#22c55e','#16a34a','#4ade80','#86efac','#bbf7d0'],
      line:   { color: dark ? '#071a0e' : '#f0fdf4', width: 2 }
    },
    textinfo:             'label+percent',
    insidetextorientation:'radial',
    hovertemplate:        '<b>%{label}</b><br>Avg Cost: ₹%{value:.2f}<extra></extra>'
  }], {
    paper_bgcolor: paperBg,
    font,
    margin: { t: 20, b: 20, l: 20, r: 20 },
    legend: { orientation: 'h', y: -0.15, font: { size: 11 } },
    showlegend: true
  }, cfg);

  // Trend Line Chart
  const sortedDates = Object.keys(data.usage_trends).sort();
  Plotly.react('trendChart', [{
    x:    sortedDates,
    y:    sortedDates.map(d => data.usage_trends[d]),
    type: 'scatter',
    mode: 'lines+markers',
    line:       { color: '#22c55e', shape: 'spline', width: 3 },
    marker:     { size: 7, color: '#22c55e', line: { color: dark ? '#071a0e' : '#f0fdf4', width: 2 } },
    fill:       'tozeroy',
    fillcolor:  dark ? 'rgba(34,197,94,0.07)' : 'rgba(34,197,94,0.10)',
    hovertemplate: '<b>%{x}</b><br>Requests: %{y}<extra></extra>'
  }], {
    ...baseLayout,
    xaxis: { ...baseLayout.xaxis, title: { text: 'Date', font: { size: 11 } } },
    yaxis: { ...baseLayout.yaxis, title: { text: 'Volume', font: { size: 11 } } }
  }, cfg);
}

/* ── Export ── */
function exportData(format) {
  window.location.href = `${API_URL}/export/${format}`;
}
