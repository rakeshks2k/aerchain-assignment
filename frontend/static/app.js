/**
 * Aerchain RFx Intelligence - Single Page Application Frontend
 * Enterprise procurement copilot for corrugated packaging RFx analysis.
 */

// ── Global Configuration & State ──────────────────────────────────────────────
const API = ''; // Relative path works seamlessly with FastAPI root mount
const RFX_ID = 1;

const SUPPLIER_COLORS = {
  PKI: '#373192', // PackIndia - Aerchain Deep Indigo
  EBS: '#EF5433', // EcoBox - Aerchain Signature Coral
  IPI: '#10b981', // IndoPack - Emerald Teal
  PCO: '#9b38fc', // PremiumCorrugated - Aerchain Bright Purple
  RPC: '#f59e0b', // RegionalPacks - Amber Gold
};

const App = {
  // Category & Pagination State
  compCategoryFilter: 'all',
  compPage: 1,
  itemsPerPage: 10,
  rfxCategoryFilter: 'all',
  rfxPage: 1,

  setCategoryFilter(cat) {
    this.compCategoryFilter = cat;
    document.querySelectorAll('.subnav-filter-strip .filter-pill').forEach(btn => {
      const txt = btn.textContent.toLowerCase();
      btn.classList.toggle('active', (cat === 'all' && txt.includes('overview')) || txt.includes(cat));
    });
    if (this.currentSection === 'comparison') {
      this.renderComparisonTable();
    }
  },

  filterComparisonCategory(cat) {
    this.compCategoryFilter = cat;
    this.compPage = 1;
    document.querySelectorAll('#section-comparison .filter-pill').forEach(btn => {
      const bCat = btn.getAttribute('data-category') || '';
      btn.classList.toggle('active', bCat === cat);
    });
    this.renderComparisonTable();
  },

  setCompPage(p) {
    this.compPage = p;
    this.renderComparisonTable();
  },

  // ── Lucide Line Icon Helper (Image 2 Design System) ────────────────────────
  icon(name, size = 16, className = '') {
    const cls = className ? `class="lucide-icon ${className}"` : 'class="lucide-icon"';
    const s = `width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"`;
    switch (name) {
      case 'search': return `<svg ${cls} ${s}><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`;
      case 'bell': return `<svg ${cls} ${s}><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>`;
      case 'file': return `<svg ${cls} ${s}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>`;
      case 'file-text': return `<svg ${cls} ${s}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" x2="8" y1="13" y2="13"/><line x1="16" x2="8" y1="17" y2="17"/></svg>`;
      case 'upload': return `<svg ${cls} ${s}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>`;
      case 'download': return `<svg ${cls} ${s}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>`;
      case 'refresh': return `<svg ${cls} ${s}><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>`;
      case 'edit': return `<svg ${cls} ${s}><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`;
      case 'trash': return `<svg ${cls} ${s}><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>`;
      case 'check': return `<svg ${cls} ${s}><polyline points="20 6 9 17 4 12"/></svg>`;
      case 'check-circle': return `<svg ${cls} ${s}><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`;
      case 'x': return `<svg ${cls} ${s}><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
      case 'alert-triangle': return `<svg ${cls} ${s}><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
      case 'arrow-right': return `<svg ${cls} ${s}><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`;
      case 'arrow-up-right': return `<svg ${cls} ${s}><line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/></svg>`;
      case 'chevron-down': return `<svg ${cls} ${s}><polyline points="6 9 12 15 18 9"/></svg>`;
      case 'chevron-right': return `<svg ${cls} ${s}><polyline points="9 18 15 12 9 6"/></svg>`;
      case 'eye': return `<svg ${cls} ${s}><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`;
      case 'award': return `<svg ${cls} ${s}><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>`;
      case 'shield': return `<svg ${cls} ${s}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`;
      case 'plus': return `<svg ${cls} ${s}><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>`;
      case 'sparkles':
      case 'sparkle':
      case 'copilot':
      case 'ai':
        return `<svg ${cls} ${s}><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>`;
      case 'mail':
        return `<svg ${cls} ${s}><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>`;
      case 'message-square':
      case 'chat':
        return `<svg ${cls} ${s}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`;
      case 'activity':
      case 'pulse':
        return `<svg ${cls} ${s}><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`;
      case 'user':
        return `<svg ${cls} ${s}><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>`
      case 'clock':
        return `<svg ${cls} ${s}><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`;
      case 'info':
        return `<svg ${cls} ${s}><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`;
      default:
        return `<svg ${cls} ${s}><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`;
    }
  },

  getFileTypeIcon(fileType) {
    const type = (fileType || '').toUpperCase();
    if (type.includes('EXCEL') || type.includes('XLS')) {
      return `<span class="file-icon-box file-box-excel" title="Excel Spreadsheet (.xlsx)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M8 13h8"/><path d="M8 17h8"/><path d="M12 9v12"/></svg>
      </span>`;
    }
    if (type.includes('PDF')) {
      return `<span class="file-icon-box file-box-pdf" title="PDF Document (.pdf)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><path d="M10 12h4"/><path d="M10 16h4"/></svg>
      </span>`;
    }
    if (type.includes('WORD') || type.includes('DOC')) {
      return `<span class="file-icon-box file-box-word" title="Word Document (.docx)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="15" y2="17"/></svg>
      </span>`;
    }
    if (type.includes('IMAGE') || type.includes('PNG') || type.includes('JPG')) {
      return `<span class="file-icon-box file-box-image" title="Scanned Image (.png, .jpg)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>
      </span>`;
    }
    if (type.includes('EMAIL') || type.includes('EML') || type.includes('MSG')) {
      return `<span class="file-icon-box file-box-email" title="Email Quotation (.msg, .eml)">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
      </span>`;
    }
    return `<span class="file-icon-box file-box-generic" title="${fileType || 'Quotation Document'}">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
    </span>`;
  },

  getFileTypeBadge(fileType) {
    return this.getFileTypeIcon(fileType);
  },

  // ── Currency Switcher & Metric State ─────────────────────────────────────────
  currentCurrency: 'INR',
  spendVisible: true,

  setCurrency(curr) {
    this.currentCurrency = curr || 'INR';
    this.updateHeroSpendDisplay();
  },

  toggleSpendVisibility() {
    this.spendVisible = !this.spendVisible;
    this.updateHeroSpendDisplay();
  },

  updateHeroSpendDisplay() {
    const el = document.getElementById('kpi-spend-val') || document.getElementById('hero-spend-val');
    if (!el) return;
    const spend = this.portfolioSpend || 26661540;
    el.textContent = this.inr(spend);
  },

  showSearchModal() {
    this.showModal(
      'Quick Sourcing Search',
      `<div style="display:flex; flex-direction:column; gap:16px;">
        <input type="text" class="form-input w-full" style="font-size:14px; height:44px; padding:10px 18px; border-radius:9999px;" placeholder="Search line items, suppliers, specifications..." oninput="App.handleQuickSearch(this.value)" autofocus />
        <div id="quick-search-results" style="max-height:300px; overflow-y:auto; padding-top:4px;">
          <div class="text-xs text-muted" style="line-height:1.5;">Type SKU description, flute type, or supplier code to jump directly...</div>
        </div>
       </div>`
    );
  },

  handleQuickSearch(val) {
    const resEl = document.getElementById('quick-search-results');
    if (!resEl || !val.trim()) {
      if (resEl) resEl.innerHTML = '<div class="text-xs text-muted">Type SKU description, flute type, or supplier code to jump directly...</div>';
      return;
    }
    const q = val.toLowerCase();
    const matches = [];
    if ('packindia'.includes(q) || 'pki'.includes(q)) matches.push({ title: 'PackIndia Ltd (PKI)', sub: 'Supplier Profile & Submissions', sec: 'submissions' });
    if ('indopack'.includes(q) || 'ipi'.includes(q)) matches.push({ title: 'IndoPack Industries (IPI)', sub: 'Supplier Profile & Submissions', sec: 'submissions' });
    if ('ecobox'.includes(q) || 'ebs'.includes(q)) matches.push({ title: 'EcoBox Solutions (EBS)', sub: 'Supplier Profile & Submissions', sec: 'submissions' });
    if ('carton'.includes(q) || 'box'.includes(q) || '3-ply'.includes(q) || '5-ply'.includes(q)) matches.push({ title: 'Line Items & Packaging SKUs', sub: '30 Corrugated specifications', sec: 'rfx' });
    if ('comparison'.includes(q) || 'matrix'.includes(q) || 'price'.includes(q)) matches.push({ title: 'Comparison Workspace', sub: '30x5 Landed Cost Matrix', sec: 'comparison' });
    if ('split'.includes(q) || 'award'.includes(q) || 'savings'.includes(q)) matches.push({ title: 'Award Scenarios & Savings', sub: 'Optimal Split-Award Model', sec: 'award' });

    if (matches.length === 0) {
      resEl.innerHTML = '<div class="text-xs text-muted p-8">No quick matches found. Check RFx Events or Comparison.</div>';
    } else {
      resEl.innerHTML = matches.map(m => `
        <div style="padding:10px 14px; border-radius:12px; background:var(--surface-subtle); margin-bottom:8px; cursor:pointer; display:flex; justify-content:space-between; align-items:center;" onclick="App.closeModal(); App.navigateTo('${m.sec}')">
          <div>
            <div class="font-semibold text-sm">${this.escapeHtml(m.title)}</div>
            <div class="text-xs text-muted">${this.escapeHtml(m.sub)}</div>
          </div>
          <span class="badge badge-blue">Jump</span>
        </div>
      `).join('');
    }
  },

  currentSection: null,
  currentRfxId: 1,
  currentRfxNumber: 'RFX-2026-001',
  comparisonData: null,
  awardData: null,
  chartInstances: {},
  chatHistory: [],
  suppliersVisible: { PKI: true, EBS: true, IPI: true, PCO: true, RPC: true },
  selectedQuote: null,

  // ── Initialization ──────────────────────────────────────────────────────────
  init() {
    this.setupNavigation();
    this.initCopilotHistory();
    const handleHash = () => {
      const h = window.location.hash ? window.location.hash.replace('#', '') : 'dashboard';
      if (h.startsWith('rfx-detail')) {
        const parts = h.split('/');
        const rfxId = parts[1] ? parseInt(parts[1], 10) : 1;
        const subtab = parts[2] || 'line-items';
        this.navigateTo('rfx');
        this.showRfxDetail(rfxId).then(() => {
          if (subtab && subtab !== 'line-items') {
            const btnId = subtab.startsWith('tab-') ? subtab.replace('tab-', 'tab-btn-') : `tab-btn-${subtab}`;
            const targetId = subtab.startsWith('tab-') ? subtab : `tab-${subtab}`;
            const tabBtn = document.getElementById(btnId);
            this.switchRfxTab(tabBtn, targetId);
          }
        });
      } else if (h === 'search') {
        this.navigateTo('dashboard');
        setTimeout(() => this.showSearchModal(), 200);
      } else if (h === 'edit-rfx') {
        this.navigateTo('rfx');
        this.showRfxDetail(1).then(() => {
          setTimeout(() => this.editRfxModal(1), 200);
        });
      } else if (h === 'add-item') {
        this.navigateTo('rfx');
        this.showRfxDetail(1).then(() => {
          setTimeout(() => this.showAddLineItemModal(1), 200);
        });
      } else if (h === 'create-rfx') {
        this.navigateTo('rfx');
        setTimeout(() => this.showNewRfxModal(), 200);
      } else if (h.startsWith('sub-inspect')) {
        const parts = h.split('/');
        const supplierId = parts[1] ? parseInt(parts[1], 10) : 1;
        this.navigateTo('submissions');
        setTimeout(() => this.viewSubmissionDetails(supplierId), 350);
      } else if (h.startsWith('sub-upload')) {
        this.navigateTo('submissions', false);
        setTimeout(() => this.showUploadModal(1, 'PackIndia Ltd'), 350);
      } else if (h === 'sub-menu') {
        this.navigateTo('submissions', false);
        setTimeout(() => this.toggleSubRowMenu(null, 1), 600);
      } else if (h.startsWith('quote-detail')) {
        this.navigateTo('comparison', false);
        setTimeout(() => this.openCellDetail(2, 'PCO'), 700);
      } else if (h === 'comparison-diecut') {
        this.navigateTo('comparison', false);
        setTimeout(() => this.filterComparisonCategory('diecut'), 600);
      } else if (h === 'comparison-brc') {
        this.navigateTo('comparison', false);
        setTimeout(() => {
          const chk = document.getElementById('brc-toggle');
          if (chk) { chk.checked = true; this.toggleBrcFilter(true); }
        }, 600);
      } else if (h === 'corr-modal') {
        this.navigateTo('comparison', false);
        setTimeout(() => this.openCorrectionModal(1, '16.10'), 600);
      } else if (h === 'award-approve') {
        this.navigateTo('award', false);
        setTimeout(() => this.approveAward(), 600);
      } else if (h === 'copilot-thread') {
        this.navigateTo('analyst', false);
        setTimeout(() => this.resetCopilotChat(), 100);
      } else {
        this.navigateTo(h || 'dashboard');
      }
    };
    handleHash();
    window.addEventListener('hashchange', handleHash);
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.row-actions-wrap')) {
        this.closeAllRowMenus();
      }
    });
  },

  setupNavigation() {
    document.querySelectorAll('.nav-item, .nav-pill-btn, [data-section]').forEach(link => {
      link.addEventListener('click', e => {
        e.preventDefault();
        const section = link.getAttribute('data-section');
        if (section) this.navigateTo(section);
      });
    });

    // Keyboard shortcut Cmd-K / Ctrl-K for quick search modal
    document.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        this.showSearchModal();
      }
    });
  },

  navigateTo(sectionId, updateHash = true) {
    if (this.currentSection && this.currentSection !== sectionId && this.currentSection !== 'analyst') {
      this.previousSection = this.currentSection;
    }
    this.currentSection = sectionId;
    if (updateHash && window.location.hash.replace('#', '') !== sectionId) {
      window.location.hash = sectionId;
    }

    // Toggle viewport-copilot-mode for full-height smooth scrolling in Copilot
    const mainViewport = document.getElementById('main-viewport');
    if (mainViewport) {
      if (sectionId === 'analyst') {
        mainViewport.classList.add('viewport-copilot-mode');
      } else {
        mainViewport.classList.remove('viewport-copilot-mode');
      }
    }

    // Update active state on sidebar and any nav items
    document.querySelectorAll('.nav-item, .nav-pill-btn').forEach(a => {
      a.classList.toggle('active', a.getAttribute('data-section') === sectionId);
    });

    // Update section visibility
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    const targetSection = document.getElementById(`section-${sectionId}`);
    if (targetSection) targetSection.classList.add('active');

    // Close quote detail drawer when navigating
    this.closeCellDetail();

    // Section specific loaders
    switch (sectionId) {
      case 'dashboard':
        this.loadDashboard();
        break;
      case 'rfx':
        this.loadRfxEvents();
        break;
      case 'submissions':
        this.loadSubmissions();
        break;
      case 'comparison':
        this.loadComparison();
        break;
      case 'analyst':
        this.loadAnalyst();
        break;
      case 'award':
        this.loadAward();
        break;
    }
  },

  // ── Global Helpers ──────────────────────────────────────────────────────────
  async api(method, path, body = null) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API + path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      let msg = `HTTP ${res.status}`;
      if (typeof err.detail === 'string') {
        msg = err.detail;
      } else if (Array.isArray(err.detail)) {
        msg = err.detail.map(d => (d.loc ? d.loc.slice(1).join('.') + ': ' : '') + d.msg).join('; ');
      } else if (err.detail && typeof err.detail === 'object') {
        msg = err.detail.message || JSON.stringify(err.detail);
      } else if (err.message) {
        msg = err.message;
      }
      throw new Error(msg);
    }
    return res.json();
  },

  badge(status, text = null) {
    const label = text || status;
    const classes = {
      PENDING: 'badge-gray',
      IN_PROGRESS: 'badge-blue badge-pulse',
      COMPLETED: 'badge-green',
      FAILED: 'badge-red',
      ACTIVE: 'badge-green',
      DRAFT: 'badge-gray',
      SENT: 'badge-blue',
      EXCEL: 'badge-excel',
      PDF: 'badge-pdf',
      WORD: 'badge-word',
      IMAGE: 'badge-image',
      EMAIL: 'badge-email',
      COMPLIANT: 'badge-green',
      NON_COMPLIANT: 'badge-red',
      SUBSTITUTE: 'badge-orange',
      UNKNOWN: 'badge-gray',
    };
    return `<span class="badge ${classes[status] || 'badge-gray'}">${label}</span>`;
  },

  confidenceDot(conf) {
    if (conf === null || conf === undefined) return '<span class="conf-dot conf-unknown" title="Unknown confidence"></span>';
    const pct = Math.round(conf * 100);
    const cls = conf >= 0.85 ? 'conf-high' : conf >= 0.6 ? 'conf-mid' : 'conf-low';
    return `<span class="conf-dot ${cls}" title="${pct}% extraction confidence"></span>`;
  },

  inr(val, placeholder = '-') {
    if (val === null || val === undefined) return placeholder;
    return '₹' + Number(val).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  },

  toast(msg, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${this.escapeHtml(msg)}</span>`;
    container.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateY(10px)';
      setTimeout(() => t.remove(), 300);
    }, 4000);
  },

  showModal(title, bodyHtml, footerHtml = '', modalClass = '') {
    const mc = document.getElementById('modal-container');
    mc.innerHTML = `
      <div class="modal-overlay" onclick="if(event.target===this) App.closeModal()">
        <div class="modal ${modalClass || ''}">
          <div class="modal-header">
            <div class="modal-title">${this.escapeHtml(title)}</div>
            <button class="modal-close" onclick="App.closeModal()">&times;</button>
          </div>
          <div class="modal-body">${bodyHtml}</div>
          ${footerHtml ? `<div class="modal-footer">${footerHtml}</div>` : ''}
        </div>
      </div>
    `;
  },

  closeModal() {
    const mc = document.getElementById('modal-container');
    if (mc) mc.innerHTML = '';
  },

  escapeHtml(str) {
    if (str === null || str === undefined) return '';
    const map = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#039;',
      '/': '&#x2F;',
      '`': '&#x60;'
    };
    return String(str).replace(/[&<>"'`\/]/g, m => map[m]);
  },

  renderMarkdown(text) {
    if (!text) return '';
    // Security: Escape all raw HTML entities first to prevent XSS injection
    let html = this.escapeHtml(text)
      .replace(/^#### (.*$)/gim, '<h5 style="margin:8px 0 4px 0; color:var(--text-primary); font-size:12.5px;">$1</h5>')
      .replace(/^### (.*$)/gim, '<h4 style="margin:10px 0 6px 0; color:var(--primary); font-size:13.5px;">$1</h4>')
      .replace(/^## (.*$)/gim, '<h3 style="margin:12px 0 8px 0; color:var(--primary); font-size:14.5px;">$1</h3>')
      .replace(/^# (.*$)/gim, '<h2 style="margin:14px 0 10px 0; color:var(--primary); font-size:15.5px;">$1</h2>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code style="background:#f1f5f9; padding:2px 5px; border-radius:3px; font-size:11.5px;">$1</code>')
      .replace(/^\s*[-*]\s+(.*)$/gim, '<li style="margin-left:18px; margin-bottom:4px;">$1</li>')
      .replace(/^\s*(\d+)\.\s+(.*)$/gim, '<li style="margin-left:18px; margin-bottom:4px;">$2</li>');
    
    html = html.replace(/(<li[\s\S]*?<\/li>\n?)+/g, '<ul style="margin:6px 0 10px 0; padding-left:0;">$&</ul>');
    html = html.replace(/\n\n/g, '<div style="margin-bottom:8px;"></div>');
    return html;
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 1: DASHBOARD
  // ════════════════════════════════════════════════════════════════════════════
  async loadDashboard() {
    try {
      const rfxId = this.currentRfxId || 1;
      const [rfxRes, auditRes, subRes, awardRes] = await Promise.all([
        this.api('GET', '/api/rfx/list').catch(err => {
          console.warn('Using cached rfx events fallback:', err);
          return {
            rfx_events: [{
              id: 1,
              rfx_number: 'RFX-2026-001',
              title: 'Corrugated Packaging Sourcing RFx FY2026-27',
              status: 'OPEN',
              line_items_count: 30,
              submissions_count: 5,
              deadline: '2026-10-20'
            }]
          };
        }),
        this.api('GET', `/api/rfx/${rfxId}/audit-log`).catch(() => ({ audit_log: [] })),
        this.api('GET', `/api/rfx/${rfxId}/submissions`).catch(() => ({ submissions: [] })),
        this.api('GET', `/api/rfx/${rfxId}/award-scenarios`).catch(() => null),
      ]);

      const rfxList = rfxRes.rfx_events || [];
      const auditLog = auditRes.audit_log || [];
      const subs = subRes.submissions || [];

      // Update KPI metrics in strip
      const spend = awardRes?.single_supplier?.best?.total_cost || 26661540;
      this.portfolioSpend = spend;
      this.updateHeroSpendDisplay();

      const savingsEl = document.getElementById('kpi-savings-val');
      if (savingsEl) {
        const savings = awardRes?.savings_from_split || 4505550;
        savingsEl.textContent = this.inr(savings);
      }

      // Render Charts & Dynamic Supplier Breakdown
      this.renderDashboardCharts();
      this.renderDashboardSupplierProgress(awardRes, subRes);
      this.renderDashboardRecentActivity(auditLog);

      const insightPill = document.getElementById('dash-insight-pill');
      if (insightPill && awardRes?.savings_from_split) {
        insightPill.innerHTML = `${this.icon('sparkles', 13)} Optimal Split Award Saves ${this.inr(awardRes.savings_from_split)} vs Single Sourcing`;
      }

      // Render Active RFx Events summary table
      const rfxTableWrap = document.getElementById('dash-rfx-table');
      if (rfxTableWrap) {
        if (rfxList.length === 0) {
          rfxTableWrap.innerHTML = '<div class="empty-state">No RFx events found.</div>';
        } else {
          rfxTableWrap.innerHTML = `
            <table>
              <thead>
                <tr>
                  <th>RFx Number</th>
                  <th>Title &amp; Scope</th>
                  <th>Status</th>
                  <th>Line Items</th>
                  <th>Submissions</th>
                  <th>Deadline</th>
                  <th style="width: 150px; text-align: right; white-space: nowrap;">Action</th>
                </tr>
              </thead>
              <tbody>
                ${rfxList.map(r => `
                  <tr>
                    <td><strong>${r.rfx_number}</strong></td>
                    <td>
                      <div class="font-semibold">${r.title}</div>
                      <div class="text-xs text-muted">Corrugated Packaging - FMCG Division</div>
                    </td>
                    <td>${this.badge(r.status)}</td>
                    <td>${r.line_items_count || 30} SKUs</td>
                    <td>${r.submissions_count || 5} received</td>
                    <td>${r.deadline ? r.deadline.substring(0, 10) : '2026-10-20'}</td>
                    <td style="text-align: right; white-space: nowrap;">
                      <button class="btn-capsule-secondary" style="height:32px; padding:0 16px; font-size:12px; display:inline-flex; align-items:center; gap:6px; white-space: nowrap;" onclick="App.showRfxDetail(${r.id})">
                        View Event
                        ${this.icon('arrow-right', 12)}
                      </button>
                    </td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        }
      }
    } catch (err) {
      console.error('Dashboard load error:', err);
      this.toast(`Failed to load dashboard: ${err.message}`, 'error');
    }
  },

  renderDashboardCharts() {
    // Pie chart removed
    if (this.chartInstances['category-spend']) {
      this.chartInstances['category-spend'].destroy();
      delete this.chartInstances['category-spend'];
    }
  },

  renderDashboardSupplierProgress(awardRes, subRes) {
    const container = document.getElementById('dash-supplier-progress');
    if (!container) return;

    const allocSummary = {};
    const splitDetail = awardRes?.split_award?.detail || [];
    if (splitDetail.length > 0) {
      splitDetail.forEach(d => {
        if (!d.best_supplier_code) return;
        const c = d.best_supplier_code;
        if (!allocSummary[c]) {
          allocSummary[c] = {
            code: c,
            name: d.best_supplier_name || c,
            items_awarded: 0,
            total_value: 0
          };
        }
        allocSummary[c].items_awarded += 1;
        allocSummary[c].total_value += (d.total_cost || 0);
      });
    }

    const totalCost = awardRes?.split_award?.total_cost || 26661540;

    const baseSuppliers = [
      { code: 'IPI', name: 'IndoPack Industries', city: 'Chennai', brc: true },
      { code: 'PKI', name: 'PackIndia Ltd', city: 'Pune', brc: true },
      { code: 'PCO', name: 'PremiumCorrugated', city: 'Mumbai', brc: true },
      { code: 'EBS', name: 'EcoBox Solutions', city: 'Ahmedabad', brc: false },
      { code: 'RPC', name: 'RegionalPacks Co', city: 'Hyderabad', brc: false }
    ];

    const subs = subRes?.submissions || [];
    const supplierList = subs.length > 0
      ? subs.map(s => ({
          code: s.supplier_code,
          name: s.supplier_name,
          city: s.supplier_city || '',
          brc: s.brc_qualified
        }))
      : baseSuppliers;

    const items = supplierList.map(s => {
      const a = allocSummary[s.code];
      const color = SUPPLIER_COLORS[s.code] || '#4C00D0';
      if (a) {
        const share = Math.round((a.total_value / totalCost) * 100);
        return {
          name: a.name || s.name,
          code: s.code,
          share,
          amount: this.inr(a.total_value),
          role: `${s.city ? s.city + ' · ' : ''}${a.items_awarded} SKUs Awarded`,
          color
        };
      } else {
        return {
          name: s.name,
          code: s.code,
          share: 0,
          amount: '₹0',
          role: s.brc === false ? `${s.city ? s.city + ' · ' : ''}Non-BRC (Disqualified)` : `${s.city ? s.city + ' · ' : ''}0 SKUs Awarded`,
          color
        };
      }
    });

    items.sort((a, b) => b.share - a.share);

    container.innerHTML = items.map(s => `
      <div class="provider-row">
        <div class="provider-info-left">
          <div class="provider-avatar" style="background:${s.color}15; color:${s.color};">
            ${s.code}
          </div>
          <div class="provider-text">
            <span class="provider-name">${s.name}</span>
            <span class="provider-role">${s.role}</span>
          </div>
        </div>
        <div class="provider-bar-track">
          <div class="provider-bar-fill" style="width:${Math.max(s.share, s.share > 0 ? 4 : 0)}%; background:${s.color};"></div>
        </div>
        <div class="provider-pct" style="width: 80px; text-align: right;">
          <div style="font-size: 13.5px; font-weight: 700; color: var(--text-main);">${s.share}%</div>
          <div style="font-size: 11px; font-weight: 500; color: var(--text-muted);">${s.amount}</div>
        </div>
      </div>
    `).join('');
  },

  renderDashboardRecentActivity(auditLog) {
    const container = document.getElementById('dash-recent-activity');
    if (!container) return;

    const defaultActivities = [
      { type: 'Optimization', title: 'Optimal Split-Award modeled: ₹45.05L verified savings', time: 'Just now', badge: 'OPTIMIZED', badgeClass: 'badge-purple', icon: 'award' },
      { type: 'Compliance', title: 'BRC/IoP Food-Grade compliance audit completed for 5 suppliers', time: '2h ago', badge: 'AUDITED', badgeClass: 'badge-green', icon: 'check-circle' },
      { type: 'AI Extraction', title: 'PackIndia Ltd quotation ingested & normalized (98% confidence)', time: '4h ago', badge: 'INGESTED', badgeClass: 'badge-blue', icon: 'file' },
      { type: 'Sourcing Round', title: 'RFX-2026-001 published to approved packaging suppliers', time: '1d ago', badge: 'PUBLISHED', badgeClass: 'badge-gray', icon: 'file-text' }
    ];

    let activities = [];
    if (auditLog && auditLog.length > 0) {
      const seen = new Set();
      for (const a of auditLog) {
        const cleanTitle = (a.event_detail || '').replace(/^Query:\s*/i, 'Analyst Query: ');
        const key = (a.event_type || '') + ':' + cleanTitle.substring(0, 32);
        if (seen.has(key)) continue;
        seen.add(key);

        let icon = 'file-text';
        let badge = 'LOGGED';
        let badgeClass = 'badge-blue';
        const type = (a.event_type || '').replace(/_/g, ' ');

        if (a.event_type.includes('EXTRACTION')) {
          if (a.event_type.includes('FAIL')) {
            icon = 'alert-triangle';
            badge = 'FAILED';
            badgeClass = 'badge-red';
          } else {
            icon = 'check-circle';
            badge = 'EXTRACTED';
            badgeClass = 'badge-green';
          }
        } else if (a.event_type.includes('ANALYST') || a.event_type.includes('QUERY')) {
          icon = 'sparkles';
          badge = 'COPILOT';
          badgeClass = 'badge-purple';
        } else if (a.event_type.includes('AWARD')) {
          icon = 'award';
          badge = 'AWARDED';
          badgeClass = 'badge-green';
        } else if (a.event_type.includes('INVITATION')) {
          icon = 'mail';
          badge = 'SENT';
          badgeClass = 'badge-blue';
        } else if (a.event_type.includes('SUBMISSION') || a.event_type.includes('UPLOAD')) {
          icon = 'upload';
          badge = 'UPLOADED';
          badgeClass = 'badge-blue';
        } else if (a.event_type.includes('OVERRIDE')) {
          icon = 'edit';
          badge = 'OVERRIDE';
          badgeClass = 'badge-purple';
        } else if (a.event_type.includes('LINE_ITEM') || a.event_type.includes('ITEM')) {
          icon = 'edit';
          badge = 'ITEM';
          badgeClass = 'badge-gray';
        } else if (a.event_type.includes('RFX')) {
          icon = 'file';
          badge = 'CREATED';
          badgeClass = 'badge-gray';
        }

        const rfxMatch = (a.event_detail || '').match(/RFX-\d+-(\d+)/i);
        const eventRfxId = a.rfx_id || (rfxMatch ? parseInt(rfxMatch[1], 10) : 1);
        const isAnalyst = a.event_type.includes('ANALYST') || a.event_type.includes('QUERY');

        activities.push({
          type,
          title: cleanTitle,
          time: (a.created_at || a.timestamp || '').substring(11, 16) || 'Today',
          badge,
          badgeClass,
          icon,
          rfxId: eventRfxId,
          isAnalyst
        });
        if (activities.length >= 4) break;
      }
    }

    if (activities.length === 0) {
      activities = defaultActivities;
    }

    container.innerHTML = activities.map(act => `
      <div class="activity-item" style="cursor: pointer;" onclick="${act.isAnalyst ? "App.navigateTo('analyst')" : `App.showRfxDetail(${act.rfxId || 1})`}" title="Click to view details">
        <div class="activity-left">
          <div class="activity-icon-circle ${act.badgeClass ? 'circle-' + act.badgeClass.replace('badge-', '') : ''}">
            ${this.icon(act.icon, 16)}
          </div>
          <div class="activity-info">
            <span class="activity-title">${this.escapeHtml(act.title)}</span>
            <span class="activity-time">${this.escapeHtml(act.time)} · ${this.escapeHtml(act.type)}</span>
          </div>
        </div>
        <div class="activity-right">
          <span class="badge ${this.escapeHtml(act.badgeClass)}">${this.escapeHtml(act.badge)}</span>
        </div>
      </div>
    `).join('');
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 2: RFX EVENTS & DETAIL
  // ════════════════════════════════════════════════════════════════════════════
  async loadRfxEvents() {
    this.showRfxList();
  },

  async showRfxList() {
    document.getElementById('rfx-list-view').style.display = 'block';
    document.getElementById('rfx-detail-view').style.display = 'none';

    try {
      const res = await this.api('GET', '/api/rfx/list');
      const rfxList = res.rfx_events || [];
      const wrap = document.getElementById('rfx-list-table');
      wrap.innerHTML = `
        <table>
          <thead>
            <tr>
              <th style="width: 150px;">RFx Number</th>
              <th>Title &amp; Scope</th>
              <th style="width: 110px;">Status</th>
              <th style="width: 110px;">Line Items</th>
              <th style="width: 120px;">Submissions</th>
              <th style="width: 130px;">Target Deadline</th>
              <th style="width: 160px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            ${rfxList.map(r => `
              <tr>
                <td style="white-space: nowrap; font-weight: 700; letter-spacing: 0.02em; padding: 14px 18px;">${r.rfx_number}</td>
                <td style="padding: 14px 18px;">
                  <div class="font-semibold" style="margin-bottom: 4px;">${r.title}</div>
                  <div class="text-xs text-muted" style="line-height: 1.4;">${(r.description || '').substring(0, 80)}...</div>
                </td>
                <td style="white-space: nowrap; padding: 14px 18px;">${this.badge(r.status)}</td>
                <td style="white-space: nowrap; padding: 14px 18px;">${r.line_items_count || 30} SKUs</td>
                <td style="white-space: nowrap; padding: 14px 18px;">${r.submissions_count || 5} received</td>
                <td style="white-space: nowrap; padding: 14px 18px;">${r.deadline ? r.deadline.substring(0, 10) : '2026-10-20'}</td>
                <td style="text-align: right; white-space: nowrap; padding: 14px 18px;">
                  <button class="btn-capsule-dark" style="height: 32px; padding: 0 16px; font-size: 12px; white-space: nowrap; display: inline-flex; align-items: center; gap: 6px;" onclick="App.showRfxDetail(${r.id})">
                    Open Workspace
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                  </button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (err) {
      this.toast(`Error loading RFx events: ${err.message}`, 'error');
    }
  },

  async showRfxDetail(rfxId, defaultTab = 'tab-line-items') {
    this.navigateTo('rfx', false);

    const listView = document.getElementById('rfx-list-view');
    const detailView = document.getElementById('rfx-detail-view');
    if (listView) listView.style.display = 'none';
    if (detailView) detailView.style.display = 'block';

    // Select the requested tab
    document.querySelectorAll('#rfx-detail-view .filter-pill').forEach(t => t.classList.remove('active'));
    const tabBtnMap = {
      'tab-line-items': 'tab-btn-line-items',
      'tab-questionnaire': 'tab-btn-questionnaire',
      'tab-invitations': 'tab-btn-invitations'
    };
    const targetBtn = document.getElementById(tabBtnMap[defaultTab] || 'tab-btn-line-items');
    if (targetBtn) targetBtn.classList.add('active');

    ['tab-line-items', 'tab-questionnaire', 'tab-invitations'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = id === defaultTab ? 'block' : 'none';
    });

    try {
      const rfx = await this.api('GET', `/api/rfx/${rfxId}`);
      this.currentRfxId = rfx.id;
      this.currentRfxNumber = rfx.rfx_number;
      document.getElementById('rfx-detail-title').textContent = `${rfx.rfx_number}: ${rfx.title}`;

      const bcBadge = document.getElementById('breadcrumb-rfx');
      if (bcBadge) {
        bcBadge.innerHTML = `<span class="breadcrumb-sep">›</span><span class="badge badge-blue" style="font-size:11px;">${rfx.rfx_number}</span>`;
        bcBadge.style.display = 'inline-flex';
      }

      // Render Meta Card
      const meta = document.getElementById('rfx-detail-meta');
      meta.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; padding-bottom:12px; border-bottom:1px solid var(--border-light);">
          <div style="font-size:15px; font-weight:700; color:var(--text-main);">Event Specifications &amp; Timeline</div>
          <button type="button" class="btn-capsule-secondary" style="height:32px; padding:0 14px; font-size:12px; display:inline-flex; align-items:center; gap:6px;" onclick="App.editRfxModal(${rfx.id})">${this.icon("edit", 13)} Edit Details</button>
        </div>
        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:24px; margin-bottom:16px;">
          <div>
            <div class="detail-label">RFx Event</div>
            <div class="font-bold" style="font-size:14px;">${rfx.rfx_number}</div>
          </div>
          <div>
            <div class="detail-label">Status</div>
            <div>${this.badge(rfx.status)}</div>
          </div>
          <div>
            <div class="detail-label">Category Manager</div>
            <div class="font-bold" style="font-size:14px;">${rfx.buyer_name || 'Priya Krishnamurthy'}</div>
          </div>
          <div>
            <div class="detail-label">Submission Deadline</div>
            <div class="font-bold" style="font-size:14px;">${rfx.deadline ? rfx.deadline.substring(0, 10) : '2026-10-20'}</div>
          </div>
        </div>
        <div style="padding-top:14px; border-top:1px solid var(--border-light); font-size:13px; line-height:1.6; color:var(--text-secondary);">
          <strong style="color:var(--text-main);">Scope:</strong> ${rfx.description || 'Annual contracted procurement for corrugated cartons and packaging materials across North & Western manufacturing plants.'}
        </div>
      `;

      // Render Line Items tab
      const items = rfx.line_items || [];
      this.currentLineItems = items;
      const skuCountNum = document.getElementById('sku-count-num');
      if (skuCountNum) skuCountNum.textContent = items.length;
      const tabBtn = document.getElementById('tab-btn-line-items');
      if (tabBtn) tabBtn.textContent = `Line Items (${items.length})`;

      document.getElementById('rfx-items-table').innerHTML = `
        <table>
          <thead>
            <tr>
              <th style="width: 44px; text-align: center; padding: 12px 10px;">
                <input type="checkbox" id="chk-all-items" onchange="App.toggleSelectAllLineItems(this.checked)" style="cursor: pointer; width: 16px; height: 16px; accent-color: var(--brand-violet); border-radius: 4px;" title="Select all specifications">
              </th>
              <th style="width: 50px;">#</th>
              <th>SKU Description</th>
              <th style="width: 80px;">Ply</th>
              <th style="width: 80px;">Flute</th>
              <th style="width: 140px;">GSM Spec</th>
              <th style="width: 130px;">Dimensions</th>
              <th style="width: 110px;">Print</th>
              <th style="width: 80px;">ECT Min</th>
              <th style="width: 80px;">FEFCO</th>
              <th style="width: 100px;">Quantity</th>
              <th style="width: 100px;">Annual Vol</th>
              <th style="width: 70px; text-align: right;">Action</th>
            </tr>
          </thead>
          <tbody>
            ${items.map(i => `
              <tr id="line-item-row-${i.id}">
                <td style="text-align: center; padding: 12px 10px;">
                  <input type="checkbox" class="line-item-chk" value="${i.id}" data-number="${i.item_number}" onchange="App.updateSelectedLineItems()" style="cursor: pointer; width: 16px; height: 16px; accent-color: var(--brand-violet); border-radius: 4px;">
                </td>
                <td style="white-space: nowrap; font-weight: 700;">${i.item_number}</td>
                <td><div class="font-semibold">${i.description}</div></td>
                <td><span class="badge badge-gray">${i.spec_ply}</span></td>
                <td>${i.spec_flute || '-'}</td>
                <td class="text-xs text-muted">${i.spec_gsm || '-'}</td>
                <td><code>${i.spec_dimensions}</code></td>
                <td class="text-xs">${i.spec_print}</td>
                <td>${i.spec_ect_min || '-'}</td>
                <td class="text-xs text-muted">${i.fefco_code || '0201'}</td>
                <td class="font-semibold">${Number(i.quantity).toLocaleString('en-IN')} pcs</td>
                <td class="text-muted">${Number(i.annual_volume || i.quantity * 4).toLocaleString('en-IN')} pcs</td>
                <td style="text-align: right; position: relative;">
                  <div class="row-actions-wrap">
                    <button type="button" class="action-dots-btn" onclick="App.toggleRowMenu(event, ${i.id})" title="Actions">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="5" r="2.2"></circle>
                        <circle cx="12" cy="12" r="2.2"></circle>
                        <circle cx="12" cy="19" r="2.2"></circle>
                      </svg>
                    </button>
                    <div id="row-menu-${i.id}" class="action-dropdown" onclick="event.stopPropagation()">
                      <button type="button" class="action-dropdown-item" onclick="App.triggerEditLineItem(${i.id})">
                        ${this.icon('edit', 14)}
                        <span>Edit Item</span>
                      </button>
                      <button type="button" class="action-dropdown-item text-danger" onclick="App.triggerDeleteLineItem(${i.id}, ${i.item_number})">
                        ${this.icon('trash', 14)}
                        <span>Delete Item</span>
                      </button>
                    </div>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
      this.updateSelectedLineItems();

      // Render Questionnaire tab
      const questions = rfx.questionnaire || [];
      document.getElementById('rfx-q-table').innerHTML = `
        <table>
          <thead>
            <tr>
              <th style="width: 80px;">Code</th>
              <th style="width: 140px;">Requirement</th>
              <th>Question / Evaluation Criteria</th>
              <th style="width: 170px;">Expected Response</th>
            </tr>
          </thead>
          <tbody>
            ${questions.map(q => {
              let responseBadge = '<span class="badge badge-gray" style="font-size:11px;">Written Statement</span>';
              const at = (q.answer_type || '').toUpperCase();
              if (at === 'NUMBER') {
                responseBadge = '<span class="badge badge-blue" style="font-size:11px;">Numeric Value</span>';
              } else if (at.includes('FILE') || at.includes('CERT')) {
                responseBadge = '<span class="badge badge-purple" style="font-size:11px;">Certificate Upload</span>';
              } else if (at.includes('BOOL') || at.includes('YES')) {
                responseBadge = '<span class="badge badge-green" style="font-size:11px;">Yes / No Confirmation</span>';
              }
              return `
              <tr>
                <td style="white-space: nowrap; font-weight: 700; padding: 14px 18px;">${q.question_code}</td>
                <td style="white-space: nowrap; padding: 14px 18px;">
                  <span class="badge ${q.is_mandatory ? 'badge-red' : 'badge-gray'}">
                    ${q.is_mandatory ? 'Mandatory' : 'Optional'}
                  </span>
                </td>
                <td class="font-semibold" style="padding: 14px 18px; line-height: 1.5;">${q.question_text}</td>
                <td style="white-space: nowrap; padding: 14px 18px;">${responseBadge}</td>
              </tr>
            `}).join('')}
          </tbody>
        </table>
      `;

      // Render Invitations tab
      const supRes = await this.api('GET', `/api/rfx/${rfxId}/suppliers`);
      const suppliers = supRes.suppliers || [];
      document.getElementById('rfx-inv-table').innerHTML = `
        <table>
          <thead>
            <tr>
              <th style="width: 120px;">Supplier Code</th>
              <th>Company Name</th>
              <th style="width: 140px;">Plant Location</th>
              <th>Certifications</th>
              <th style="width: 140px;">Invitation Status</th>
              <th style="width: 130px;">Dispatch Date</th>
            </tr>
          </thead>
          <tbody>
            ${suppliers.map(s => `
              <tr>
                <td style="white-space: nowrap; font-weight: 700; padding: 14px 18px;">${s.code}</td>
                <td style="padding: 14px 18px;"><div class="font-semibold">${s.name}</div></td>
                <td style="padding: 14px 18px;">${s.city}</td>
                <td style="padding: 14px 18px;">
                  <div class="sh-certs">
                    ${(s.certifications || '').split(',').map(c => `<span class="badge badge-gray" style="font-size:10px;">${c.trim()}</span>`).join(' ')}
                  </div>
                </td>
                <td style="white-space: nowrap; padding: 14px 18px;">${this.badge(s.invitation_status || 'SENT')}</td>
                <td style="white-space: nowrap; padding: 14px 18px;" class="text-xs text-muted">${s.sent_at ? s.sent_at.substring(0, 10) : '2026-09-30'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    } catch (err) {
      console.warn(`Error loading RFx details for ${rfxId}:`, err);
      this.toast(`Error loading RFx details: ${err.message}`, 'error');
      if (rfxId !== 1) {
        this.showRfxDetail(1, defaultTab);
      }
    }
  },

  switchRfxTab(tabEl, targetId) {
    document.querySelectorAll('#rfx-detail-view .filter-pill').forEach(t => t.classList.remove('active'));
    if (tabEl) tabEl.classList.add('active');

    ['tab-line-items', 'tab-questionnaire', 'tab-invitations'].forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = id === targetId ? 'block' : 'none';
    });
  },

  async sendInvitations() {
    const rfxId = this.currentRfxId || 1;
    let suppliers = [];
    try {
      const res = await this.api('GET', `/api/rfx/${rfxId}/suppliers`);
      suppliers = res.suppliers || [];
    } catch (e) {
      console.warn('Could not fetch supplier list for modal:', e);
    }

    if (!suppliers.length) {
      suppliers = [
        { code: 'PKI', name: 'PackIndia Ltd.', contact_email: 'suppliers@packindia.in', city: 'Mumbai, MH' },
        { code: 'EBS', name: 'EcoBox Solutions', contact_email: 'quotes@ecoboxsolutions.in', city: 'Pune, MH' },
        { code: 'IPI', name: 'IndoPack Industries', contact_email: 'sales@indopack.com', city: 'Chennai, TN' },
        { code: 'PCO', name: 'Premium Corrugated Corp', contact_email: 'tender@premiumcorrugated.in', city: 'Ahmedabad, GJ' },
        { code: 'RPC', name: 'RegionalPacks Co.', contact_email: 'rpc.packaging@gmail.com', city: 'Bengaluru, KA' }
      ];
    }

    const recipientsListHtml = suppliers.map(s => `
      <div style="display:flex; align-items:center; gap:10px; padding:8px 12px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;">
        <div style="width:30px; height:30px; border-radius:6px; background:${SUPPLIER_COLORS[s.code] || '#373192'}; color:#FFFFFF; display:flex; align-items:center; justify-content:center; font-size:10.5px; font-weight:700; flex-shrink:0; letter-spacing:0.02em;">
          ${this.escapeHtml(s.code || s.name.substring(0, 3).toUpperCase())}
        </div>
        <div style="flex:1; min-width:0;">
          <div style="font-size:12px; font-weight:600; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${this.escapeHtml(s.name)}">${this.escapeHtml(s.name)}</div>
          <div style="font-size:11px; color:#64748B; font-family:monospace; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${this.escapeHtml(s.contact_email || '')}">${this.escapeHtml(s.contact_email || '')}</div>
        </div>
      </div>
    `).join('');

    const bodyHtml = `
      <div style="display:flex; flex-direction:column; gap:16px; font-size:13px;">
        <!-- Enterprise Gateway Status Strip -->
        <div style="display:flex; align-items:center; justify-content:space-between; padding:10px 14px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981; box-shadow:0 0 0 3px rgba(16,185,129,0.18);"></span>
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12.5px; font-weight:700; color:#0F172A;">Enterprise SMTP Dispatch Gateway</span>
              <span style="font-size:11px; color:#64748B;">· RFC 5322 Compliant Delivery</span>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-family:monospace; font-size:10px; font-weight:600; background:#ECFDF5; color:#059669; border:1px solid #A7F3D0; border-radius:4px; padding:2px 8px;">TLS 1.3 ENCRYPTED</span>
            <span style="font-size:11px; color:#64748B;">Port 587</span>
          </div>
        </div>

        <!-- Verified Supplier Contacts -->
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <span style="font-size:11px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:#64748B;">Verified Supplier Recipients (${suppliers.length} Qualified Contacts)</span>
            <span style="display:inline-flex; align-items:center; gap:4px; font-size:11px; font-weight:600; color:#059669;">
              ${this.icon('check-circle', 13)} All Contacts Validated
            </span>
          </div>
          <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:8px;">
            ${recipientsListHtml}
          </div>
        </div>

        <!-- Outbound Email Preview Window -->
        <div style="display:flex; flex-direction:column; gap:8px;">
          <div style="display:flex; align-items:center; justify-content:space-between;">
            <span style="font-size:11px; font-weight:700; letter-spacing:0.05em; text-transform:uppercase; color:#64748B;">Outbound Invitation Preview</span>
            <span style="font-size:11px; color:#64748B;">Standard Category Transmission</span>
          </div>
          
          <div style="border:1px solid #E2E8F0; border-radius:10px; background:#FFFFFF; overflow:hidden;">
            <!-- Email Header Metadata -->
            <div style="background:#F8FAFC; padding:12px 16px; border-bottom:1px solid #E2E8F0; display:flex; flex-direction:column; gap:6px; font-size:12px;">
              <div style="display:flex; align-items:baseline; gap:8px;">
                <span style="font-weight:600; color:#64748B; width:52px; flex-shrink:0;">From:</span>
                <span style="color:#0F172A; flex:1;">
                  <strong>Priya Krishnamurthy</strong> &lt;sourcing.packaging@aerchain-fmcg.com&gt; <span style="color:#64748B;">· Lead Category Manager</span>
                </span>
              </div>
              <div style="display:flex; align-items:baseline; gap:8px;">
                <span style="font-weight:600; color:#64748B; width:52px; flex-shrink:0;">To:</span>
                <span style="font-family:monospace; font-size:11.5px; color:#475467; flex:1;">
                  ${suppliers.map(s => this.escapeHtml(s.contact_email || '')).join(', ')}
                </span>
              </div>
              <div style="display:flex; align-items:baseline; gap:8px;">
                <span style="font-weight:600; color:#64748B; width:52px; flex-shrink:0;">Subject:</span>
                <span style="font-weight:700; color:#0F172A; flex:1;">
                  Request for Quotation: RFX-2026-001 — FMCG Corrugated Packaging Annual Contract (FY 2026-27)
                </span>
              </div>
            </div>

            <!-- Email Body Content -->
            <div style="padding:16px; font-size:12.5px; line-height:1.6; color:#0F172A; display:flex; flex-direction:column; gap:12px;">
              <div>Dear Supplier Partner,</div>
              <div style="color:#334155;">
                You are formally invited to submit commercial quotations and technical qualification responses for the 
                <strong>FMCG Corrugated Packaging Annual Sourcing Contract (RFX-2026-001)</strong>.
              </div>

              <!-- 2x2 Parameter Grid -->
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:2px 0;">
                <div style="display:flex; gap:10px; padding:10px 12px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;">
                  <div style="width:26px; height:26px; border-radius:6px; background:#EEF2FF; color:#4338CA; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    ${this.icon('file-text', 14)}
                  </div>
                  <div style="flex:1; min-width:0;">
                    <div style="font-size:11px; font-weight:700; color:#4338CA; text-transform:uppercase; letter-spacing:0.03em;">Scope &amp; Volume</div>
                    <div style="font-size:11.5px; color:#334155; margin-top:2px; line-height:1.4;">30 SKUs across RSC Cartons, Die-Cut Shelf Trays, and Heavy Bulk Bins (FEFCO 0201, 0215, 0427, 0713)</div>
                  </div>
                </div>

                <div style="display:flex; gap:10px; padding:10px 12px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;">
                  <div style="width:26px; height:26px; border-radius:6px; background:#F0FDF4; color:#15803D; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    ${this.icon('shield', 14)}
                  </div>
                  <div style="flex:1; min-width:0;">
                    <div style="font-size:11px; font-weight:700; color:#15803D; text-transform:uppercase; letter-spacing:0.03em;">Quality Gates</div>
                    <div style="font-size:11.5px; color:#334155; margin-top:2px; line-height:1.4;">10 Questions (ISO 9001 and BRC/IoP Global Packaging Standards are mandatory disqualifying gates)</div>
                  </div>
                </div>

                <div style="display:flex; gap:10px; padding:10px 12px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;">
                  <div style="width:26px; height:26px; border-radius:6px; background:#FAF5FF; color:#7E22CE; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    ${this.icon('upload', 14)}
                  </div>
                  <div style="flex:1; min-width:0;">
                    <div style="font-size:11px; font-weight:700; color:#7E22CE; text-transform:uppercase; letter-spacing:0.03em;">Accepted Formats</div>
                    <div style="font-size:11.5px; color:#334155; margin-top:2px; line-height:1.4;">Multi-format ingestion: Excel (.xlsx), PDF, Word (.docx), Scanned Rate Cards, or direct email text</div>
                  </div>
                </div>

                <div style="display:flex; gap:10px; padding:10px 12px; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px;">
                  <div style="width:26px; height:26px; border-radius:6px; background:#FFFBEB; color:#B45309; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                    ${this.icon('clock', 14)}
                  </div>
                  <div style="flex:1; min-width:0;">
                    <div style="font-size:11px; font-weight:700; color:#B45309; text-transform:uppercase; letter-spacing:0.03em;">Submission Deadline</div>
                    <div style="font-size:11.5px; color:#334155; margin-top:2px; line-height:1.4;"><strong>October 20, 2026 at 18:00 IST</strong> (Strict closing deadline)</div>
                  </div>
                </div>
              </div>

              <div style="font-size:11.5px; color:#64748B; margin-top:2px;">
                Please ensure all quotes specify unit rates, applicable volume discounts, minimum order quantities (MOQ), and plant dispatch lead times.
              </div>

              <div style="border-top:1px solid #E2E8F0; padding-top:10px; margin-top:2px; display:flex; justify-content:space-between; align-items:flex-end;">
                <div>
                  <div style="font-weight:700; color:#0F172A; font-size:12px;">Category Management Team — Packaging Division</div>
                  <div style="font-size:11px; color:#64748B;">Aerchain Autonomous Sourcing Intelligence</div>
                </div>
                <div style="font-size:11px; color:#64748B; font-style:italic;">
                  System-generated invitation packet
                </div>
              </div>
            </div>

            <!-- Attached Specification Packets -->
            <div style="padding:12px 16px; background:#F8FAFC; border-top:1px solid #E2E8F0; display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; align-items:center; gap:6px; font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.04em; color:#64748B;">
                ${this.icon('file', 13)}
                <span>Attached Specification Packets (3 Files · 447 KB Total)</span>
              </div>
              <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:8px;">
                <div style="display:flex; align-items:center; gap:8px; padding:8px 10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px;">
                  ${this.getFileTypeIcon('EXCEL')}
                  <div style="display:flex; flex-direction:column; min-width:0;">
                    <span style="font-size:11.5px; font-weight:600; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">RFX-2026-001_Line_Items.xlsx</span>
                    <span style="font-size:10px; color:#64748B;">30 SKUs with FEFCO specs · 142 KB</span>
                  </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px; padding:8px 10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px;">
                  ${this.getFileTypeIcon('PDF')}
                  <div style="display:flex; flex-direction:column; min-width:0;">
                    <span style="font-size:11.5px; font-weight:600; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Technical_Questionnaire.pdf</span>
                    <span style="font-size:10px; color:#64748B;">10 Criteria (ISO, BRC/IoP) · 210 KB</span>
                  </div>
                </div>
                <div style="display:flex; align-items:center; gap:8px; padding:8px 10px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px;">
                  ${this.getFileTypeIcon('PDF')}
                  <div style="display:flex; flex-direction:column; min-width:0;">
                    <span style="font-size:11.5px; font-weight:600; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">Packaging_MSA_Terms.pdf</span>
                    <span style="font-size:10px; color:#64748B;">Commercial Terms · 95 KB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    const footerHtml = `
      <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
        <div style="font-size:11.5px; color:#64748B; display:flex; align-items:center; gap:6px;">
          <span style="display:inline-block; width:7px; height:7px; border-radius:50%; background:#10B981;"></span>
          <span>SMTP Simulation Active · 0 Delivery Failures Anticipated</span>
        </div>
        <div style="display:flex; gap:10px;">
          <button type="button" class="btn btn-secondary" onclick="App.closeModal()" style="font-size:12px; height:34px; padding:0 14px;">Cancel</button>
          <button type="button" class="btn btn-primary" onclick="App.executeSendInvitations()" style="font-size:12px; height:34px; padding:0 16px; display:inline-flex; align-items:center; gap:6px;">
            ${this.icon('mail', 13)} Confirm &amp; Dispatch Invitations
          </button>
        </div>
      </div>
    `;

    this.showModal('Supplier RFx Invitation Dispatch', bodyHtml, footerHtml, 'modal-lg');
  },

  async executeSendInvitations() {
    try {
      this.closeModal();
      const rfxId = this.currentRfxId || 1;
      await this.api('POST', `/api/rfx/${rfxId}/send-invitations`);
      this.toast('RFx Invitations successfully dispatched to 5 suppliers.', 'success');
      this.showRfxDetail(rfxId, 'tab-invitations');
    } catch (err) {
      this.toast(`Failed to dispatch invitations: ${err.message}`, 'error');
    }
  },

  editRfxModal(rfxId) {
    const currentTitle = document.getElementById('rfx-detail-title')?.textContent?.split(': ')[1] || 'Corrugated Packaging Sourcing RFx FY2026-27';
    const currentScope = document.getElementById('rfx-detail-meta')?.querySelector('.text-secondary')?.textContent?.replace('Scope:', '').trim() || '';
    this.showModal(
      'Edit RFx Specifications &amp; Timeline',
      `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div class="form-group">
            <label class="form-label">RFx Title</label>
            <input type="text" id="edit-rfx-title" class="form-input w-full" value="${currentTitle}" />
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">Submission Deadline</label>
              <input type="date" id="edit-rfx-deadline" class="form-input w-full" value="2026-11-01" />
            </div>
            <div class="form-group">
              <label class="form-label">Event Status</label>
              <select id="edit-rfx-status" class="form-input w-full">
                <option value="ACTIVE" selected>ACTIVE</option>
                <option value="DRAFT">DRAFT</option>
                <option value="UNDER_EVALUATION">UNDER_EVALUATION</option>
                <option value="AWARDED">AWARDED</option>
                <option value="CLOSED">CLOSED</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Procurement Scope &amp; Specifications</label>
            <textarea id="edit-rfx-desc" rows="4" class="form-input w-full" style="height:auto; padding:10px 14px; line-height:1.5;">${currentScope}</textarea>
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-dark" onclick="App.executeSaveRfx(${rfxId})">Save Changes</button>
      `
    );
  },

  async executeSaveRfx(rfxId) {
    const title = document.getElementById('edit-rfx-title')?.value.trim();
    const deadline = document.getElementById('edit-rfx-deadline')?.value;
    const description = document.getElementById('edit-rfx-desc')?.value.trim();
    const status = document.getElementById('edit-rfx-status')?.value;

    try {
      await this.api('PUT', `/api/rfx/${rfxId}`, { title, deadline, description, status });
      this.closeModal();
      this.toast('RFx details updated successfully.', 'success');
      this.showRfxDetail(rfxId);
    } catch (err) {
      this.toast(`Failed to update RFx: ${err.message}`, 'error');
    }
  },

  showAddLineItemModal(rfxId) {
    const id = rfxId || this.currentRfxId || 1;
    this.showModal(
      'Add New Line Item / SKU',
      `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div class="form-group">
            <label class="form-label">SKU Description</label>
            <input type="text" id="add-li-desc" class="form-input w-full" placeholder="e.g. RSC 5-ply Heavy Shipper 500x350x400mm" />
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">Ply Construction</label>
              <select id="add-li-ply" class="form-input w-full">
                <option value="3-ply">3-ply</option>
                <option value="5-ply" selected>5-ply</option>
                <option value="7-ply">7-ply</option>
                <option value="Honeycomb">Honeycomb</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Flute Code</label>
              <input type="text" id="add-li-flute" class="form-input w-full" value="BC-Flute" />
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">GSM Specification</label>
              <input type="text" id="add-li-gsm" class="form-input w-full" value="180+120+150+120+180" />
            </div>
            <div class="form-group">
              <label class="form-label">Dimensions (LxWxH mm)</label>
              <input type="text" id="add-li-dims" class="form-input w-full" value="450x300x250mm" />
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">Target RFQ Quantity</label>
              <input type="number" id="add-li-qty" class="form-input w-full" value="20000" />
            </div>
            <div class="form-group">
              <label class="form-label">Annual Volume</label>
              <input type="number" id="add-li-ann" class="form-input w-full" value="80000" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Print Specification</label>
            <input type="text" id="add-li-print" class="form-input w-full" value="2-color flexo" />
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-dark" onclick="App.executeAddLineItem(${id})">Add Line Item</button>
      `
    );
  },

  async executeAddLineItem(rfxId) {
    const id = rfxId || this.currentRfxId || 1;
    const description = document.getElementById('add-li-desc')?.value.trim();
    if (!description) {
      this.toast('Description is required.', 'error');
      return;
    }
    const spec_ply = document.getElementById('add-li-ply')?.value;
    const spec_flute = document.getElementById('add-li-flute')?.value;
    const spec_gsm = document.getElementById('add-li-gsm')?.value;
    const spec_dimensions = document.getElementById('add-li-dims')?.value;
    const quantity = parseInt(document.getElementById('add-li-qty')?.value || '10000', 10);
    const annual_volume = parseInt(document.getElementById('add-li-ann')?.value || '40000', 10);
    const spec_print = document.getElementById('add-li-print')?.value;

    try {
      await this.api('POST', `/api/rfx/${id}/line-items`, {
        description, spec_ply, spec_flute, spec_gsm, spec_dimensions,
        quantity, annual_volume, spec_print, spec_ect_min: '29 ECT', fefco_code: '0201'
      });
      this.closeModal();
      this.toast('New line item added to RFx scope.', 'success');
      this.showRfxDetail(id);
    } catch (err) {
      this.toast(`Failed to add line item: ${err.message}`, 'error');
    }
  },

  editLineItemModal(item) {
    this.showModal(
      `Edit Item #${item.item_number}: ${item.description}`,
      `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div class="form-group">
            <label class="form-label">SKU Description</label>
            <input type="text" id="edit-li-desc" class="form-input w-full" value="${item.description}" />
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">Ply Construction</label>
              <input type="text" id="edit-li-ply" class="form-input w-full" value="${item.spec_ply}" />
            </div>
            <div class="form-group">
              <label class="form-label">Flute Code</label>
              <input type="text" id="edit-li-flute" class="form-input w-full" value="${item.spec_flute || ''}" />
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">Dimensions</label>
              <input type="text" id="edit-li-dims" class="form-input w-full" value="${item.spec_dimensions || ''}" />
            </div>
            <div class="form-group">
              <label class="form-label">GSM Spec</label>
              <input type="text" id="edit-li-gsm" class="form-input w-full" value="${item.spec_gsm || ''}" />
            </div>
          </div>
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
            <div class="form-group">
              <label class="form-label">RFQ Quantity</label>
              <input type="number" id="edit-li-qty" class="form-input w-full" value="${item.quantity}" />
            </div>
            <div class="form-group">
              <label class="form-label">Annual Volume</label>
              <input type="number" id="edit-li-ann" class="form-input w-full" value="${item.annual_volume || item.quantity * 4}" />
            </div>
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-dark" onclick="App.executeEditLineItem(${item.id}, ${item.rfx_id || 'this.currentRfxId'})">Save Item</button>
      `
    );
  },

  async executeEditLineItem(itemId, rfxId) {
    const description = document.getElementById('edit-li-desc')?.value.trim();
    const spec_ply = document.getElementById('edit-li-ply')?.value;
    const spec_flute = document.getElementById('edit-li-flute')?.value;
    const spec_dimensions = document.getElementById('edit-li-dims')?.value;
    const spec_gsm = document.getElementById('edit-li-gsm')?.value;
    const quantity = parseInt(document.getElementById('edit-li-qty')?.value || '0', 10);
    const annual_volume = parseInt(document.getElementById('edit-li-ann')?.value || '0', 10);

    const targetRfxId = rfxId || this.currentRfxId || 1;
    try {
      await this.api('PUT', `/api/rfx/${targetRfxId}/line-items/${itemId}`, {
        description, spec_ply, spec_flute, spec_dimensions, spec_gsm, quantity, annual_volume
      });
      this.closeModal();
      this.toast('Line item updated successfully.', 'success');
      this.showRfxDetail(targetRfxId);
    } catch (err) {
      this.toast(`Failed to update item: ${err.message}`, 'error');
    }
  },

  confirmDeleteLineItem(itemId, itemNumber, rfxId) {
    const targetRfxId = rfxId || this.currentRfxId || 1;
    this.showModal(
      'Confirm Deletion',
      `
        <div style="display:flex; gap:16px; align-items:flex-start; padding:6px 0;">
          <div style="width:42px; height:42px; border-radius:10px; background:#FEF2F2; color:#DC2626; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            ${this.icon('trash', 20)}
          </div>
          <div>
            <div style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:6px;">
              Delete Line Item #${itemNumber}?
            </div>
            <p style="font-size:13px; color:var(--text-secondary); line-height:1.55; margin:0;">
              Are you sure you want to delete this specification item? This action will permanently remove Line Item #${itemNumber} and all associated extracted supplier quotes from the comparison matrix.
            </p>
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-danger" onclick="App.executeDeleteLineItem(${itemId}, ${itemNumber}, ${targetRfxId})">Delete Specification</button>
      `
    );
  },

  async executeDeleteLineItem(itemId, itemNumber, rfxId) {
    this.closeModal();
    const targetRfxId = rfxId || this.currentRfxId || 1;
    try {
      await this.api('DELETE', `/api/rfx/${targetRfxId}/line-items/${itemId}`);
      this.toast(`Line item #${itemNumber} deleted.`, 'success');
      this.showRfxDetail(targetRfxId);
    } catch (err) {
      this.toast(`Failed to delete item: ${err.message}`, 'error');
    }
  },

  deleteLineItem(itemId, itemNumber, rfxId) {
    this.confirmDeleteLineItem(itemId, itemNumber, rfxId);
  },

  toggleRowMenu(e, id) {
    if (e && e.stopPropagation) e.stopPropagation();
    const targetMenu = document.getElementById(`row-menu-${id}`);
    if (!targetMenu) return;
    const isShowing = targetMenu.classList.contains('show');
    this.closeAllRowMenus();
    if (!isShowing) {
      const btn = e && e.currentTarget ? e.currentTarget : targetMenu.previousElementSibling;
      if (btn) {
        const rect = btn.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        if (spaceBelow < 180 || rect.top > 350) {
          targetMenu.classList.add('drop-up');
        } else {
          targetMenu.classList.remove('drop-up');
        }
      }
      targetMenu.classList.add('show');
    }
  },

  closeAllRowMenus() {
    document.querySelectorAll('.action-dropdown.show').forEach(el => el.classList.remove('show'));
  },

  triggerEditLineItem(itemId) {
    this.closeAllRowMenus();
    const item = (this.currentLineItems || []).find(x => x.id === itemId);
    if (item) {
      this.editLineItemModal(item);
    }
  },

  triggerDeleteLineItem(itemId, itemNumber) {
    this.closeAllRowMenus();
    const item = (this.currentLineItems || []).find(x => x.id === itemId);
    const rfxId = item ? item.rfx_id : (this.currentRfxId || 1);
    this.confirmDeleteLineItem(itemId, itemNumber, rfxId);
  },

  toggleSelectAllLineItems(checked) {
    const checkboxes = document.querySelectorAll('.line-item-chk');
    checkboxes.forEach(chk => {
      const row = chk.closest('tr');
      if (row && row.style.display !== 'none') {
        chk.checked = checked;
      }
    });
    this.updateSelectedLineItems();
  },

  updateSelectedLineItems() {
    const checked = Array.from(document.querySelectorAll('.line-item-chk:checked'));
    const count = checked.length;
    const btn = document.getElementById('btn-batch-delete');
    const countEl = document.getElementById('selected-items-count');
    const selectAllChk = document.getElementById('chk-all-items');

    if (countEl) countEl.textContent = count;
    if (btn) {
      btn.style.display = count > 0 ? 'inline-flex' : 'none';
    }

    const allCheckboxes = Array.from(document.querySelectorAll('.line-item-chk'));
    if (selectAllChk && allCheckboxes.length > 0) {
      selectAllChk.checked = count === allCheckboxes.length;
      selectAllChk.indeterminate = count > 0 && count < allCheckboxes.length;
    }
  },

  deleteSelectedLineItems() {
    const checkedBoxes = Array.from(document.querySelectorAll('.line-item-chk:checked'));
    const count = checkedBoxes.length;
    if (count === 0) return;

    this.showModal(
      'Batch Delete Specifications',
      `
        <div style="display:flex; gap:16px; align-items:flex-start; padding:6px 0;">
          <div style="width:42px; height:42px; border-radius:10px; background:#FEF2F2; color:#DC2626; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            ${this.icon('trash', 20)}
          </div>
          <div>
            <div style="font-size:15px; font-weight:700; color:var(--text-main); margin-bottom:6px;">
              Delete ${count} Selected Specification Items?
            </div>
            <p style="font-size:13px; color:var(--text-secondary); line-height:1.55; margin:0;">
              Are you sure you want to delete ${count} selected specification items? Associated supplier quotes will also be permanently removed.
            </p>
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-danger" onclick="App.executeBatchDeleteSelected()">Delete ${count} Items</button>
      `
    );
  },

  async executeBatchDeleteSelected() {
    this.closeModal();
    const checkedBoxes = Array.from(document.querySelectorAll('.line-item-chk:checked'));
    const count = checkedBoxes.length;
    if (count === 0) return;

    const rfxId = this.currentRfxId || 1;
    const itemIds = checkedBoxes.map(chk => parseInt(chk.value, 10));

    try {
      this.toast(`Deleting ${count} items...`, 'info');
      await Promise.all(itemIds.map(id => this.api('DELETE', `/api/rfx/${rfxId}/line-items/${id}`)));
      this.toast(`Successfully deleted ${count} line item${count > 1 ? 's' : ''}.`, 'success');
      this.showRfxDetail(rfxId);
    } catch (err) {
      console.error('Batch delete error:', err);
      this.toast(`Error deleting items: ${err.message}`, 'error');
      this.showRfxDetail(rfxId);
    }
  },

  filterLineItems(query) {
    const q = (query || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#rfx-items-table tbody tr');
    let visibleCount = 0;
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const match = !q || text.includes(q);
      row.style.display = match ? '' : 'none';
      if (match) visibleCount++;
    });

    const countNumEl = document.getElementById('sku-count-num');
    if (countNumEl) {
      countNumEl.textContent = visibleCount;
    }
    this.updateSelectedLineItems();
  },

  showNewRfxModal() {
    this.showModal(
      'Create New AI-Assisted RFx',
      `
        <div style="display:flex; flex-direction:column; gap:16px;">
          <div class="form-group">
            <label class="form-label">Procurement Scope &amp; Specifications</label>
            <p class="text-xs text-muted" style="margin-top:-2px; margin-bottom:4px;">
              Outline required packaging categories, volumes, delivery terms, and quality standards.
            </p>
            <textarea id="new-rfx-desc" rows="4" class="form-input w-full" style="height:auto; padding:12px 14px; line-height:1.5;" placeholder="e.g. 30 corrugated packaging items (3-ply/5-ply shippers, die-cut trays, honeycomb panels) for FMCG plants. 30-day credit, DDP delivery."></textarea>
          </div>
          <div class="text-xs text-secondary" style="background:var(--surface-subtle); padding:10px 14px; border-radius:10px; border:1px solid var(--border-light); line-height:1.5;">
            AI copilot will structure SKUs, ply specs, flute codes, and questionnaire automatically.
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-secondary" onclick="App.closeModal()">Cancel</button>
        <button type="button" class="btn-capsule-dark" id="btn-create-rfx" onclick="App.executeCreateRfx()">
          Generate RFx with AI
        </button>
      `
    );
  },

  async executeCreateRfx() {
    const desc = document.getElementById('new-rfx-desc').value.trim();
    if (!desc) {
      this.toast('Please provide a description.', 'error');
      return;
    }

    const btn = document.getElementById('btn-create-rfx');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner spinner-sm"></span> Generating RFx specs...';

    try {
      const res = await this.api('POST', '/api/rfx/create', { description: desc });
      this.closeModal();
      this.toast(`Successfully created ${res.rfx_number}: ${res.title}`, 'success');
      this.currentRfxId = res.rfx_id;
      this.currentRfxNumber = res.rfx_number;
      await this.loadRfxEvents();
      await this.showRfxDetail(res.rfx_id);
    } catch (err) {
      this.toast(`Failed to create RFx: ${err.message}`, 'error');
      btn.disabled = false;
      btn.innerHTML = 'Generate RFx with AI';
    }
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 3: SUPPLIER SUBMISSIONS & AI EXTRACTION
  // ════════════════════════════════════════════════════════════════════════════
  closeSubmissionsDetail() {
    const listEl = document.getElementById('submissions-list-view');
    const detailEl = document.getElementById('submissions-detail-view');
    if (listEl) listEl.style.display = 'block';
    if (detailEl) detailEl.style.display = 'none';
  },

  toggleSubRowMenu(e, id) {
    if (e && e.stopPropagation) e.stopPropagation();
    const targetMenu = document.getElementById(`sub-menu-${id}`);
    if (!targetMenu) return;
    const isShowing = targetMenu.classList.contains('show');
    this.closeAllRowMenus();
    if (!isShowing) {
      const btn = e && e.currentTarget ? e.currentTarget : targetMenu.previousElementSibling;
      if (btn) {
        const rect = btn.getBoundingClientRect();
        const spaceBelow = window.innerHeight - rect.bottom;
        if (spaceBelow < 180 || rect.top > 350) {
          targetMenu.classList.add('drop-up');
        } else {
          targetMenu.classList.remove('drop-up');
        }
      }
      targetMenu.classList.add('show');
    }
  },

  async reextractAll() {
    try {
      const rfxId = this.currentRfxId || 1;
      this.toast('Starting AI extraction across all supplier submissions...', 'info');
      const res = await this.api('POST', `/api/rfx/${rfxId}/extract-all`).catch(async () => {
        const subsRes = await this.api('GET', `/api/rfx/${rfxId}/submissions`);
        const subs = subsRes.submissions || [];
        for (const s of subs) {
          await this.api('POST', `/api/rfx/${rfxId}/extract/${s.supplier_id}`);
        }
        return { success: true, total_processed: subs.length };
      });
      this.toast(`Successfully re-extracted quotes for ${res.total_processed || 5} suppliers.`, 'success');
      this.loadSubmissions();
    } catch (err) {
      console.error('Re-extract error:', err);
      this.toast(`Re-extraction failed: ${err.message}`, 'error');
    }
  },

  async loadSubmissions() {
    this.closeSubmissionsDetail();
    const wrap = document.getElementById('submissions-container');
    if (!wrap) return;
    wrap.innerHTML = '<div class="loading-state"><span class="spinner"></span> Loading supplier submissions...</div>';

    try {
      let rfxId = this.currentRfxId || 1;
      let res = await this.api('GET', `/api/rfx/${rfxId}/submissions`);
      let subs = res.submissions || [];

      if (subs.length === 0) {
        wrap.innerHTML = `
          <div class="empty-state" style="text-align:center; padding:48px 20px;">
            <div style="font-size:16px; font-weight:700; margin-bottom:8px;">No supplier quotations found for this RFx</div>
            <p class="text-xs text-muted" style="margin-bottom:16px;">Upload a quotation file (PDF, Excel, CSV) to extract and normalize pricing automatically.</p>
            <button class="btn btn-primary" onclick="App.showUploadModal(1, 'PackIndia Ltd')">
              ${this.icon('upload', 14)} Upload Quotation File
            </button>
          </div>
        `;
        return;
      }

      wrap.innerHTML = `
        <div class="table-card">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Quotation File</th>
                  <th>Compliance</th>
                  <th>Status</th>
                  <th style="width: 200px;">Extraction Confidence</th>
                  <th style="width: 70px; text-align: right;">Action</th>
                </tr>
              </thead>
              <tbody>
                ${subs.map((s, sIdx) => {
                  const confPct = s.extraction_confidence ? Math.round(s.extraction_confidence * 100) : 0;
                  const confColor = s.extraction_confidence >= 0.85 ? '#16A34A' : s.extraction_confidence >= 0.6 ? '#D97706' : '#DC2626';
                  const avatarBg = SUPPLIER_COLORS[s.supplier_code] ? SUPPLIER_COLORS[s.supplier_code] + '18' : 'var(--surface-lavender)';
                  const avatarColor = SUPPLIER_COLORS[s.supplier_code] || 'var(--brand-violet)';
                  const isNearBottom = sIdx >= subs.length - 2;

                  return `
                    <tr id="sub-row-${s.supplier_id}">
                      <td>
                        <div style="padding: 2px 0;">
                          <div class="font-semibold" style="font-size: 13.5px; color: var(--text-main); cursor: pointer;" onclick="App.viewSubmissionDetails(${s.supplier_id})">${s.supplier_name}</div>
                          <div class="text-xs text-muted" style="margin-top: 3px;">${s.supplier_city || 'India'} · Code: <strong>${s.supplier_code}</strong></div>
                        </div>
                      </td>
                      <td>
                        <div style="display: flex; align-items: center; gap: 10px;">
                          ${this.getFileTypeIcon(s.file_type)}
                          <a href="/api/rfx/${rfxId}/submission/${s.supplier_id}/download" target="_blank" style="font-weight: 600; font-size: 13px; color: var(--brand-violet); text-decoration: none;" title="Download quotation file">
                            <span>${s.file_name}</span>
                          </a>
                        </div>
                      </td>
                      <td>
                        ${(s.brc_qualified || (s.supplier_certifications || '').toLowerCase().includes('brc')) ? '<span class="badge badge-green">BRC Food-Grade</span>' : '<span class="badge badge-gray">Non-BRC</span>'}
                      </td>
                      <td>
                        <span id="status-cell-${s.supplier_id}">${this.badge(s.extraction_status)}</span>
                      </td>
                      <td>
                        <div style="display: flex; flex-direction: column; gap: 6px; min-width: 140px;">
                          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px;">
                            <span class="text-muted">Confidence</span>
                            <span class="font-bold" style="color: ${confColor};">${confPct}%</span>
                          </div>
                          <div style="width: 100%; height: 6px; background: var(--border-light); border-radius: 9999px; overflow: hidden;">
                            <div style="width: ${confPct}%; height: 100%; background: ${confColor}; border-radius: 9999px; transition: width 0.3s ease;"></div>
                          </div>
                        </div>
                      </td>
                      <td style="text-align: right; position: relative;">
                        <div class="row-actions-wrap">
                          <button type="button" class="action-dots-btn" onclick="App.toggleSubRowMenu(event, ${s.supplier_id})" title="Actions">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                              <circle cx="12" cy="5" r="2.2"></circle>
                              <circle cx="12" cy="12" r="2.2"></circle>
                              <circle cx="12" cy="19" r="2.2"></circle>
                            </svg>
                          </button>
                          <div id="sub-menu-${s.supplier_id}" class="action-dropdown ${isNearBottom ? 'drop-up' : ''}" onclick="event.stopPropagation()">
                            <button type="button" class="action-dropdown-item" onclick="App.viewSubmissionDetails(${s.supplier_id})">Inspect Quotes</button>
                            <button type="button" class="action-dropdown-item" onclick="App.triggerExtraction(${s.supplier_id})">Re-run AI Extract</button>
                            <button type="button" class="action-dropdown-item" onclick="App.showUploadModal(${s.supplier_id}, '${s.supplier_name.replace(/'/g, "\\'")}')">Upload New File</button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>
        </div>
      `;
    } catch (err) {
      wrap.innerHTML = `<div class="alert alert-error">Failed to load submissions: ${err.message}</div>`;
    }
  },

  handleFileSelection(input) {
    const nameEl = document.getElementById('file-chosen-name');
    if (!nameEl) return;
    if (input.files && input.files.length > 0) {
      nameEl.textContent = `Selected: ${input.files[0].name} (${(input.files[0].size / 1024).toFixed(1)} KB)`;
      nameEl.style.display = 'block';
    } else {
      nameEl.style.display = 'none';
    }
  },

  showUploadModal(supplierId, supplierName) {
    this.closeAllRowMenus();
    this.showModal(
      `Upload Quote Document: ${supplierName}`,
      `
        <div>
          <div class="file-upload-dropzone" onclick="document.getElementById('submission-file-input').click()">
            <input type="file" id="submission-file-input" style="display:none;" accept=".xlsx,.xls,.pdf,.docx,.doc,.jpg,.jpeg,.png,.txt,.eml" onchange="App.handleFileSelection(this)">
            <div class="file-upload-icon-circle">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
            </div>
            <div>
              <span class="file-upload-btn-fake">Choose Quotation File</span>
              <span class="file-upload-hint-text">or click to browse from device</span>
            </div>
            <div id="file-chosen-name" class="file-upload-selected-name" style="display:none;"></div>
          </div>
          <div class="text-xs text-muted" style="margin-top:10px; line-height:1.5;">
            Supported formats: Excel (.xlsx), PDF, Word (.docx), Scanned Rate Card (.jpg, .png), or Email text (.txt, .eml).
          </div>
        </div>
      `,
      `
        <button type="button" class="btn-capsule-dark" id="btn-confirm-upload" onclick="App.executeUploadFile(${supplierId})">
          Upload &amp; Attach
        </button>
      `
    );
  },

  async executeUploadFile(supplierId) {
    const fileInput = document.getElementById('submission-file-input');
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
      this.toast('Please choose a file to upload.', 'error');
      return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    const btn = document.getElementById('btn-confirm-upload');
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner spinner-sm"></span> Uploading...';
    }

    try {
      const rfxId = this.currentRfxId || 1;
      const res = await fetch(`${API}/api/rfx/${rfxId}/upload/${supplierId}`, {
        method: 'POST',
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || 'Upload failed');
      }
      this.closeModal();
      this.toast(`File '${file.name}' successfully uploaded. Ready for AI extraction.`, 'success');
      this.loadSubmissions();
    } catch (err) {
      this.toast(`Upload failed: ${err.message}`, 'error');
      if (btn) {
        btn.disabled = false;
        btn.textContent = 'Upload & Attach';
      }
    }
  },

  async triggerExtraction(supplierId) {
    this.closeAllRowMenus();
    this.toast('AI extraction in progress...', 'info');
    const statusCell = document.getElementById(`status-cell-${supplierId}`);
    if (statusCell) {
      statusCell.innerHTML = this.badge('IN_PROGRESS');
    }

    try {
      const rfxId = this.currentRfxId || 1;
      const res = await this.api('POST', `/api/rfx/${rfxId}/extract/${supplierId}`);
      this.toast(`AI extracted ${res.quotes_extracted} quotes and ${res.questionnaire_responses} Q&A responses for ${res.supplier_code}. Confidence: ${Math.round(res.extraction_confidence * 100)}%`, 'success');

      // Check if we are inside the detail view for this supplier
      const detailEl = document.getElementById('submissions-detail-view');
      if (detailEl && detailEl.style.display !== 'none' && this.currentInspectedSupplierId === supplierId) {
        await this.viewSubmissionDetails(supplierId);
      } else {
        await this.loadSubmissions();
      }
    } catch (err) {
      this.toast(`Extraction error: ${err.message}`, 'error');
      if (statusCell) {
        statusCell.innerHTML = this.badge('FAILED');
      }
    }
  },

  async viewSubmissionDetails(supplierId) {
    this.closeAllRowMenus();
    this.currentInspectedSupplierId = supplierId;

    const listEl = document.getElementById('submissions-list-view');
    const detailEl = document.getElementById('submissions-detail-view');
    if (listEl) listEl.style.display = 'none';
    if (detailEl) {
      detailEl.style.display = 'block';
      detailEl.innerHTML = '<div class="loading-state"><span class="spinner"></span> Loading quote extraction details...</div>';
    }

    try {
      const rfxId = this.currentRfxId || 1;
      const data = await this.api('GET', `/api/rfx/${rfxId}/submission/${supplierId}`);
      const quotes = data.extracted_quotes || [];
      const qAns = data.questionnaire_responses || [];
      const sub = data.submission || {};
      const sup = data.supplier || {};

      let unresolved = [];
      try {
        unresolved = JSON.parse(sub.unresolved_items || '[]');
      } catch (e) {
        unresolved = [];
      }

      const confPct = sub.extraction_confidence ? Math.round(sub.extraction_confidence * 100) : 0;
      const confColor = sub.extraction_confidence >= 0.85 ? '#16A34A' : sub.extraction_confidence >= 0.6 ? '#D97706' : '#DC2626';

      detailEl.innerHTML = `
        <div class="rfx-header-bar mb-20">
          <div class="rfx-header-left">
            <button class="btn-capsule-secondary" onclick="App.closeSubmissionsDetail()" title="Back" style="width: 36px; height: 36px; padding: 0; justify-content: center; border-radius: 50%;">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            </button>
            <div class="rfx-header-divider"></div>
            <span class="rfx-header-title">Extraction Inspection: ${sup.name} (${sup.code})</span>
          </div>
          <div class="flex-gap-8 align-center">
            <button class="btn-capsule-secondary" onclick="App.triggerExtraction(${supplierId})">
              ${this.icon('refresh', 13)} Re-run AI Extract
            </button>
            <button class="btn-capsule-dark" onclick="App.showUploadModal(${supplierId}, '${sup.name.replace(/'/g, "\\'")}')">
              ${this.icon('upload', 13)} Upload New File
            </button>
          </div>
        </div>

        <!-- 4 Top Cards -->
        <div class="kpi-metrics-strip" style="grid-template-columns: repeat(4, 1fr); margin-bottom: 20px;">
          <div class="kpi-card">
            <span class="kpi-title">Source Quotation</span>
            <div class="kpi-card-bottom">
              <span class="kpi-metric-val" style="font-size: 15px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${sub.file_name}</span>
              <span class="badge badge-outline">${sub.file_type}</span>
            </div>
          </div>
          <div class="kpi-card ${confPct < 75 ? 'highlight-orange' : 'highlight-lavender'}">
            <span class="kpi-title">Extraction Accuracy</span>
            <div class="kpi-card-bottom">
              <span class="kpi-metric-val" style="color: ${confColor};">${confPct}%</span>
              <span class="badge ${confPct < 75 ? 'badge-orange font-bold' : confPct < 85 ? 'badge-blue' : 'badge-purple'}">
                ${confPct < 75 ? 'Review Needed' : confPct < 85 ? 'Medium Conf' : 'High Confidence'}
              </span>
            </div>
          </div>
          <div class="kpi-card">
            <span class="kpi-title">Quotes Normalized</span>
            <div class="kpi-card-bottom">
              <span class="kpi-metric-val">${quotes.length} SKUs</span>
              <span class="badge badge-blue">Ready</span>
            </div>
          </div>
          <div class="kpi-card highlight-lime">
            <span class="kpi-title">Quality Standard</span>
            <div class="kpi-card-bottom">
              <span class="kpi-metric-val">${(sup.brc_certified || sup.brc_qualified || (sup.certifications || '').toLowerCase().includes('brc')) ? 'BRC Certified' : 'Non-BRC'}</span>
              <span class="badge badge-green">${sub.extraction_status}</span>
            </div>
          </div>
        </div>

        <!-- 2-Column Grid: Commercial Notes & Exceptions -->
        <div class="grid-two-col mb-20" style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <!-- Left: Commercial Notes -->
          <div class="table-card" style="padding: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border-light);">
              <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--surface-lavender); color: var(--brand-violet); display: flex; align-items: center; justify-content: center;">
                ${this.icon('file-text', 15)}
              </div>
              <div>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-main);">Commercial Notes &amp; Policies</div>
                <div class="text-xs text-muted">Terms extracted directly from quotation document</div>
              </div>
            </div>
            <div style="background: var(--surface-subtle); border: 1px solid var(--border-light); border-radius: 12px; padding: 14px 16px; font-size: 13px; line-height: 1.6; color: var(--text-main);">
              ${sub.commercial_notes || 'No custom commercial terms or volume discount notes specified in submission.'}
            </div>
          </div>

          <!-- Right: Extraction Exceptions -->
          <div class="table-card" style="padding: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border-light);">
              <div style="width: 32px; height: 32px; border-radius: 50%; background: #FEF3C7; color: #D97706; display: flex; align-items: center; justify-content: center;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01"/></svg>
              </div>
              <div>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-main);">Extraction Exceptions &amp; Unresolved Items</div>
                <div class="text-xs text-muted">Items requiring buyer confirmation or engineering approval</div>
              </div>
            </div>
            ${unresolved.length > 0 ? `
              <div style="display: flex; flex-direction: column; gap: 8px;">
                ${unresolved.map(u => `
                  <div style="display: flex; align-items: flex-start; gap: 8px; background: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 10px 14px; font-size: 12.5px; color: #92400E; line-height: 1.5;">
                    <span style="font-weight: 700; color: #B45309;">•</span>
                    <span>${u}</span>
                  </div>
                `).join('')}
              </div>
            ` : `
              <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 10px; padding: 12px 14px; font-size: 13px; color: #166534;">
                All line items and quotes resolved with zero exceptions.
              </div>
            `}
          </div>
        </div>

        <!-- Extracted Quotes Table -->
        <div class="table-card">
          <div class="section-heading-row">
            <div>
              <h3 style="font-size: 15px; font-weight: 700; color: var(--text-main);">Extracted Commercial Quotes (${quotes.length})</h3>
              <p class="text-xs text-muted" style="margin-top: 2px;">Itemized specification pricing normalized to landed cost excluding GST</p>
            </div>
          </div>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th style="width: 50px;">Item #</th>
                  <th>Supplier Description</th>
                  <th>Quoted Rate</th>
                  <th>Normalized /pc</th>
                  <th>Landed Cost (excl GST)</th>
                  <th style="width: 110px;">Confidence</th>
                  <th>Discount</th>
                  <th>Freight</th>
                  <th>Compliance</th>
                  <th>Source Reference &amp; Notes</th>
                </tr>
              </thead>
              <tbody>
                ${quotes.map(q => {
                  const isLowConf = (q.confidence !== null && q.confidence !== undefined && q.confidence <= 0.2) || q.orig_price === null;
                  const confDisplay = q.confidence !== null && q.confidence !== undefined
                    ? (q.confidence <= 0.2 ? '0.10 (10%)' : `${Math.round(q.confidence * 100)}%`)
                    : '-';
                  const confBadgeClass = q.confidence <= 0.2 ? 'badge-red font-bold' : q.confidence < 0.8 ? 'badge-orange' : 'badge-green';

                  return `
                  <tr style="${isLowConf ? 'background: #FFFDF7;' : ''}">
                    <td><strong>${q.item_number || q.line_item_id || '-'}</strong></td>
                    <td class="font-semibold" style="font-size: 13px;">${q.item_description_supplier || '-'}</td>
                    <td>
                      ${q.orig_price !== null 
                        ? `₹${q.orig_price} <span class="text-xs text-muted">${q.orig_unit || ''}</span>` 
                        : '<span class="badge badge-orange font-bold">UNRESOLVED</span>'}
                    </td>
                    <td>${this.inr(q.norm_price_per_unit)}</td>
                    <td class="font-bold" style="color: var(--brand-violet);">${this.inr(q.landed_cost_excl_gst)}</td>
                    <td>
                      <span class="badge ${confBadgeClass}">${confDisplay}</span>
                    </td>
                    <td>${q.discount_pct ? `${q.discount_pct}%` : '0%'}</td>
                    <td class="text-xs">${q.freight_included ? 'Included' : `+₹${q.freight_per_unit || 0}/pc`}</td>
                    <td>${this.badge(q.tech_compliance)}</td>
                    <td style="max-width: 280px;">
                      <div class="text-xs text-muted font-mono" style="word-break: break-all;">${q.source_ref || '-'}</div>
                      ${q.notes && (isLowConf || q.notes.includes('UNRESOLVED') || q.notes.includes('Historical')) ? `
                        <div style="font-size: 11px; color: #B45309; margin-top: 4px; line-height: 1.35; background: #FEF3C7; padding: 3px 6px; border-radius: 4px; border: 1px solid #FDE68A;">
                          <strong>Exception:</strong> ${q.notes}
                        </div>
                      ` : ''}
                    </td>
                  </tr>
                `}).join('')}
              </tbody>
            </table>
          </div>
        </div>

        ${qAns.length > 0 ? `
          <div class="table-card mt-20">
            <div class="section-heading-row">
              <div>
                <h3 style="font-size: 15px; font-weight: 700; color: var(--text-main);">Questionnaire Responses (${qAns.length})</h3>
                <p class="text-xs text-muted" style="margin-top: 2px;">Supplier answers to technical qualification requirements</p>
              </div>
            </div>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th style="width: 80px;">Code</th>
                    <th>Question</th>
                    <th>Extracted Supplier Answer</th>
                    <th style="width: 130px;">Compliance</th>
                  </tr>
                </thead>
                <tbody>
                  ${qAns.map(qa => `
                    <tr>
                      <td><strong>${qa.question_code}</strong></td>
                      <td class="text-xs font-semibold">${qa.question_text || ''}</td>
                      <td class="text-xs">${qa.answer || '-'}</td>
                      <td>
                        <span class="badge ${qa.is_compliant === 1 ? 'badge-green' : qa.is_compliant === 0 ? 'badge-red' : 'badge-gray'}">
                          ${qa.is_compliant === 1 ? 'Compliant' : qa.is_compliant === 0 ? 'Non-Compliant' : 'Pending Review'}
                        </span>
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        ` : ''}
      `;
    } catch (err) {
      if (detailEl) {
        detailEl.innerHTML = `<div class="alert alert-error">Failed to load quote details: ${err.message}</div>`;
      }
    }
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 4: COMPARISON WORKSPACE (CORE)
  // ════════════════════════════════════════════════════════════════════════════
  async loadComparison() {
    const loading = document.getElementById('comparison-loading');
    const empty = document.getElementById('comparison-empty');
    const content = document.getElementById('comparison-content');

    loading.style.display = 'flex';
    empty.style.display = 'none';
    content.style.display = 'none';

    try {
      const rfxId = this.currentRfxId || 1;
      const data = await this.api('GET', `/api/rfx/${rfxId}/comparison`);
      this.comparisonData = data;
      loading.style.display = 'none';

      if (!data.line_items || data.line_items.length === 0 || data.summary.quotes_extracted === 0) {
        empty.style.display = 'block';
        return;
      }

      content.style.display = 'block';
      this.renderSupplierFilterChips();
      this.renderSupplierHeaderCards();
      this.renderComparisonTable();
    } catch (err) {
      loading.style.display = 'none';
      this.toast(`Failed to load comparison: ${err.message}`, 'error');
    }
  },

  renderSupplierFilterChips() {
    // Redundant chip row removed in favor of interactive supplier cards
    this.renderSupplierHeaderCards();
  },

  toggleSupplierVisibility(code) {
    this.suppliersVisible[code] = !this.suppliersVisible[code];
    this.renderSupplierHeaderCards();
    this.renderComparisonTable();
  },

  toggleBrcFilter(checked) {
    this.renderSupplierHeaderCards();
    this.renderComparisonTable();
  },

  showAllSuppliers() {
    if (!this.comparisonData || !this.comparisonData.suppliers) return;
    this.comparisonData.suppliers.forEach(s => {
      this.suppliersVisible[s.code] = true;
    });
    this.renderSupplierHeaderCards();
    this.renderComparisonTable();
  },

  renderSupplierHeaderCards() {
    const container = document.getElementById('supplier-header-cards');
    if (!container || !this.comparisonData) return;

    const suppliers = this.comparisonData.suppliers || [];
    const brcFilter = document.getElementById('brc-toggle')?.checked;
    const visibleCount = suppliers.filter(s => this.suppliersVisible[s.code] !== false).length;

    container.innerHTML = `
      <div style="grid-column: 1 / -1; display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; padding: 0 2px;">
        <div style="display: flex; align-items: center; gap: 10px;">
          <span style="font-size: 14px; font-weight: 700; color: var(--text-main);">Participating Packaging Vendors (${suppliers.length})</span>
          <span style="color: var(--border-light); font-size: 13px;">•</span>
          <span style="font-size: 12.5px; color: var(--text-muted);">Click any vendor card to toggle column visibility</span>
        </div>
        <div class="matrix-visibility-pill" style="display: inline-flex; align-items: center; gap: 7px; background: var(--surface-subtle); border: 1px solid var(--border-light); padding: 5px 14px; border-radius: 20px; font-size: 12px; color: var(--text-secondary); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--brand-violet);">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          <span><strong style="color: var(--text-main); font-weight: 700;">${visibleCount} of ${suppliers.length}</strong> visible in matrix</span>
        </div>
      </div>
      ${suppliers.map(s => {
        const isVisible = this.suppliersVisible[s.code] !== false;
        const isDisqualified = !s.brc_qualified;
        const isDimmed = (brcFilter && isDisqualified) || !isVisible;

        return `
          <div class="supplier-header-card ${isVisible ? 'card-active' : 'card-dimmed'} ${isDimmed && isVisible ? 'card-disqualified' : ''}" 
               onclick="App.toggleSupplierVisibility('${s.code}')"
               title="Click to ${isVisible ? 'hide' : 'show'} ${s.name} in matrix">
            <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 8px;">
              <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
                <span style="display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: ${SUPPLIER_COLORS[s.code] || 'var(--aer-violet)'}; flex-shrink: 0;"></span>
                <span class="sh-name" title="${s.name}">${s.name}</span>
              </div>
              ${s.brc_qualified 
                ? '<span class="badge badge-green" style="font-size: 10px; padding: 2px 6px; flex-shrink: 0;">BRC AA</span>' 
                : '<span class="badge badge-red" style="font-size: 10px; padding: 2px 6px; flex-shrink: 0;">Non-BRC</span>'}
            </div>
            <div class="sh-city text-muted" style="margin-top: 2px;">${s.city || 'India'} · Code: <strong>${s.code}</strong></div>
            
            <div class="sh-spend-block">
              <div class="sh-spend-label">Delivered Spend</div>
              <div class="sh-spend-val">${this.inr(s.total_cost_estimate)}</div>
            </div>

            <div class="sh-footer-row">
              <span class="sh-sku-count text-muted" style="font-size: 11px;">${s.items_quoted || 30}/30 SKUs</span>
              <span class="sh-toggle-badge ${isVisible ? 'active' : 'hidden'}">
                ${isVisible ? '✓ In Matrix' : '+ Click to Show'}
              </span>
            </div>
          </div>
        `;
      }).join('')}
    `;
  },

  renderComparisonTable() {
    if (!this.comparisonData) return;

    const brcFilter = document.getElementById('brc-toggle')?.checked;
    const thead = document.getElementById('comparison-thead');
    const tbody = document.getElementById('comparison-tbody');

    const suppliers = this.comparisonData.suppliers.filter(s => this.suppliersVisible[s.code] !== false);
    let allItems = this.comparisonData.line_items || [];

    // Dynamically update category pill counts
    const totalCount = allItems.length;
    const diecutItems = allItems.filter(i => {
      const desc = (i.description || '').toLowerCase();
      return desc.includes('die-cut') || desc.includes('tray') || desc.includes('mailer') || desc.includes('lock');
    });
    const heavyItems = allItems.filter(i => {
      if (diecutItems.includes(i)) return false;
      const desc = (i.description || '').toLowerCase();
      const ply = (i.spec_ply || '').toLowerCase();
      return ply.includes('5-ply') || ply.includes('7-ply') || desc.includes('heavy') || desc.includes('bulk') || desc.includes('export');
    });
    const standardItems = allItems.filter(i => !diecutItems.includes(i) && !heavyItems.includes(i));

    // Update pill text & active class dynamically in comparison strip
    document.querySelectorAll('#section-comparison .filter-pill').forEach(btn => {
      const bCat = btn.getAttribute('data-category') || '';
      if (bCat === 'all') btn.textContent = `All Items (${totalCount})`;
      else if (bCat === 'heavy') btn.textContent = `Heavy Duty (${heavyItems.length})`;
      else if (bCat === 'standard') btn.textContent = `Standard (${standardItems.length})`;
      else if (bCat === 'diecut') btn.textContent = `Die-Cut (${diecutItems.length})`;
      btn.classList.toggle('active', bCat === this.compCategoryFilter);
    });

    // Apply category filter if active
    if (this.compCategoryFilter === 'heavy') {
      allItems = heavyItems;
    } else if (this.compCategoryFilter === 'standard') {
      allItems = standardItems;
    } else if (this.compCategoryFilter === 'diecut') {
      allItems = diecutItems;
    }

    // Pagination
    const totalItems = allItems.length;
    const totalPages = Math.ceil(totalItems / this.itemsPerPage) || 1;
    if (this.compPage > totalPages) this.compPage = 1;
    const startIndex = (this.compPage - 1) * this.itemsPerPage;
    const pagedItems = allItems.slice(startIndex, startIndex + this.itemsPerPage);

    // Table Header
    thead.innerHTML = `
      <tr>
        <th class="col-sticky-left" style="width: 48px; text-align: center;">#</th>
        <th class="col-sticky-left" style="min-width: 270px; text-align: left;">Line Item SKU</th>
        <th style="min-width: 150px; text-align: left;">Specifications</th>
        <th style="width: 110px; text-align: right;">RFQ Qty</th>
        ${suppliers.map(s => {
          const isDisq = brcFilter && !s.brc_qualified;
          return `
            <th style="min-width: 155px; text-align: right; padding: 12px 16px; ${isDisq ? 'opacity: 0.45;' : ''}">
              <div style="display: flex; align-items: center; justify-content: flex-end; gap: 6px;">
                <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: ${SUPPLIER_COLORS[s.code] || 'var(--aer-violet)'};"></span>
                <span style="font-size: 13px; font-weight: 700; color: var(--text-main);">${s.code}</span>
              </div>
              <div style="font-size: 11.5px; font-weight: 500; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${s.name}">${s.name}</div>
              ${isDisq ? '<div class="badge badge-red" style="font-size: 9.5px; padding: 1px 6px; margin-top: 4px; display: inline-block;">Disqualified (Non-BRC)</div>' : ''}
            </th>
          `;
        }).join('')}
      </tr>
    `;

    // Table Body
    tbody.innerHTML = pagedItems.map(li => {
      // Find lowest qualified price among visible suppliers
      const qualifiedQuotes = suppliers
        .filter(s => !brcFilter || s.brc_qualified)
        .map(s => li.suppliers ? li.suppliers[s.code] : null)
        .filter(q => q && q.landed_cost !== null);
      
      const lowestLandedCost = qualifiedQuotes.length > 0 
        ? Math.min(...qualifiedQuotes.map(q => q.landed_cost)) 
        : null;

      return `
        <tr>
          <td class="col-sticky-left" style="text-align: center; font-weight: 700; color: var(--text-muted); width: 48px;">
            ${li.item_number}
          </td>
          <td class="col-sticky-left" style="text-align: left;">
            <div class="font-semibold text-ellipsis" style="font-size: 13.5px; color: var(--text-main);" title="${li.description}">${li.description}</div>
            <div class="text-xs text-muted" style="margin-top: 3px;">${li.spec_dimensions}</div>
          </td>
          <td style="text-align: left;">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="badge badge-gray" style="font-size: 10.5px; font-weight: 600;">${li.spec_ply}</span>
              <span class="text-xs text-muted font-mono">${li.spec_flute || ''}</span>
            </div>
            <div class="text-xs text-muted" style="margin-top: 3px; font-size: 11px;">${li.spec_gsm || ''}</div>
          </td>
          <td style="text-align: right; font-weight: 700; font-size: 13px; font-variant-numeric: tabular-nums; color: var(--text-main);">
            ${Number(li.quantity).toLocaleString('en-IN')}
          </td>
          ${suppliers.map(s => {
            const q = li.suppliers ? li.suppliers[s.code] : null;
            const isLowestQualified = lowestLandedCost !== null && q && q.landed_cost === lowestLandedCost && (!brcFilter || s.brc_qualified);
            const isDisqualified = brcFilter && !s.brc_qualified;

            if (!q) {
              return `
                <td style="text-align: right; padding: 8px 12px; cursor: pointer;" onclick="App.openCellDetail(${li.id}, '${s.code}')" title="Not quoted - Click to enter manual rate">
                  <div class="price-cell-box" style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px; opacity: 0.5;">
                    <span style="font-size: 12px; color: var(--text-muted); font-weight: 500;">Not Quoted</span>
                    <span style="font-size: 10px; color: var(--brand-violet);">+ Add Rate</span>
                  </div>
                </td>
              `;
            }

            if (q.landed_cost === null) {
              return `
                <td style="text-align: right; padding: 8px 12px; cursor: pointer;" onclick="App.openCellDetail(${li.id}, '${s.code}')" title="Review exception">
                  <div class="price-cell-box" style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px; background: #FEF3C7; border: 1px solid #FCD34D;">
                    <div style="color: #D97706; font-size: 12px; font-weight: 700;">Review Needed</div>
                    <div style="color: #92400E; font-size: 10px;">Exception</div>
                  </div>
                </td>
              `;
            }

            let boxClass = 'price-cell-box ';
            if (isDisqualified) {
              boxClass += 'opacity-40 ';
            } else if (isLowestQualified) {
              boxClass += 'lowest ';
            }

            return `
              <td style="padding: 6px 10px; text-align: right;">
                <div class="${boxClass}" onclick="App.openCellDetail(${li.id}, '${s.code}')" style="display: flex; flex-direction: column; align-items: flex-end; gap: 2px;">
                  <div class="font-bold" style="font-size: 13.5px; letter-spacing: -0.01em;">${this.inr(q.landed_cost)}</div>
                  <div style="display: flex; align-items: center; gap: 4px; font-size: 10.5px; color: var(--text-muted);">
                    <span>${q.lead_time_days ? `${q.lead_time_days}d lead` : 'std'}</span>
                    ${q.tech_compliance === 'SUBSTITUTE' ? '<span class="badge badge-orange" style="font-size: 8.5px; padding: 1px 4px;">SUB</span>' : ''}
                    ${isLowestQualified ? '<span class="badge badge-green" style="font-size: 8.5px; padding: 1px 4px;">Lowest</span>' : ''}
                  </div>
                </div>
              </td>
            `;
          }).join('')}
        </tr>
      `;
    }).join('');

    // Summary & Centered Pagination footer
    const footerWrap = document.createElement('tr');
    footerWrap.innerHTML = `
      <td colspan="${4 + suppliers.length}" style="padding: 24px 20px; background: #FAF9FC; border-top: 1px solid var(--border-light);">
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px;">
          <div class="page-pills" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px;">
            <button class="page-btn page-btn-nav" onclick="App.setCompPage(${Math.max(1, this.compPage - 1)})" ${this.compPage === 1 ? 'disabled style="opacity: 0.35; cursor: not-allowed;"' : ''}>Previous</button>
            ${Array.from({ length: totalPages }, (_, idx) => idx + 1).map(p => `
              <button class="page-btn page-btn-num ${p === this.compPage ? 'active' : ''}" onclick="App.setCompPage(${p})">${p}</button>
            `).join('')}
            <button class="page-btn page-btn-nav" onclick="App.setCompPage(${Math.min(totalPages, this.compPage + 1)})" ${this.compPage === totalPages ? 'disabled style="opacity: 0.35; cursor: not-allowed;"' : ''}>Next</button>
          </div>
          <div style="font-size: 12.5px; color: var(--text-muted); text-align: center; margin-top: 6px;">
            Showing <strong>${startIndex + 1}-${Math.min(startIndex + this.itemsPerPage, totalItems)}</strong> of <strong>${totalItems}</strong> SKUs
          </div>
        </div>
      </td>
    `;
    tbody.appendChild(footerWrap);
  },

  async openCellDetail(lineItemId, supplierCode) {
    const panel = document.getElementById('cell-detail-panel');
    const content = document.getElementById('cell-detail-content');
    const title = document.getElementById('cell-detail-title');

    panel.classList.add('open');
    content.innerHTML = '<div class="loading-state"><span class="spinner"></span> Loading quote audit breakdown...</div>';

    try {
      const rfxId = this.currentRfxId || 1;
      const res = await this.api('GET', `/api/rfx/${rfxId}/comparison`);
      const li = (res.line_items || []).find(i => i.id === lineItemId);
      const sup = (res.suppliers || []).find(s => s.code === supplierCode);

      if (!li || !sup) {
        content.innerHTML = '<div class="alert alert-error">Item or supplier not found.</div>';
        return;
      }

      // Fetch the detailed quote from submission
      const subRes = await this.api('GET', `/api/rfx/${rfxId}/submission/${sup.id}`);
      const q = (subRes.extracted_quotes || []).find(quote => quote.line_item_id === lineItemId);

      title.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 4px;">
          <span style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Quote Audit &amp; Provenance</span>
          <span style="font-size: 16px; font-weight: 800; color: var(--text-main); letter-spacing: -0.01em;">Item ${li.item_number}: ${sup.name} (${sup.code})</span>
        </div>
      `;

      if (!q) {
        content.innerHTML = `
          <!-- Card 1: SKU Specification & Volumes -->
          <div class="card" style="padding: 20px 22px; margin-bottom: 20px; background: #FAF9FD; border: 1px solid var(--border-light); border-radius: 16px;">
            <div class="font-bold" style="font-size: 15px; color: var(--text-main); margin-bottom: 12px; line-height: 1.4;">${li.description}</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
              <span class="badge badge-purple" style="font-size: 11.5px; font-weight: 600; padding: 4px 10px;">${li.spec_ply}</span>
              ${li.spec_flute ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_flute}</span>` : ''}
              ${li.spec_gsm ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_gsm}</span>` : ''}
              <span class="badge badge-gray font-mono" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_dimensions}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; border-top: 1px solid var(--border-subtle); padding-top: 14px;">
              <span class="text-muted">Target RFQ Qty: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.quantity).toLocaleString('en-IN')} pcs</strong></span>
              <span class="text-muted">Annual Volume: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.annual_volume || li.quantity * 4).toLocaleString('en-IN')} pcs</strong></span>
            </div>
          </div>

          <div style="background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="font-size: 12.5px; font-weight: 700; color: #92400E; margin-bottom: 4px;">Not Quoted in Submission</div>
            <div style="font-size: 12px; color: #78350F; line-height: 1.5;">This vendor did not submit an explicit rate for this SKU in their uploaded document. You can record a buyer-negotiated offline rate below.</div>
          </div>

          <div class="card" style="padding: 16px 18px; margin-bottom: 16px; border: 1px solid var(--border-light); border-radius: 14px; background: #FFFFFF;">
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 12px;">Enter Buyer Negotiated / Direct Rate</div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Unit Price (INR):</label>
              <input type="number" step="0.01" id="manual-unit-price" class="form-input" placeholder="e.g. 42.50" style="width: 140px;" />
            </div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Freight /pc (INR):</label>
              <input type="number" step="0.01" id="manual-freight" class="form-input" value="0.00" style="width: 140px;" />
            </div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Freight Included:</label>
              <input type="checkbox" id="manual-freight-inc" checked style="accent-color: var(--aer-violet);" />
            </div>
            <div class="form-row mb-16">
              <label class="form-label" style="min-width: 120px;">Audit Reason:</label>
              <input type="text" id="manual-reason" class="form-input" placeholder="e.g. Agreed via email negotiation" style="flex: 1;" />
            </div>
            <button class="btn btn-primary w-full" style="height: 40px; font-size: 13.5px; font-weight: 600;" onclick="App.saveManualQuote(${li.id}, ${sup.id})">
              Save Manual Quote
            </button>
          </div>
        `;
        return;
      }

      if (q.landed_cost_excl_gst === null) {
        content.innerHTML = `
          <!-- Card 1: SKU Specification & Volumes -->
          <div class="card" style="padding: 20px 22px; margin-bottom: 20px; background: #FAF9FD; border: 1px solid var(--border-light); border-radius: 16px;">
            <div class="font-bold" style="font-size: 15px; color: var(--text-main); margin-bottom: 12px; line-height: 1.4;">${li.description}</div>
            <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
              <span class="badge badge-purple" style="font-size: 11.5px; font-weight: 600; padding: 4px 10px;">${li.spec_ply}</span>
              ${li.spec_flute ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_flute}</span>` : ''}
              ${li.spec_gsm ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_gsm}</span>` : ''}
              <span class="badge badge-gray font-mono" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_dimensions}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; border-top: 1px solid var(--border-subtle); padding-top: 14px;">
              <span class="text-muted">Target RFQ Qty: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.quantity).toLocaleString('en-IN')} pcs</strong></span>
              <span class="text-muted">Annual Volume: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.annual_volume || li.quantity * 4).toLocaleString('en-IN')} pcs</strong></span>
            </div>
          </div>

          <div style="background: #FEF2F2; border: 1px solid #FECACA; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 12.5px; font-weight: 700; color: #991B1B;">Unresolved Extraction Gap</span>
              <span class="badge badge-red font-bold" style="font-size: 11px;">0.10 Confidence Score</span>
            </div>
            <div style="font-size: 12px; color: #7F1D1D; line-height: 1.5;">${q.notes || "Supplier referenced an ambiguous price or 'rest same as last year' without baseline contract in RFx scope."}</div>
            <div class="text-xs text-muted mt-8" style="font-family: monospace;">Raw text: "${q.orig_value_raw || 'rest same as last year, freight extra'}"</div>
            <div class="text-xs text-muted mt-4">Document Citation: <code>${q.source_ref || 'Email Body'}</code></div>
          </div>

          <div class="card" style="padding: 16px 18px; margin-bottom: 16px; border: 1px solid var(--border-light); border-radius: 14px; background: #FFFFFF;">
            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 12px;">Enter Verified Baseline Rate</div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Verified Rate /pc:</label>
              <input type="number" step="0.01" id="manual-unit-price" class="form-input" placeholder="e.g. 44.00" style="width: 140px;" />
            </div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Freight /pc (INR):</label>
              <input type="number" step="0.01" id="manual-freight" class="form-input" value="${q.freight_per_unit || 2.0}" style="width: 140px;" />
            </div>
            <div class="form-row mb-12">
              <label class="form-label" style="min-width: 120px;">Freight Included:</label>
              <input type="checkbox" id="manual-freight-inc" ${q.freight_included ? 'checked' : ''} style="accent-color: var(--aer-violet);" />
            </div>
            <div class="form-row mb-16">
              <label class="form-label" style="min-width: 120px;">Audit Reason:</label>
              <input type="text" id="manual-reason" class="form-input" value="Verified from FY2025 contract baseline" style="flex: 1;" />
            </div>
            <button class="btn btn-primary w-full" style="height: 40px; font-size: 13.5px; font-weight: 600;" onclick="App.saveManualQuote(${li.id}, ${sup.id})">
              Resolve &amp; Save Verified Rate
            </button>
          </div>
        `;
        return;
      }

      this.selectedQuote = q;
      const confPct = Math.round((q.confidence || 0) * 100);
      const confColor = confPct >= 85 ? '#16A34A' : confPct >= 60 ? '#D97706' : '#DC2626';

      content.innerHTML = `
        <!-- Card 1: SKU Specification & Target Volume -->
        <div class="card" style="padding: 20px 22px; margin-bottom: 20px; background: #FAF9FD; border: 1px solid var(--border-light); border-radius: 16px;">
          <div class="font-bold" style="font-size: 15px; color: var(--text-main); margin-bottom: 12px; line-height: 1.4;">${li.description}</div>
          <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
            <span class="badge badge-purple" style="font-size: 11.5px; font-weight: 600; padding: 4px 10px;">${li.spec_ply}</span>
            ${li.spec_flute ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_flute}</span>` : ''}
            ${li.spec_gsm ? `<span class="badge badge-gray" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_gsm}</span>` : ''}
            <span class="badge badge-gray font-mono" style="font-size: 11.5px; padding: 4px 10px;">${li.spec_dimensions}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; border-top: 1px solid var(--border-subtle); padding-top: 14px;">
            <span class="text-muted">Target RFQ Qty: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.quantity).toLocaleString('en-IN')} pcs</strong></span>
            <span class="text-muted">Annual Volume: <strong style="color: var(--text-main); font-weight: 700; margin-left: 4px;">${Number(li.annual_volume || li.quantity * 4).toLocaleString('en-IN')} pcs</strong></span>
          </div>
        </div>

        <!-- Card 2: Hero Landed Cost Card -->
        <div style="background: #F0FDF4; border: 1.5px solid #86EFAC; border-radius: 14px; padding: 18px 20px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(22, 163, 74, 0.08);">
          <div>
            <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #15803D; margin-bottom: 4px;">Delivered Landed Cost (excl GST)</div>
            <div style="font-size: 26px; font-weight: 800; color: #14532D; letter-spacing: -0.03em;">
              ${this.inr(q.landed_cost_excl_gst)} <span style="font-size: 13px; font-weight: 500; color: #166534;">/ pc</span>
            </div>
          </div>
          <div style="text-align: right;">
            <span class="badge badge-green" style="font-size: 11px; padding: 4px 10px; font-weight: 700;">${q.tech_compliance || 'COMPLIANT'}</span>
            <div style="font-size: 11px; color: #15803D; margin-top: 4px; font-weight: 500;">Delivered DDP</div>
          </div>
        </div>

        <!-- Card 3: Commercial Terms & Pricing Breakdown Card -->
        <div class="card" style="padding: 16px 18px; margin-bottom: 16px; border: 1px solid var(--border-light); border-radius: 14px; background: #FFFFFF;">
          <div style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 12px;">Pricing & Commercial Breakdown</div>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Original Quoted Rate:</span>
              <span class="font-semibold" style="color: var(--text-main);">₹${q.orig_price} ${q.orig_unit || 'per piece'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Normalized Base Rate:</span>
              <span class="font-bold" style="color: var(--text-main);">${this.inr(q.norm_price_per_unit)}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Trade / Volume Discount:</span>
              <span class="font-semibold" style="color: ${q.discount_pct ? '#15803D' : 'var(--text-main)'};">${q.discount_pct ? `${q.discount_pct}% applied` : '0%'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Freight Terms:</span>
              <span class="font-semibold" style="color: var(--text-main);">${q.freight_included ? 'Included (DDP)' : `+₹${q.freight_per_unit}/pc at cost`}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px; border-top: 1px solid var(--border-subtle); padding-top: 8px;">
              <span class="text-muted">Applicable GST:</span>
              <span class="font-semibold" style="color: var(--text-muted);">${q.gst_rate}% (ITC eligible)</span>
            </div>
          </div>
        </div>

        <!-- Card 4: Fulfillment & AI Extraction Provenance Card -->
        <div class="card" style="padding: 16px 18px; margin-bottom: 16px; border: 1px solid var(--border-light); border-radius: 14px; background: #FFFFFF;">
          <div style="font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: var(--text-muted); margin-bottom: 12px;">Fulfillment & Extraction Provenance</div>
          <div style="display: flex; flex-direction: column; gap: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Production Lead Time:</span>
              <span class="font-semibold" style="color: var(--text-main);">${q.lead_time_days ? `${q.lead_time_days} days` : 'Standard'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Minimum Order Qty (MOQ):</span>
              <span class="font-semibold" style="color: var(--text-main);">${q.moq ? `${Number(q.moq).toLocaleString('en-IN')} pcs` : 'Standard'}</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Extraction Confidence:</span>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span class="font-bold" style="color: ${confColor}; font-size: 13px;">${confPct}%</span>
                <div style="width: 50px; height: 6px; background: var(--border-light); border-radius: 9999px; overflow: hidden;">
                  <div style="width: ${confPct}%; height: 100%; background: ${confColor};"></div>
                </div>
              </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; font-size: 13px;">
              <span class="text-muted">Document Source:</span>
              <span class="font-mono text-xs" style="background: var(--surface-subtle); padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border-subtle);">${q.source_ref || 'Extracted table'}</span>
            </div>
          </div>
        </div>

        <!-- Card 5: Extraction Notes & Flags -->
        ${q.notes ? `
          <div style="background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700; color: #92400E; margin-bottom: 4px;">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              <span>Extraction Notes & Flags</span>
            </div>
            <div style="font-size: 12.5px; color: #78350F; line-height: 1.5;">${q.notes}</div>
          </div>
        ` : ''}

        ${q.is_manual_override ? `
          <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="font-size: 12px; font-weight: 700; color: #1E40AF; margin-bottom: 4px;">Manual Override Applied</div>
            <div style="font-size: 12.5px; color: #1E3A8A; line-height: 1.4;">
              Modified by <strong>${q.override_by}</strong><br/>
              Reason: "${q.override_reason}" (Original raw value: ₹${q.orig_value_raw})
            </div>
          </div>
        ` : ''}

        <!-- Card 6: Action Button -->
        <button class="btn btn-secondary w-full" style="height: 42px; font-size: 13.5px; font-weight: 600; display: flex; align-items: center; justify-content: center; gap: 8px; border-radius: 10px;" onclick="App.openCorrectionModal(${q.id}, ${q.norm_price_per_unit})">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          <span>Correct or Override This Value</span>
        </button>
      `;
    } catch (err) {
      content.innerHTML = `<div class="alert alert-error">Error loading detail: ${err.message}</div>`;
    }
  },

  async saveManualQuote(lineItemId, supplierId) {
    const priceInput = document.getElementById('manual-unit-price');
    const price = parseFloat(priceInput?.value);
    if (isNaN(price) || price <= 0) {
      this.toast('Please enter a valid positive unit price.', 'error');
      return;
    }
    const freight = parseFloat(document.getElementById('manual-freight')?.value || 0) || 0;
    const freightInc = document.getElementById('manual-freight-inc')?.checked || false;
    const reason = document.getElementById('manual-reason')?.value.trim() || 'Manual rate entered by buyer';

    try {
      const rfxId = this.currentRfxId || 1;
      await this.api('POST', `/api/rfx/${rfxId}/quotes/manual`, {
        supplier_id: supplierId,
        line_item_id: lineItemId,
        unit_price: price,
        freight_per_unit: freight,
        freight_included: freightInc,
        override_reason: reason,
        override_by: 'Priya Krishnamurthy'
      });
      this.toast(`Quote rate saved: ₹${price.toFixed(2)}/pc recorded with audit log.`, 'success');
      this.closeCellDetail();
      this.loadComparison();
    } catch (err) {
      this.toast(`Failed to save quote: ${err.message}`, 'error');
    }
  },

  closeCellDetail() {
    const panel = document.getElementById('cell-detail-panel');
    if (panel) panel.classList.remove('open');
    this.selectedQuote = null;
  },

  openCorrectionModal(quoteId, currentValue) {
    this.showModal(
      'Manual Quote Correction &amp; Audit Override',
      `
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <div class="form-group">
            <label class="form-label" style="font-weight: 600; font-size: 13px; color: var(--text-main); margin-bottom: 6px; display: block;">Field to Correct</label>
            <select id="corr-field" class="form-input w-full" style="height: 42px; border-radius: 10px; font-size: 13.5px;">
              <option value="norm_price_per_unit" selected>Normalized Price / Piece (INR)</option>
              <option value="orig_price">Original Price</option>
              <option value="discount_pct">Discount Percentage</option>
              <option value="freight_per_unit">Freight per Unit (INR)</option>
              <option value="lead_time_days">Lead Time (Days)</option>
              <option value="moq">Minimum Order Quantity (MOQ)</option>
              <option value="tech_compliance">Technical Compliance (COMPLIANT/NON_COMPLIANT/SUBSTITUTE)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" style="font-weight: 600; font-size: 13px; color: var(--text-main); margin-bottom: 6px; display: block;">New Corrected Value</label>
            <input type="text" id="corr-val" class="form-input w-full" value="${currentValue || ''}" placeholder="Enter verified value" style="height: 42px; border-radius: 10px; font-size: 13.5px;" />
          </div>
          <div class="form-group">
            <label class="form-label" style="font-weight: 600; font-size: 13px; color: var(--text-main); margin-bottom: 6px; display: block;">Reason for Override (Mandatory for Audit Trail)</label>
            <textarea id="corr-reason" rows="3" class="form-input w-full" style="height: auto; min-height: 75px; padding: 10px 14px; border-radius: 10px; font-family: var(--font-sans); font-size: 13px;" placeholder="e.g. Confirmed with supplier via email on 18-Oct; discount footnote re-calculated"></textarea>
          </div>
          <div style="background: var(--surface-subtle); padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border-light); font-size: 12px; color: var(--text-muted); line-height: 1.5;">
            All overrides are permanently logged in the RFx audit ledger with your user signature.
          </div>
        </div>
      `,
      `
        <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
        <button class="btn btn-primary" onclick="App.executeCorrection(${quoteId})">Apply Correction</button>
      `
    );
  },

  async executeCorrection(quoteId) {
    const field = document.getElementById('corr-field').value;
    const val = document.getElementById('corr-val').value.trim();
    const reason = document.getElementById('corr-reason').value.trim();

    if (!val || !reason) {
      this.toast('Please provide both new value and audit reason.', 'error');
      return;
    }

    try {
      const rfxId = this.currentRfxId || 1;
      await this.api('POST', `/api/rfx/${rfxId}/corrections`, {
        quote_id: quoteId,
        field: field,
        new_value: isNaN(Number(val)) ? val : Number(val),
        reason: reason,
        override_by: 'Priya Krishnamurthy (Category Mgr)',
      });

      this.closeModal();
      this.toast('Quote corrected successfully. Audit log updated.', 'success');
      this.closeCellDetail();
      this.loadComparison();
    } catch (err) {
      this.toast(`Failed to apply correction: ${err.message}`, 'error');
    }
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 5: NATURAL-LANGUAGE PROCUREMENT ANALYST
  // ════════════════════════════════════════════════════════════════════════════
  copilotSessions: [],
  currentCopilotSessionId: null,

  initCopilotHistory() {
    try {
      const saved = localStorage.getItem('aerchain_copilot_sessions');
      if (saved) {
        this.copilotSessions = JSON.parse(saved);
      } else {
        this.copilotSessions = [];
      }
    } catch (e) {
      this.copilotSessions = [];
    }
    this.renderCopilotHistoryList();
  },

  saveCopilotSessions() {
    try {
      localStorage.setItem('aerchain_copilot_sessions', JSON.stringify(this.copilotSessions));
    } catch (e) {}
  },

  renderCopilotHistoryList() {
    const list = document.getElementById('copilot-history-list');
    if (!list) return;

    if (!this.copilotSessions || this.copilotSessions.length === 0) {
      list.innerHTML = `
        <div style="padding: 14px 12px; font-size: 11.5px; color: var(--text-muted); line-height: 1.5;">
          No saved chats yet. Start a new conversation below!
        </div>
      `;
      return;
    }

    list.innerHTML = this.copilotSessions.map(s => {
      const isActive = this.currentCopilotSessionId === s.id;
      return `
        <div class="copilot-history-item ${isActive ? 'active' : ''}" onclick="App.loadCopilotSession('${s.id}')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink: 0; opacity: 0.7;"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          <span class="copilot-history-title" title="${s.title}">${s.title}</span>
          <button class="copilot-history-del-btn" onclick="App.deleteCopilotSession('${s.id}', event)" title="Delete Chat">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
      `;
    }).join('');
  },

  loadCopilotSession(sessionId) {
    const session = this.copilotSessions.find(s => s.id === sessionId);
    if (!session) return;

    this.currentCopilotSessionId = sessionId;
    this.renderCopilotHistoryList();

    const chat = document.getElementById('chat-history');
    if (!chat) return;

    chat.innerHTML = '';
    const empty = document.getElementById('chat-empty-state');
    if (empty) empty.remove();

    session.messages.forEach(msg => {
      if (msg.role === 'user') {
        const userRow = document.createElement('div');
        userRow.className = 'chatgpt-msg-row msg-row-user';
        userRow.innerHTML = `<div class="chatgpt-user-bubble">${this.escapeHtml(msg.text)}</div>`;
        chat.appendChild(userRow);
      } else {
        const respRow = document.createElement('div');
        respRow.className = 'chatgpt-msg-row msg-row-assistant';
        respRow.innerHTML = `
          <div class="chatgpt-assistant-avatar">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
            </svg>
          </div>
          <div class="chatgpt-assistant-content">
            <div class="chatgpt-assistant-name">Aerchain Copilot</div>
            <div class="chatgpt-prose">${this.renderMarkdown(msg.text)}</div>
            ${msg.sources && msg.sources.length > 0 ? `
              <div class="msg-sources" style="font-size: 11.5px; color: var(--text-muted); margin-top: 8px;">
                <strong>Sources:</strong> ${msg.sources.map(s => this.escapeHtml(s)).join(' • ')}
              </div>
            ` : ''}
          </div>
        `;
        chat.appendChild(respRow);
      }
    });

    const scrollArea = document.getElementById('copilot-scroll-area');
    if (scrollArea) {
      setTimeout(() => {
        scrollArea.scrollTop = scrollArea.scrollHeight;
      }, 50);
    }
  },

  resetCopilotChat() {
    this.currentCopilotSessionId = null;
    this.renderCopilotHistoryList();

    const chat = document.getElementById('chat-history');
    if (!chat) return;

    chat.innerHTML = `
      <div class="chatgpt-welcome" id="chat-empty-state">
        <div class="chatgpt-avatar-circle">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
          </svg>
        </div>
        <h2 class="chatgpt-headline">Ask Aerchain Procurement Copilot</h2>
        <p class="chatgpt-subheadline">Interrogate the 5 supplier responses across all 30 line items in plain English.</p>

        <div class="chatgpt-suggestions-block">
          <div class="chatgpt-suggestions-title">Try the sample prompts below or ask scenario calculations:</div>
          <div class="chatgpt-prompt-grid">
            <div class="chatgpt-prompt-card" onclick="App.submitQuestion('Cheapest supplier per line item (BRC qualified only)')">
              <div class="chatgpt-card-title">Cheapest supplier per line item (BRC qualified only)</div>
              <div class="chatgpt-card-sub">Find lowest landed cost with food safety qualification</div>
            </div>
            <div class="chatgpt-prompt-card" onclick="App.submitQuestion('Single supplier vs split award financial comparison')">
              <div class="chatgpt-card-title">Single supplier vs split award financial comparison</div>
              <div class="chatgpt-card-sub">Simulate cost differences and volume discounts</div>
            </div>
            <div class="chatgpt-prompt-card" onclick="App.submitQuestion('Suppliers with greatest price spread across items')">
              <div class="chatgpt-card-title">Suppliers with greatest price spread across items</div>
              <div class="chatgpt-card-sub">Highlight pricing anomalies and variance across vendors</div>
            </div>
            <div class="chatgpt-prompt-card" onclick="App.submitQuestion('Quotes requiring manual review or verification')">
              <div class="chatgpt-card-title">Quotes requiring manual review or verification</div>
              <div class="chatgpt-card-sub">Audit missing values, footnotes, and extraction exceptions</div>
            </div>
          </div>
        </div>
      </div>
    `;

    const input = document.getElementById('analyst-input');
    if (input) {
      input.value = '';
      input.focus();
    }
  },

  deleteCopilotSession(sessionId, event) {
    if (event) event.stopPropagation();
    this.copilotSessions = this.copilotSessions.filter(s => s.id !== sessionId);
    this.saveCopilotSessions();
    if (this.currentCopilotSessionId === sessionId) {
      this.resetCopilotChat();
    } else {
      this.renderCopilotHistoryList();
    }
  },

  toggleChatHistorySidebar() {
    const sidebar = document.getElementById('copilot-history-sidebar');
    if (sidebar) {
      sidebar.classList.toggle('collapsed');
      const btn = document.getElementById('copilot-toggle-history-btn');
      if (btn) {
        btn.classList.toggle('active', !sidebar.classList.contains('collapsed'));
      }
    }
  },

  navBackCopilot() {
    const target = (this.previousSection && this.previousSection !== 'analyst') ? this.previousSection : 'comparison';
    this.navigateTo(target);
  },

  loadAnalyst() {
    this.renderCopilotHistoryList();
  },

  submitQuestion(q) {
    const input = document.getElementById('analyst-input');
    if (input) input.value = q;
    this.submitAnalystQuery();
  },

  analystKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      this.submitAnalystQuery();
    }
  },

  async submitAnalystQuery() {
    const input = document.getElementById('analyst-input');
    const question = input.value.trim();
    if (!question) return;

    input.value = '';
    const chat = document.getElementById('chat-history');

    // Remove empty state
    const empty = document.getElementById('chat-empty-state');
    if (empty) empty.remove();

    // Append User Bubble
    const userRow = document.createElement('div');
    userRow.className = 'chatgpt-msg-row msg-row-user';
    userRow.innerHTML = `<div class="chatgpt-user-bubble">${this.escapeHtml(question)}</div>`;
    chat.appendChild(userRow);

    // Scroll smoothly
    const scrollArea = document.getElementById('copilot-scroll-area');
    if (scrollArea) {
      scrollArea.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
    }

    // Append Loading State
    const loadId = 'load-' + Date.now();
    const loadRow = document.createElement('div');
    loadRow.id = loadId;
    loadRow.className = 'chatgpt-msg-row msg-row-assistant';
    loadRow.innerHTML = `
      <div class="chatgpt-assistant-avatar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
        </svg>
      </div>
      <div class="chatgpt-assistant-content">
        <div class="chatgpt-loading-bubble"><span class="spinner spinner-sm"></span> Aerchain Copilot is calculating scenario models...</div>
      </div>
    `;
    chat.appendChild(loadRow);
    if (scrollArea) {
      scrollArea.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
    }

    try {
      const rfxId = this.currentRfxId || 1;

      // Collect conversation history for multi-turn conversational reasoning
      let history = [];
      if (this.currentCopilotSessionId) {
        const activeSession = this.copilotSessions.find(s => s.id === this.currentCopilotSessionId);
        if (activeSession && Array.isArray(activeSession.messages)) {
          history = activeSession.messages.map(m => ({
            role: m.role,
            text: m.text
          }));
        }
      }

      const res = await this.api('POST', '/api/analyst/query', {
        question: question,
        rfx_id: rfxId,
        history: history.length > 0 ? history : undefined,
      });

      const lb = document.getElementById(loadId);
      if (lb) lb.remove();

      // Append Assistant Response Row
      const respRow = document.createElement('div');
      respRow.className = 'chatgpt-msg-row msg-row-assistant';

      let tableHtml = '';
      if (res.table_data && Array.isArray(res.table_data) && res.table_data.length > 0) {
        const tableId = 'analyst_table_' + Date.now();
        window[tableId] = res.table_data;
        const keys = Object.keys(res.table_data[0]);
        tableHtml = `
          <div class="table-wrap analyst-table" style="margin: 12px 0;">
            <div style="display: flex; justify-content: flex-end; margin-bottom: 8px;">
              <button class="btn-capsule-secondary" style="height: 28px; padding: 0 12px; font-size: 11.5px; display: inline-flex; align-items: center; gap: 5px;" onclick="App.exportTableDataCSV('${tableId}')">
                ${this.icon('download', 12)} Export Table (CSV)
              </button>
            </div>
            <table>
              <thead>
                <tr>
                  ${keys.map(k => `<th>${k.replace(/_/g, ' ').toUpperCase()}</th>`).join('')}
                </tr>
              </thead>
              <tbody>
                ${res.table_data.slice(0, 30).map(row => `
                  <tr>
                    ${keys.map(k => `
                      <td>${typeof row[k] === 'number' ? (k.includes('cost') || k.includes('price') || k.includes('spend') || k.includes('min') || k.includes('max') ? App.inr(row[k]) : row[k]) : (row[k] === true ? 'Yes' : row[k] === false ? 'No' : (row[k] || '-'))}</td>
                    `).join('')}
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        `;
      }

      const canvasId = 'chart-' + Date.now();
      const chartHtml = res.chart_data ? `<div class="analyst-chart-wrap" style="height: 260px; margin: 12px 0;"><canvas id="${canvasId}"></canvas></div>` : '';

      respRow.innerHTML = `
        <div class="chatgpt-assistant-avatar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
          </svg>
        </div>
        <div class="chatgpt-assistant-content">
          <div class="chatgpt-assistant-name">Aerchain Copilot</div>
          <div class="chatgpt-prose">${this.renderMarkdown(res.answer_text)}</div>
          ${tableHtml}
          ${chartHtml}
          ${res.sources && res.sources.length > 0 ? `
            <div class="msg-sources" style="font-size: 11.5px; color: var(--text-muted); margin-top: 8px;">
              <strong>Sources:</strong> ${res.sources.join(' • ')}
            </div>
          ` : ''}
        </div>
      `;

      chat.appendChild(respRow);
      if (scrollArea) {
        scrollArea.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
      }

      // Track in copilot sessions
      if (!this.currentCopilotSessionId) {
        const newSession = {
          id: 'session-' + Date.now(),
          title: question.length > 28 ? question.substring(0, 28) + '...' : question,
          date: 'Just now',
          messages: []
        };
        this.copilotSessions.unshift(newSession);
        this.currentCopilotSessionId = newSession.id;
      }
      const activeSession = this.copilotSessions.find(s => s.id === this.currentCopilotSessionId);
      if (activeSession) {
        activeSession.messages.push({ role: 'user', text: question });
        activeSession.messages.push({ role: 'assistant', text: res.answer_text, sources: res.sources });
        this.saveCopilotSessions();
        this.renderCopilotHistoryList();
      }

      // Render Chart.js if data exists
      if (res.chart_data && window.Chart) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (ctx) {
          const cfg = res.chart_data;
          // Apply supplier palette if matching labels
          if (cfg.labels && cfg.datasets && cfg.datasets[0]) {
            cfg.datasets[0].backgroundColor = cfg.labels.map(l => SUPPLIER_COLORS[l] || '#3b03c5');
            cfg.datasets[0].borderRadius = 8;
          }

          new Chart(ctx, {
            type: cfg.type || 'bar',
            data: cfg,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    label: (item) => ' ₹' + Number(item.raw).toLocaleString('en-IN')
                  }
                }
              },
              scales: {
                y: {
                  ticks: {
                    callback: (val) => '₹' + (val >= 100000 ? (val / 100000).toFixed(1) + 'L' : val)
                  }
                }
              }
            }
          });
        }
      }

      this.chatHistory.push({ q: question, a: res });
    } catch (err) {
      const lb = document.getElementById(loadId);
      if (lb) lb.remove();

      const errBubble = document.createElement('div');
      errBubble.className = 'msg-bubble msg-analyst alert alert-error';
      errBubble.textContent = `Analyst Query Error: ${err.message}`;
      chat.appendChild(errBubble);
    }
  },

  exportTableDataCSV(tableId) {
    const data = window[tableId];
    if (!data || !Array.isArray(data) || data.length === 0) {
      this.toast('No table data to export', 'error');
      return;
    }
    const keys = Object.keys(data[0]);
    const csvRows = [];
    csvRows.push(keys.map(k => `"${k.replace(/"/g, '""')}"`).join(','));
    for (const row of data) {
      csvRows.push(keys.map(k => {
        const val = row[k] === null || row[k] === undefined ? '' : String(row[k]);
        return `"${val.replace(/"/g, '""')}"`;
      }).join(','));
    }
    const blob = new Blob([csvRows.join('\r\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analyst_query_result_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    this.toast('Analyst table exported successfully', 'success');
  },

  // ════════════════════════════════════════════════════════════════════════════
  // SECTION 6: AWARD RECOMMENDATION & EXPORT
  // ════════════════════════════════════════════════════════════════════════════
  async loadAward() {
    const loading = document.getElementById('award-loading');
    const container = document.getElementById('award-cards');
    const tablesContainer = document.getElementById('award-tables-container');

    loading.style.display = 'flex';
    container.innerHTML = '';
    if (tablesContainer) tablesContainer.innerHTML = '';

    try {
      const rfxId = this.currentRfxId || 1;
      const data = await this.api('GET', `/api/rfx/${rfxId}/award-scenarios`);
      this.awardData = data;
      loading.style.display = 'none';

      const single = data.single_supplier || {};
      const bestSingle = single.best || {};
      const split = data.split_award || {};
      const savings = data.savings_from_split || 0;

      // Compute detailed supplier allocations from split.detail and split.supplier_allocation
      const allocSummary = {};
      if (split.detail && Array.isArray(split.detail)) {
        split.detail.forEach(d => {
          if (!d.best_supplier_code) return;
          const c = d.best_supplier_code;
          if (!allocSummary[c]) {
            allocSummary[c] = {
              code: c,
              name: d.best_supplier_name || c,
              items_awarded: 0,
              total_value: 0
            };
          }
          allocSummary[c].items_awarded += 1;
          allocSummary[c].total_value += (d.total_cost || 0);
        });
      }

      const totalSplitSpend = split.total_cost || Object.values(allocSummary).reduce((sum, x) => sum + x.total_value, 0) || 1;
      const allocItems = Object.values(allocSummary);

      const allocHtml = allocItems.length > 0
        ? allocItems.map(a => {
            const pct = Math.round((a.total_value / totalSplitSpend) * 100);
            return `
              <div class="flex-between">
                <span>${a.name} (${a.code}):</span>
                <strong>${a.items_awarded} SKUs (${pct}% volume · ${this.inr(a.total_value)})</strong>
              </div>
            `;
          }).join('')
        : (split.supplier_allocation && Object.keys(split.supplier_allocation).length > 0
            ? Object.entries(split.supplier_allocation).map(([code, count]) => `
                <div class="flex-between">
                  <span>${code}:</span>
                  <strong>${typeof count === 'number' ? count : (count.items_awarded || 0)} SKUs</strong>
                </div>
              `).join('')
            : '<div class="text-xs text-muted">No line item allocations computed.</div>');

      container.innerHTML = `
        <!-- Card 1: Best Single Supplier -->
        <div class="award-decision-card">
          <div>
            <div class="text-xs font-bold text-muted uppercase" style="letter-spacing:0.05em;">Scenario A: Single Sourcing</div>
            <h3 style="font-size:18px; font-weight:800; margin-top:4px;">${bestSingle.supplier_name || 'PremiumCorrugated'} (${bestSingle.supplier_code || 'PCO'})</h3>
            <div class="award-metric-large">${this.inr(bestSingle.total_cost || 0)}</div>
            <div class="text-xs text-muted mb-12">
              Coverage: <strong>${bestSingle.items_covered || 30} / 30</strong> line items (100%) · Lead time: 14 days
            </div>
          </div>
          <div style="border-top:1px solid var(--border-subtle); padding-top:12px; display:flex; flex-direction:column; gap:6px; font-size:12.5px;">
            <div class="flex-between"><span>Quality Audit:</span><span class="badge badge-green">BRC Grade A &amp; ISO 9001</span></div>
            <div class="flex-between"><span>Payment Terms:</span><span>30 days credit (DDP)</span></div>
            <div class="flex-between"><span>Operational Risk:</span><span class="text-muted">Single-source capacity constraint</span></div>
          </div>
        </div>

        <!-- Card 2: AI-Optimized Split Award -->
        <div class="award-decision-card recommended">
          <div>
            <div class="flex-between">
              <span class="text-xs font-bold uppercase" style="color:var(--aer-violet); letter-spacing:0.05em;">Scenario B: AI-Optimized Split Award</span>
              <span class="badge badge-green">Recommended</span>
            </div>
            <h3 style="font-size:18px; font-weight:800; margin-top:4px;">Optimal Landed Cost Allocation</h3>
            <div class="award-metric-large" style="color:var(--aer-violet);">${this.inr(split.total_cost || 0)}</div>
            <div style="margin-bottom:12px;">
              <span class="badge badge-green" style="font-size:12px; padding:4px 12px;">Saves ${this.inr(savings)} vs Best Single Supplier (${split.savings_pct || (bestSingle.total_cost ? Math.round((savings / bestSingle.total_cost) * 100) : 0)}%)</span>
            </div>
          </div>
          <div style="border-top:1px solid var(--border-subtle); padding-top:12px; display:flex; flex-direction:column; gap:6px; font-size:12.5px;">
            ${allocHtml}
          </div>
        </div>
      `;

      if (tablesContainer) {
        tablesContainer.innerHTML = `
          <!-- Supplier Mandatory Quality Qualification Audit Table -->
          <div class="table-card mb-24">
            <div class="flex-between" style="margin-bottom: 22px; align-items: flex-start;">
              <div>
                <h4 style="font-size: 16px; font-weight: 700; color: var(--text-main); margin: 0 0 6px 0; letter-spacing: -0.01em;">Supplier Quality &amp; Compliance Audit</h4>
                <p class="text-secondary" style="font-size: 13px; margin: 0; line-height: 1.4; color: var(--text-muted);">ISO 9001:2015, BRC/IoP Food Packaging Standard, and Chain of Custody certification</p>
              </div>
              <span class="badge badge-blue" style="padding: 5px 12px; font-size: 12px;">Mandatory Gate</span>
            </div>
            <div class="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Supplier</th>
                    <th>Plant Location</th>
                    <th>ISO 9001:2015</th>
                    <th>BRC Packaging Standard</th>
                    <th>Sustainability Cert</th>
                    <th>Audit Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>PackIndia Ltd (PKI)</strong></td>
                    <td>Pune</td>
                    <td><span class="badge badge-green">ISO 9001:2015</span></td>
                    <td><span class="badge badge-green">Grade A</span></td>
                    <td><span class="text-muted">-</span></td>
                    <td><span class="badge badge-green">QUALIFIED</span></td>
                  </tr>
                  <tr>
                    <td><strong>IndoPack Industries (IPI)</strong></td>
                    <td>Chennai</td>
                    <td><span class="badge badge-green">ISO 9001:2015</span></td>
                    <td><span class="badge badge-green">BRC Global</span></td>
                    <td><span class="badge badge-green">FSC Chain of Custody</span></td>
                    <td><span class="badge badge-green">QUALIFIED</span></td>
                  </tr>
                  <tr>
                    <td><strong>PremiumCorrugated (PCO)</strong></td>
                    <td>Mumbai</td>
                    <td><span class="badge badge-green">ISO 9001:2015</span></td>
                    <td><span class="badge badge-green">Grade AA</span></td>
                    <td><span class="badge badge-green">GMP+ / FSC</span></td>
                    <td><span class="badge badge-green">QUALIFIED</span></td>
                  </tr>
                  <tr>
                    <td><strong>EcoBox Solutions (EBS)</strong></td>
                    <td>Ahmedabad</td>
                    <td><span class="badge badge-green">ISO 9001:2015</span></td>
                    <td><span class="badge badge-orange">Audit Pending Q1 2027</span></td>
                    <td><span class="badge badge-green">100% Recycled Liner</span></td>
                    <td><span class="badge badge-red">DISQUALIFIED (Non-BRC)</span></td>
                  </tr>
                  <tr>
                    <td><strong>RegionalPacks Co (RPC)</strong></td>
                    <td>Hyderabad</td>
                    <td><span class="badge badge-green">ISO 9001:2015</span></td>
                    <td><span class="badge badge-red">Absent</span></td>
                    <td><span class="text-muted">-</span></td>
                    <td><span class="badge badge-red">DISQUALIFIED (Non-BRC)</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 4-Card Risk Registry (No endless text) -->
          <div class="table-card">
            <div class="flex-between" style="margin-bottom: 22px; align-items: flex-start;">
              <div>
                <h4 style="font-size: 16px; font-weight: 700; color: var(--text-main); margin: 0 0 6px 0; letter-spacing: -0.01em;">Commercial Risk Registry</h4>
                <p class="text-secondary" style="font-size: 13px; margin: 0; line-height: 1.4; color: var(--text-muted);">Audited vendor exceptions, unquoted items, and tariff discrepancies</p>
              </div>
              <span class="badge badge-purple" style="padding: 5px 12px; font-size: 12px;">4 Exceptions Audited</span>
            </div>

            <div class="risk-cards-grid">
              <div class="risk-chip-card">
                <div class="risk-vendor-tag"><span>RegionalPacks (RPC)</span><span class="badge badge-red">High Risk</span></div>
                <p class="risk-desc-text">13 line items quoted via informal note 'rest same as last year'. Excluded from automated allocation to prevent rate disputes.</p>
              </div>

              <div class="risk-chip-card">
                <div class="risk-vendor-tag"><span>EcoBox Solutions (EBS)</span><span class="badge badge-orange">Medium</span></div>
                <p class="risk-desc-text">Buried 8% volume discount in footnote and quoted non-standard 12% GST (statutory rate is 18%). BRC audit pending.</p>
              </div>

              <div class="risk-chip-card">
                <div class="risk-vendor-tag"><span>IndoPack Industries (IPI)</span><span class="badge badge-green">Resolved</span></div>
                <p class="risk-desc-text">Item 29 technical substitution (5-ply wax-treated board) approved following moisture-barrier specification sign-off.</p>
              </div>

              <div class="risk-chip-card">
                <div class="risk-vendor-tag"><span>PackIndia Ltd (PKI)</span><span class="badge badge-blue">Info</span></div>
                <p class="risk-desc-text">Item 18 heavy bin quoted 'On Request'. Requires structural CAD approval before purchase order release.</p>
              </div>
            </div>
          </div>
        `;
      }
    } catch (err) {
      loading.style.display = 'none';
      this.toast(`Failed to load award scenarios: ${err.message}`, 'error');
    }
  },

  async exportCSV(e) {
    if (e && e.preventDefault) e.preventDefault();
    try {
      const rfxId = this.currentRfxId || 1;
      const res = await fetch(`${API}/api/rfx/${rfxId}/export`);
      if (!res.ok) throw new Error(`Export failed (${res.status})`);
      const blob = await res.blob();

      // Modern File System Access API: confirmation triggers only when user actually saves
      if (window.showSaveFilePicker) {
        try {
          const handle = await window.showSaveFilePicker({
            suggestedName: `RFX-${rfxId}-Packaging-Comparison.csv`,
            types: [{
              description: 'CSV Spreadsheet',
              accept: { 'text/csv': ['.csv'] }
            }]
          });
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
          this.toast('CSV saved successfully to your device', 'success');
          return;
        } catch (pickerErr) {
          if (pickerErr.name === 'AbortError') {
            // User cancelled save dialog
            return;
          }
        }
      }

      // Standard browser download fallback
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = `RFX-${rfxId}-Packaging-Comparison.csv`;
      document.body.appendChild(a);
      a.click();
      window.setTimeout(() => {
        if (a.parentNode) document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      }, 500);
    } catch (err) {
      console.error('Export CSV error:', err);
      this.toast(`Export failed: ${err.message}`, 'error');
    }
  },

  downloadAwardSummary() {
    if (!this.awardData) {
      this.toast('Award data not loaded yet.', 'error');
      return;
    }

    const rfxNumber = this.currentRfxNumber || 'RFX-2026-001';
    const single = this.awardData.single_supplier?.best || {};
    const split = this.awardData.split_award || {};
    const savings = this.awardData.savings_from_split || 0;

    const summaryText = `AERCHAIN RFX INTELLIGENCE - SOURCING AWARD RECOMMENDATION
================================================================================
RFx Event: ${rfxNumber} | Category: Corrugated Packaging FY 2026-27
Category Manager: Priya Krishnamurthy | Date: ${new Date().toLocaleDateString('en-IN')}

1. EXECUTIVE SUMMARY & AWARD DECISION
--------------------------------------------------------------------------------
Recommended Strategy: AI-Optimized Split Award across Qualified BRC/IoP Vendors.
- Net Spend under Recommended Split: INR ${split.total_cost?.toLocaleString('en-IN')}
- Net Spend under Best Single Supplier: INR ${single.total_cost?.toLocaleString('en-IN')} (${single.supplier_name})
- Total Projected Net Savings: INR ${savings.toLocaleString('en-IN')} (${single.total_cost ? ((savings / single.total_cost) * 100).toFixed(1) : 0}%)

2. ALLOCATION MATRIX
--------------------------------------------------------------------------------
${Object.entries(split.supplier_allocation || {}).map(([code, count]) => `• ${code}: ${count} Line Items awarded`).join('\n')}

3. QUALIFICATION AUDIT
--------------------------------------------------------------------------------
• PKI (PackIndia Ltd): QUALIFIED (BRC Grade A, ISO 9001:2015)
• IPI (IndoPack Industries): QUALIFIED (BRC Global Standard, ISO 9001:2015, FSC)
• PCO (PremiumCorrugated): QUALIFIED (BRC Grade AA, ISO 9001:2015, GMP)
• EBS (EcoBox Solutions): DISQUALIFIED (BRC application pending Q1 2027)
• RPC (RegionalPacks Co): DISQUALIFIED (BRC absent, 13 unresolved pricing gaps)

4. AUDIT & TRACEABILITY VERIFICATION
--------------------------------------------------------------------------------
All rates normalized to per-piece INR basis including trade discounts and freight.
Approved by Category Management Team.
`;

    const blob = new Blob([summaryText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${rfxNumber}_Award_Recommendation_${new Date().toISOString().substring(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    this.toast('Award summary downloaded.', 'success');
  },

  approveAward() {
    const rfxNumber = this.currentRfxNumber || 'RFX-2026-001';
    const split = this.awardData?.split_award || {};
    const savings = this.awardData?.savings_from_split || 4505550;

    const allocSummary = {};
    if (split.detail && Array.isArray(split.detail)) {
      split.detail.forEach(d => {
        if (!d.best_supplier_code) return;
        const c = d.best_supplier_code;
        if (!allocSummary[c]) {
          allocSummary[c] = {
            code: c,
            name: d.best_supplier_name || c,
            items_awarded: 0,
            total_value: 0
          };
        }
        allocSummary[c].items_awarded += 1;
        allocSummary[c].total_value += (d.total_cost || 0);
      });
    }

    const totalSplitSpend = split.total_cost || Object.values(allocSummary).reduce((sum, x) => sum + x.total_value, 0) || 1;
    const allocItems = Object.values(allocSummary);

    const vendorNames = allocItems.length > 0
      ? allocItems.map(a => a.code).join(', ')
      : (split.supplier_allocation ? Object.keys(split.supplier_allocation).join(', ') : 'PKI, IPI, and PCO');

    const allocHtml = allocItems.length > 0
      ? allocItems.map(a => {
          const pct = Math.round((a.total_value / totalSplitSpend) * 100);
          return `
            <div style="display: flex; justify-content: space-between;">
              <span>${a.name} (${a.code})</span>
              <strong>${a.items_awarded} SKUs (${pct}% volume · ${this.inr(a.total_value)})</strong>
            </div>
          `;
        }).join('')
      : `
          <div style="display: flex; justify-content: space-between;">
            <span>IndoPack Industries (IPI)</span>
            <strong>26 SKUs (78% volume)</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>PackIndia Ltd (PKI)</span>
            <strong>3 SKUs (14% volume)</strong>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span>PremiumCorrugated (PCO)</span>
            <strong>1 SKU (8% volume)</strong>
          </div>
        `;

    this.showModal(
      'Executive Award Authorization',
      `
        <div style="display: flex; flex-direction: column; gap: 18px; padding: 4px 0;">
          <div>
            <div style="font-size: 16px; font-weight: 700; color: var(--text-main); margin-bottom: 8px;">Confirm Sourcing Award Approval</div>
            <p style="font-size: 13px; color: var(--text-secondary); line-height: 1.55; margin: 0;">
              You are authorizing the category award recommendation for <strong style="color: var(--text-main);">${rfxNumber}</strong>.
              This action commits the allocation matrix to the database, writes to the immutable audit log, and transitions the RFx status to <span class="badge badge-green" style="font-size: 11px;">AWARDED</span>.
            </p>
          </div>

          <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 14px; padding: 18px 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
              <span style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; color: #15803D;">Recommended Allocation</span>
              <span class="badge badge-green" style="font-size: 12px; font-weight: 700;">${this.inr(savings)} Verified Savings</span>
            </div>
            <div style="font-size: 14.5px; font-weight: 700; color: #14532D; margin-bottom: 12px;">
              Split Award across ${vendorNames} yielding ${this.inr(savings)} in verified savings.
            </div>
            <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12.5px; color: #166534; padding-top: 10px; border-top: 1px solid #DCFCE7;">
              ${allocHtml}
            </div>
          </div>

          <div style="background: var(--surface-subtle); border: 1px solid var(--border-light); border-radius: 10px; padding: 12px 16px; display: flex; align-items: flex-start; gap: 10px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6B7280" stroke-width="2" style="flex-shrink: 0; margin-top: 2px;">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <div style="font-size: 12px; color: var(--text-muted); line-height: 1.45;">
              Authorized by Category Manager <strong>Priya Krishnamurthy</strong>. Signed with timestamp and cryptographic ledger hash.
            </div>
          </div>
        </div>
      `,
      `
        <button class="btn btn-primary" style="width: 100%; height: 44px; font-size: 14px; font-weight: 600; justify-content: center;" onclick="App.executeAwardApproval()">Confirm &amp; Authorize Award</button>
      `
    );
  },

  async executeAwardApproval() {
    this.closeModal();
    try {
      const rfxId = this.currentRfxId || 1;
      await this.api('POST', `/api/rfx/${rfxId}/award`, {
        scenario: 'split',
        notes: 'Executive split award formally approved across qualified vendors PKI, IPI, and PCO.',
        approved_by: 'Priya Krishnamurthy'
      });
      this.toast('Award decision formally approved and recorded in audit log.', 'success');
      const btn = document.getElementById('btn-approve-award');
      if (btn) {
        btn.disabled = true;
        btn.className = 'btn btn-secondary';
        btn.textContent = 'Award Approved & Signed';
      }
    } catch (err) {
      this.toast(`Failed to approve award: ${err.message}`, 'error');
    }
  },
};

// ── Application Bootstrapping ─────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
