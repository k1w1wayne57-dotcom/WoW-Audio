// WoW Audio — admin console (Phase 1). Talks to serve.py on the same origin.
// Vanilla JS, no frameworks (matches app.js).

const RANKS = ["", "Top 10", "Top 10-20", "Top 20-30", "Top 30-40", "Top 40-50", "Unranked"];
const TYPES = ["Receiver", "Integrated", "Power Amp", "Preamp", "Tuner", "Tape Deck",
  "Quad", "Tube Power Amp", "Tube Preamp", "Turntable"];

// Field spec drives form generation + (de)serialization.
// type: text | textarea | int | number | select | selectfree | check | csvint | lines
const SECTIONS = [
  ["Identity", [
    { k: "id", label: "ID (auto-generated if blank)", type: "text", hint: "e.g. marantz-2226b-1977" },
    { k: "jdm_model", label: "Model *", type: "text" },
    { k: "int_model", label: "International model", type: "text" },
    { k: "type", label: "Type", type: "selectfree", options: TYPES },
    { k: "series", label: "Series", type: "text" },
    { k: "year_start", label: "Year start", type: "int" },
    { k: "year_end", label: "Year end", type: "int" },
  ]],
  ["Specifications", [
    { k: "watts_per_channel", label: "Watts / channel", type: "int" },
    { k: "freq_response_hz", label: "Freq response (Hz)", type: "text", hint: "e.g. 20-20000" },
    { k: "thd_percent", label: "THD %", type: "number" },
    { k: "ps_type", label: "PS type", type: "text" },
    { k: "weight_kg", label: "Weight (kg)", type: "number" },
    { k: "japan_price_kyen", label: "Japan price (k¥)", type: "number" },
    { k: "amp_circuit", label: "Amp circuit", type: "textarea", full: true },
    { k: "special_features", label: "Special features", type: "textarea", full: true },
  ]],
  ["Market & Price", [
    { k: "avg_price_usd_3mo", label: "Avg price USD (3mo)", type: "int" },
    { k: "price_basis", label: "Price basis", type: "text" },
    { k: "usd_msrp", label: "USD MSRP", type: "int" },
    { k: "price_thb_listings", label: "THB listings", type: "csvint", hint: "comma-separated, e.g. 11000, 11500" },
    { k: "thb_status", label: "Thai status", type: "select", options: ["", "For Sale", "Sold"] },
    { k: "market", label: "Target market", type: "select", options: ["", "JDM", "International"] },
    { k: "price_confidence", label: "Price confidence", type: "select", options: ["None", "Low", "Medium", "High"] },
    { k: "last_price_check", label: "Last price check", type: "text", hint: "YYYY-MM" },
    { k: "year_source", label: "Year source", type: "text", full: true },
  ]],
  ["Collector", [
    { k: "collector_ranking", label: "Collector ranking", type: "select", options: RANKS },
    { k: "best_buy.rating", label: "Best-buy rating (1-5)", type: "int" },
    { k: "pros", label: "Pros", type: "text", full: true, hint: "comma-separated" },
    { k: "cons", label: "Cons", type: "text", full: true, hint: "comma-separated" },
    { k: "best_buy.reason", label: "Best-buy reason", type: "textarea", full: true },
    { k: "collector_info.known_issues", label: "Known issues", type: "textarea", full: true },
    { k: "collector_info.collector_notes", label: "Collector notes", type: "textarea", full: true },
  ]],
  ["Restorer", [
    { k: "restorer_info.recap_difficulty", label: "Recap difficulty (1-5)", type: "int" },
    { k: "restorer_info.estimated_recap_cost_usd", label: "Est. recap cost USD", type: "int" },
    { k: "restorer_info.bias_spec_mv", label: "Bias spec (mV)", type: "number" },
    { k: "restorer_info.service_manual_link", label: "Service manual link", type: "text" },
    { k: "restorer_info.recap_notes", label: "Recap notes", type: "textarea", full: true },
    { k: "restorer_info.known_failure_points", label: "Known failure points", type: "lines", full: true, hint: "one per line" },
    { k: "restorer_info.common_faults", label: "Common faults", type: "lines", full: true, hint: "one per line" },
  ]],
  ["Sonic & Trust", [
    { k: "sonic_signature", label: "Sonic signature", type: "textarea", full: true },
    { k: "notes", label: "Notes", type: "textarea", full: true },
    { k: "verification", label: "Verification tier", type: "select", options: ["sourced", "verified", "unconfirmed"] },
    { k: "verified", label: "Verified by Wayne", type: "check" },
  ]],
  ["Links", [
    { k: "links.audio_database", label: "Audio Database", type: "text" },
    { k: "links.hifi_engine", label: "HiFi Engine", type: "text" },
    { k: "links.brochure", label: "Brochure", type: "text" },
    { k: "links.source", label: "Source", type: "text" },
    { k: "links.sansui_us", label: "sansui.us", type: "text" },
  ]],
];

const ALL_FIELDS = SECTIONS.flatMap(s => s[1]);
const elId = k => "f_" + k.replace(/\./g, "__");

let brand = "marantz";
let editingId = null;
let records = [];

const $ = id => document.getElementById(id);


// ---------- form build ----------
function buildForm() {
  const form = $("form");
  form.innerHTML = "";
  for (const [title, fields] of SECTIONS) {
    const fs = document.createElement("fieldset");
    const grid = document.createElement("div");
    grid.className = "grid";
    fs.innerHTML = `<legend>${title}</legend>`;
    for (const f of fields) {
      const wrap = document.createElement("div");
      wrap.className = "field" + (f.full ? " full" : "") + (f.type === "check" ? " check" : "");
      const id = elId(f.k);
      let control;
      if (f.type === "textarea") {
        control = `<textarea id="${id}"></textarea>`;
      } else if (f.type === "lines") {
        control = `<textarea id="${id}"></textarea>`;
      } else if (f.type === "select") {
        control = `<select id="${id}">${f.options.map(o => `<option value="${o}">${o || "—"}</option>`).join("")}</select>`;
      } else if (f.type === "selectfree") {
        control = `<input id="${id}" list="${id}_dl"><datalist id="${id}_dl">${f.options.map(o => `<option value="${o}">`).join("")}</datalist>`;
      } else if (f.type === "check") {
        control = `<input type="checkbox" id="${id}">`;
      } else {
        const it = (f.type === "int" || f.type === "number") ? "number" : "text";
        const step = f.type === "number" ? ` step="any"` : "";
        control = `<input type="${it}"${step} id="${id}">`;
      }
      if (f.type === "check") {
        wrap.innerHTML = `${control}<label for="${id}" style="margin:0">${f.label}</label>`;
      } else {
        wrap.innerHTML = `<label for="${id}">${f.label}</label>${control}` +
          (f.hint ? `<div class="hint">${f.hint}</div>` : "");
      }
      grid.appendChild(wrap);
    }
    fs.appendChild(grid);
    form.appendChild(fs);
  }
}


// ---------- nested get/set ----------
function getPath(obj, path) {
  return path.split(".").reduce((o, k) => (o == null ? undefined : o[k]), obj);
}
function setPath(obj, path, val) {
  const keys = path.split(".");
  let o = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    o[keys[i]] = o[keys[i]] || {};
    o = o[keys[i]];
  }
  o[keys[keys.length - 1]] = val;
}


// ---------- record -> form ----------
function fillForm(rec) {
  for (const f of ALL_FIELDS) {
    const el = $(elId(f.k));
    if (!el) continue;
    const v = rec ? getPath(rec, f.k) : undefined;
    if (f.type === "check") {
      el.checked = !!v;
    } else if (f.type === "csvint") {
      el.value = Array.isArray(v) ? v.join(", ") : "";
    } else if (f.type === "lines") {
      el.value = Array.isArray(v) ? v.join("\n") : "";
    } else {
      el.value = (v === null || v === undefined) ? "" : v;
    }
  }
}


// ---------- form -> record ----------
function serializeForm() {
  const rec = {};
  for (const f of ALL_FIELDS) {
    const el = $(elId(f.k));
    if (!el) continue;
    let val;
    if (f.type === "check") {
      val = el.checked;
    } else if (f.type === "int") {
      const n = parseInt(el.value, 10); val = isNaN(n) ? null : n;
    } else if (f.type === "number") {
      const n = parseFloat(el.value); val = isNaN(n) ? null : n;
    } else if (f.type === "csvint") {
      val = el.value.split(",").map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
    } else if (f.type === "lines") {
      val = el.value.split("\n").map(s => s.trim()).filter(Boolean);
    } else {
      const t = el.value.trim(); val = t === "" ? null : t;
    }
    setPath(rec, f.k, val);
  }
  return rec;
}


// ---------- server ----------
async function api(path, opts) {
  const r = await fetch(path, opts);
  const j = await r.json().catch(() => ({ ok: false, error: "bad response" }));
  if (!r.ok || !j.ok) throw new Error(j.error || r.statusText);
  return j;
}

async function loadRecords() {
  const j = await api(`/api/records?brand=${brand}`);
  records = j.records;
  const sel = $("existing");
  const filter = $("filter").value.trim().toLowerCase();
  sel.innerHTML = `<option value="">— new model —</option>`;
  records
    .filter(r => !filter || (`${r.jdm_model} ${r.int_model || ""}`).toLowerCase().includes(filter))
    .sort((a, b) => (a.jdm_model || "").localeCompare(b.jdm_model || ""))
    .forEach(r => {
      const o = document.createElement("option");
      o.value = r.id;
      const yr = r.year_start ? ` (${r.year_start})` : "";
      o.textContent = `${r.jdm_model}${r.int_model ? " / " + r.int_model : ""}${yr}`;
      sel.appendChild(o);
    });
  if (editingId) sel.value = editingId;
}

function setMode() {
  $("mode").textContent = editingId ? `EDITING ${editingId}` : "NEW MODEL";
  $("target").textContent = `data/${brand}.json`;
}

function selectExisting(id) {
  editingId = id || null;
  const rec = records.find(r => r.id === id);
  fillForm(rec || null);
  setMode();
  setStatus("");
}

function setStatus(msg, cls) {
  const s = $("status");
  s.textContent = msg;
  s.className = "status" + (cls ? " " + cls : "");
}

async function save() {
  const rec = serializeForm();
  if (!rec.jdm_model) { setStatus("Model is required.", "err"); return; }
  $("saveBtn").disabled = true;
  setStatus("Saving…");
  try {
    let j;
    if (editingId) {
      j = await api(`/api/records/${encodeURIComponent(editingId)}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand, record: rec }),
      });
    } else {
      j = await api(`/api/records`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brand, record: rec }),
      });
    }
    editingId = j.id;                     // stay on the record for further edits
    await loadRecords();
    setMode();
    setStatus(`Saved ${j.id} → data/${brand}.json. Remember to commit & push.`, "ok");
  } catch (e) {
    setStatus("Error: " + e.message, "err");
  } finally {
    $("saveBtn").disabled = false;
  }
}


async function refreshPrice() {
  const model = $("f_jdm_model").value.trim();
  if (!model) { setPriceStatus("Enter a model first.", "err"); return; }
  const months = parseInt($("priceMonths").value, 10) || 3;
  const btn = $("refreshPriceBtn");
  btn.disabled = true;
  setPriceStatus(`Fetching from HiFi Shark… (~10–20s)`);
  try {
    const j = await api(`/api/price?brand=${brand}&model=${encodeURIComponent(model)}&months=${months}`);
    if (!j.found) {
      setPriceStatus(`No dated listings for "${model}" in the last ${months} mo.`, "err");
      return;
    }
    $("f_avg_price_usd_3mo").value = j.median;
    $("f_price_basis").value = j.price_basis;
    let msg = `median $${j.median.toLocaleString()} from ${j.count} listings ` +
              `(range $${j.low.toLocaleString()}–$${j.high.toLocaleString()}). Review, then Save.`;
    if (j.skipped_currencies && j.skipped_currencies.length) {
      msg += ` [skipped: ${j.skipped_currencies.join(", ")}]`;
    }
    setPriceStatus(msg, "ok");
  } catch (e) {
    setPriceStatus("Error: " + e.message, "err");
  } finally {
    btn.disabled = false;
  }
}

function setPriceStatus(msg, cls) {
  const s = $("priceStatus");
  s.textContent = msg;
  s.className = "status" + (cls ? " " + cls : "");
}


// ---------- init ----------
async function init() {
  buildForm();
  try {
    const h = await api("/api/health");
    const bsel = $("brand");
    h.brands.forEach(b => {
      const o = document.createElement("option");
      o.value = b; o.textContent = b[0].toUpperCase() + b.slice(1);
      bsel.appendChild(o);
    });
    bsel.value = brand;
  } catch (e) {
    $("offline").style.display = "block";
    return;
  }

  $("brand").addEventListener("change", async e => {
    brand = e.target.value; editingId = null;
    fillForm(null); setMode(); await loadRecords();
  });
  $("existing").addEventListener("change", e => selectExisting(e.target.value));
  $("filter").addEventListener("input", loadRecords);
  $("newBtn").addEventListener("click", () => { editingId = null; fillForm(null); setMode(); $("existing").value = ""; setStatus(""); });
  $("revertBtn").addEventListener("click", () => selectExisting(editingId || ""));
  $("saveBtn").addEventListener("click", save);
  $("refreshPriceBtn").addEventListener("click", refreshPrice);

  setMode();
  await loadRecords();
}

init();
