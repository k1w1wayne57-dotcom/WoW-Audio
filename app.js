// WoW Audio — World of Wayne. Vanilla JS only, no frameworks.

let DB = [];
let currentSort = "collector";
let currentType = "all";
let currentEra = "all";
let bestBuyOnly = false;
let thaiPriceOnly = false;
let searchTerm = "";

const RANK_ORDER = { "Top 10": 1, "Top 10-20": 2, "Top 20-30": 3, "Top 30-40": 4, "Top 40-50": 5, "Unranked": 6 };

const tableBody = document.getElementById("table-body");
const noResults = document.getElementById("no-results");

init();

async function init() {
  try {
    const res = await fetch("data/sansui.json");
    DB = await res.json();
  } catch (e) {
    tableBody.innerHTML = `<tr><td colspan="11" style="padding:24px;text-align:center;color:var(--text-secondary)">Could not load database (data/sansui.json). If opening this file directly, run a local server instead.</td></tr>`;
    return;
  }
  populateStats();
  bindControls();
  render();
}

function populateStats() {
  document.getElementById("stat-models").textContent = DB.length;
  const years = DB.map(d => d.year_start).filter(y => y !== null && y !== undefined);
  if (years.length) {
    document.getElementById("stat-years").textContent = `${Math.min(...years)}–${Math.max(...years)}`;
  }
  const priceCount = DB.filter(d => d.avg_price_usd_3mo !== null || (d.price_thb_listings && d.price_thb_listings.length)).length;
  document.getElementById("stat-prices").textContent = priceCount;
}

function bindControls() {
  document.querySelectorAll(".sort-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentSort = btn.dataset.sort;
      render();
    });
  });

  document.querySelectorAll(".filter-btn[data-type]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".filter-btn[data-type]").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentType = btn.dataset.type;
      render();
    });
  });

  document.querySelectorAll(".era-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".era-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      currentEra = btn.dataset.era;
      render();
    });
  });

  const bestBuyBtn = document.getElementById("best-buy-filter");
  bestBuyBtn.addEventListener("click", () => {
    bestBuyOnly = !bestBuyOnly;
    bestBuyBtn.classList.toggle("active", bestBuyOnly);
    render();
  });

  const thaiBtn = document.getElementById("thai-price-filter");
  thaiBtn.addEventListener("click", () => {
    thaiPriceOnly = !thaiPriceOnly;
    thaiBtn.classList.toggle("active", thaiPriceOnly);
    render();
  });

  document.getElementById("search-input").addEventListener("input", (e) => {
    searchTerm = e.target.value.trim().toLowerCase();
    render();
  });

  document.querySelectorAll("thead th[data-col]").forEach(th => {
    th.addEventListener("click", () => {
      const map = {
        rank: "collector", model: "newest", type: null, years: "newest",
        watts: "watts", weight: "heaviest", circuit: null, recap: "recap",
        bestbuy: "bestbuy", price: "price", links: null
      };
      const sortKey = map[th.dataset.col];
      if (!sortKey) return;
      document.querySelectorAll(".sort-btn").forEach(b => b.classList.remove("active"));
      const matchingBtn = document.querySelector(`.sort-btn[data-sort="${sortKey}"]`);
      if (matchingBtn) matchingBtn.classList.add("active");
      currentSort = sortKey;
      render();
    });
  });

  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("modal-overlay").addEventListener("click", (e) => {
    if (e.target.id === "modal-overlay") closeModal();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });
}

function matchesType(item, type) {
  if (type === "all") return true;
  if (type === "Quad") return item.type && item.type.toLowerCase().includes("quad") || (item.type && item.type.includes("4-ch"));
  return item.type === type;
}

function matchesEra(item, era) {
  if (era === "all") return true;
  if (era === "Tube Era") return item.series === "Tube Era";
  if (era === "Alpha Series") return item.series === "Alpha Series";
  if (era === "1960s") return item.year_start >= 1960 && item.year_start <= 1969;
  if (era === "1970s") return item.year_start >= 1970 && item.year_start <= 1979;
  if (era === "1980s") return item.year_start >= 1980 && item.year_start <= 1989;
  return true;
}

function matchesSearch(item, term) {
  if (!term) return true;
  const haystack = [
    item.jdm_model, item.int_model, item.type, item.series, item.notes,
    item.collector_info && item.collector_info.known_issues,
    item.collector_info && item.collector_info.collector_notes
  ].filter(Boolean).join(" ").toLowerCase();
  return haystack.includes(term);
}

function getFiltered() {
  return DB.filter(item =>
    matchesType(item, currentType) &&
    matchesEra(item, currentEra) &&
    matchesSearch(item, searchTerm) &&
    (!bestBuyOnly || (item.best_buy && item.best_buy.rating)) &&
    (!thaiPriceOnly || (item.price_thb_listings && item.price_thb_listings.length > 0))
  );
}

function sortItems(items) {
  const arr = [...items];
  switch (currentSort) {
    case "collector":
      arr.sort((a, b) => (RANK_ORDER[a.collector_ranking] || 6) - (RANK_ORDER[b.collector_ranking] || 6));
      break;
    case "newest":
      arr.sort((a, b) => (b.year_start || 0) - (a.year_start || 0));
      break;
    case "oldest":
      arr.sort((a, b) => (a.year_start || 9999) - (b.year_start || 9999));
      break;
    case "heaviest":
      arr.sort((a, b) => (b.weight_kg || 0) - (a.weight_kg || 0));
      break;
    case "watts":
      arr.sort((a, b) => (b.watts_per_channel || 0) - (a.watts_per_channel || 0));
      break;
    case "price":
      arr.sort((a, b) => (b.avg_price_usd_3mo || 0) - (a.avg_price_usd_3mo || 0));
      break;
    case "recap":
      arr.sort((a, b) => {
        const da = a.restorer_info && a.restorer_info.recap_difficulty;
        const db_ = b.restorer_info && b.restorer_info.recap_difficulty;
        return (da || 99) - (db_ || 99);
      });
      break;
    case "bestbuy":
      arr.sort((a, b) => ((b.best_buy && b.best_buy.rating) || 0) - ((a.best_buy && a.best_buy.rating) || 0));
      break;
  }
  return arr;
}

function rankClass(rank) {
  return "rank-" + (rank || "Unranked").replace(/\s+/g, "-");
}

function priceClass(price) {
  if (!price) return "price-low";
  if (price >= 1500) return "price-high";
  if (price >= 600) return "price-mid";
  return "price-low";
}

function formatPrice(item) {
  const parts = [];
  if (item.avg_price_usd_3mo) {
    const label = item.price_basis === "restored" ? " (rest.)" : "";
    parts.push(`$${item.avg_price_usd_3mo.toLocaleString()}${label}`);
  }
  if (item.price_thb_listings && item.price_thb_listings.length) {
    parts.push(item.price_thb_listings.map(v => `฿${v.toLocaleString()}`).join(" · "));
  }
  return parts.length ? parts.join(" / ") : "—";
}

function wrenchDisplay(level) {
  if (!level) return "—";
  const filled = "🔧".repeat(level);
  const empty = "⬜".repeat(5 - level);
  return `<span class="recap-wrench" title="${level}/5">${filled}${empty}</span>`;
}

function render() {
  const items = sortItems(getFiltered());
  tableBody.innerHTML = "";

  if (!items.length) {
    noResults.style.display = "block";
    return;
  }
  noResults.style.display = "none";

  const frag = document.createDocumentFragment();
  items.forEach(item => {
    const tr = document.createElement("tr");
    tr.addEventListener("click", () => openModal(item));

    const years = item.year_start
      ? `${item.year_start}${item.year_end ? "–" + item.year_end : ""}`
      : "—";

    tr.innerHTML = `
      <td><span class="rank-badge ${rankClass(item.collector_ranking)}">${item.collector_ranking || "Unranked"}</span></td>
      <td class="model-cell">
        <span class="model-jdm">${escapeHtml(item.jdm_model)}</span>
        ${item.int_model ? `<span class="model-int">${escapeHtml(item.int_model)}</span>` : ""}
      </td>
      <td>${escapeHtml(item.type || "—")}</td>
      <td>${years}</td>
      <td>${item.watts_per_channel ? item.watts_per_channel + "w" : "—"}</td>
      <td>${item.weight_kg ? item.weight_kg + " kg" : "—"}</td>
      <td>${escapeHtml(item.amp_circuit || "—")}</td>
      <td>${wrenchDisplay(item.restorer_info && item.restorer_info.recap_difficulty)}</td>
      <td>${item.best_buy && item.best_buy.rating ? `<span class="bestbuy-star">${"⭐".repeat(item.best_buy.rating)}</span>` : "—"}</td>
      <td class="price-cell ${priceClass(item.avg_price_usd_3mo)}">${formatPrice(item)}</td>
      <td class="links-cell">
        ${item.links && item.links.audio_database ? `<a class="link-icon" href="${item.links.audio_database}" target="_blank" rel="noopener" title="Audio Database" onclick="event.stopPropagation()">📄</a>` : ""}
      </td>
    `;
    frag.appendChild(tr);
  });
  tableBody.appendChild(frag);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  return String(str).replace(/[&<>"']/g, c => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[c]));
}

function openModal(item) {
  const modalContent = document.getElementById("modal-content");
  const years = item.year_start ? `${item.year_start}${item.year_end ? "–" + item.year_end : ""}` : "Year unknown";
  const recap = (item.restorer_info && item.restorer_info.recap_difficulty) || null;
  const failurePoints = (item.restorer_info && item.restorer_info.known_failure_points) || [];
  const commonFaults = (item.restorer_info && item.restorer_info.common_faults) || [];

  modalContent.innerHTML = `
    <div class="modal-header">
      <div>
        <h2>${escapeHtml(item.jdm_model)}${item.int_model ? " / " + escapeHtml(item.int_model) : ""}</h2>
        <p class="modal-sub">${escapeHtml(item.type || "")} | ${years}</p>
        <div class="modal-badges">
          <span class="rank-badge ${rankClass(item.collector_ranking)}">${item.collector_ranking || "Unranked"}</span>
          ${item.best_buy && item.best_buy.rating ? `<span class="bestbuy-star">⭐ Best Buy</span>` : ""}
        </div>
      </div>
    </div>

    <div class="modal-section">
      <h3>Specifications</h3>
      <div class="spec-grid">
        <div class="spec-row"><span class="spec-label">Watts</span><span class="spec-value">${item.watts_per_channel ? item.watts_per_channel + "w/ch" : "—"}</span></div>
        <div class="spec-row"><span class="spec-label">Weight</span><span class="spec-value">${item.weight_kg ? item.weight_kg + " kg" : "—"}</span></div>
        <div class="spec-row"><span class="spec-label">Freq Response</span><span class="spec-value">${escapeHtml(item.freq_response_hz || "—")}</span></div>
        <div class="spec-row"><span class="spec-label">THD</span><span class="spec-value">${item.thd_percent !== null && item.thd_percent !== undefined ? item.thd_percent + "%" : "—"}</span></div>
        <div class="spec-row"><span class="spec-label">PS Type</span><span class="spec-value">${escapeHtml(item.ps_type || "—")}</span></div>
        <div class="spec-row"><span class="spec-label">Circuit</span><span class="spec-value">${escapeHtml(item.amp_circuit || "—")}</span></div>
        <div class="spec-row"><span class="spec-label">Japan Price</span><span class="spec-value">${item.japan_price_kyen ? "¥" + (item.japan_price_kyen * 1000).toLocaleString() : "—"}</span></div>
        <div class="spec-row"><span class="spec-label">Int'l Model</span><span class="spec-value">${escapeHtml(item.int_model || "—")}</span></div>
      </div>
      ${item.special_features ? `<p class="info-line"><span class="il-label">Special Features:</span>${escapeHtml(item.special_features)}</p>` : ""}
    </div>

    <div class="modal-section">
      <h3>🏆 Collector Information</h3>
      <p class="info-line"><span class="il-label">Collector Ranking:</span><strong>${item.collector_ranking || "Unranked"}</strong></p>
      <p class="info-line"><span class="il-label">3-Mo Price:</span>${formatPrice(item)}${item.price_basis ? ` <em>(${item.price_basis})</em>` : ""}${item.price_thb_listings && item.price_thb_listings.length ? " <em>· each ฿ = a separate Thai listing</em>" : ""}</p>
      <p class="info-line"><span class="il-label">Price Confidence:</span>${escapeHtml(item.price_confidence || "None")}</p>
      ${item.collector_info && item.collector_info.known_issues ? `<p class="info-line"><span class="il-label">Known Issues:</span>${escapeHtml(item.collector_info.known_issues)}</p>` : ""}
      ${item.collector_info && item.collector_info.collector_notes ? `<p class="info-line"><span class="il-label">Collector Notes:</span>${escapeHtml(item.collector_info.collector_notes)}</p>` : ""}
    </div>

    <div class="modal-section">
      <h3>🔧 Restorer Information</h3>
      <p class="info-line"><span class="il-label">Recap Difficulty:</span>${wrenchDisplay(recap)} ${recap ? `(${recap}/5)` : ""}</p>
      ${item.restorer_info && item.restorer_info.estimated_recap_cost_usd ? `<p class="info-line"><span class="il-label">Est. Recap Cost:</span>$${item.restorer_info.estimated_recap_cost_usd} USD parts</p>` : ""}
      ${item.restorer_info && item.restorer_info.bias_spec_mv ? `<p class="info-line"><span class="il-label">Bias Spec:</span>${item.restorer_info.bias_spec_mv} mV</p>` : ""}
      ${item.restorer_info && item.restorer_info.recap_notes ? `<p class="info-line"><span class="il-label">Recap Notes:</span>${escapeHtml(item.restorer_info.recap_notes)}</p>` : ""}
      ${failurePoints.length ? `<p class="info-line" style="margin-top:12px;"><strong>Known Failure Points:</strong></p><ul class="fault-list">${failurePoints.map(f => `<li>${escapeHtml(f)}</li>`).join("")}</ul>` : ""}
      ${commonFaults.length ? `<p class="info-line" style="margin-top:12px;"><strong>Common Faults:</strong></p><ul class="fault-list simple">${commonFaults.map(f => `<li>${escapeHtml(f)}</li>`).join("")}</ul>` : ""}
    </div>

    ${item.best_buy && item.best_buy.rating ? `
    <div class="modal-section">
      <h3>⭐ Best Buy Rating</h3>
      <p class="info-line">Rating: <span class="bestbuy-star">${"⭐".repeat(item.best_buy.rating)}</span></p>
      ${item.best_buy.reason ? `<p class="info-line">Reason: ${escapeHtml(item.best_buy.reason)}</p>` : ""}
    </div>` : ""}

    <div class="modal-section">
      <h3>🔩 Capacitor List</h3>
      <div class="cap-phase2">
        Coming in Phase 2 — full cap list will appear here.
        <br><button disabled>Generate Cap Order List</button>
      </div>
    </div>

    ${(item.pros || item.cons) ? `
    <div class="modal-section">
      <h3>Pros / Cons</h3>
      <div class="pros-cons-grid">
        <div><h4>✅ Pros</h4><ul>${(item.pros ? item.pros.split(",") : []).map(p => `<li>${escapeHtml(p.trim())}</li>`).join("") || "<li>—</li>"}</ul></div>
        <div><h4>❌ Cons</h4><ul>${(item.cons ? item.cons.split(",") : []).map(c => `<li>${escapeHtml(c.trim())}</li>`).join("") || "<li>—</li>"}</ul></div>
      </div>
    </div>` : ""}

    <div class="modal-section">
      <h3>Links</h3>
      <div class="modal-links">
        ${item.links && item.links.audio_database ? `<a href="${item.links.audio_database}" target="_blank" rel="noopener">📄 Audio Database</a>` : ""}
        ${item.links && item.links.hifi_engine ? `<a href="${item.links.hifi_engine}" target="_blank" rel="noopener">📋 HiFi Engine</a>` : ""}
        ${item.links && item.links.sansui_us ? `<a href="${item.links.sansui_us}" target="_blank" rel="noopener">🌐 Sansui.us</a>` : ""}
        <a href="https://hifishark.com/?s=${encodeURIComponent("sansui " + item.jdm_model)}" target="_blank" rel="noopener">🔍 Search HiFi Shark</a>
        <a href="https://www.ebay.com/sch/i.html?_nkw=${encodeURIComponent("sansui " + item.jdm_model)}" target="_blank" rel="noopener">🔍 Search eBay</a>
      </div>
    </div>

    <div class="modal-section data-status">
      <span class="${item.verified ? "verified" : "unverified"}">${item.verified ? "✅ Verified by Wayne" : "⚠️ Unverified — specs sourced from web/period catalogs, not manually confirmed"}</span>
      <span>Last price check: ${escapeHtml(item.last_price_check || "—")}</span>
    </div>
  `;

  document.getElementById("modal-overlay").classList.add("open");
  document.body.style.overflow = "hidden";
}

function closeModal() {
  document.getElementById("modal-overlay").classList.remove("open");
  document.body.style.overflow = "";
}
