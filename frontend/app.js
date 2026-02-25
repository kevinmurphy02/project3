"use strict";
/*
  GameLog – Solo Project 3
  Client JS: fetch() → Flask/MySQL backend
  Features: CRUD, search, filter, sort, configurable paging (cookie), images
*/

// ── Cookie helpers ─────────────────────────────────────────────────────────
function setCookie(name, value, days = 365) {
  const d = new Date();
  d.setTime(d.getTime() + days * 86400000);
  document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/;SameSite=Lax`;
}
function getCookie(name) {
  const v = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return v ? decodeURIComponent(v[1]) : null;
}

// ── State ──────────────────────────────────────────────────────────────────
let currentPage  = 1;
let totalPages   = 1;
let pageSize     = parseInt(getCookie("page_size") || "10");
let searchVal    = "";
let statusFilter = "";
let platformFilter = "";
let sortVal      = "title";
let sortDir      = "asc";
let debounceTimer;

// ── DOM ────────────────────────────────────────────────────────────────────
const tabList    = document.getElementById("tabList");
const tabForm    = document.getElementById("tabForm");
const tabStats   = document.getElementById("tabStats");
const viewList   = document.getElementById("viewList");
const viewForm   = document.getElementById("viewForm");
const viewStats  = document.getElementById("viewStats");

const btnAddNew       = document.getElementById("btnAddNew");
const cardsGrid       = document.getElementById("cardsGrid");
const emptyState      = document.getElementById("emptyState");
const loadingState    = document.getElementById("loadingState");
const listError       = document.getElementById("listError");
const pagingBar       = document.getElementById("pagingBar");
const btnPrev         = document.getElementById("btnPrev");
const btnNext         = document.getElementById("btnNext");
const pageIndicator   = document.getElementById("pageIndicator");
const totalIndicator  = document.getElementById("totalIndicator");
const pageSizeSelect  = document.getElementById("pageSizeSelect");
const searchInput     = document.getElementById("searchInput");
const filterStatus    = document.getElementById("filterStatus");
const filterPlatform  = document.getElementById("filterPlatform");
const sortSelect      = document.getElementById("sortSelect");

const formTitle   = document.getElementById("formTitle");
const itemForm    = document.getElementById("itemForm");
const itemId      = document.getElementById("itemId");
const titleInput  = document.getElementById("titleInput");
const platformInput = document.getElementById("platformInput");
const statusInput = document.getElementById("statusInput");
const hoursInput  = document.getElementById("hoursInput");
const imageInput  = document.getElementById("imageInput");
const imgPreview  = document.getElementById("imgPreview");
const btnSave     = document.getElementById("btnSave");
const btnCancel   = document.getElementById("btnCancel");
const formBanner  = document.getElementById("formBanner");
const formSuccess = document.getElementById("formSuccess");

const errTitle    = document.getElementById("errTitle");
const errPlatform = document.getElementById("errPlatform");
const errStatus   = document.getElementById("errStatus");
const errHours    = document.getElementById("errHours");
const errImage    = document.getElementById("errImage");

const statTotal      = document.getElementById("statTotal");
const statCompletion = document.getElementById("statCompletion");
const statHours      = document.getElementById("statHours");
const statAvgHours   = document.getElementById("statAvgHours");
const statPageSize   = document.getElementById("statPageSize");
const statMostPlayed = document.getElementById("statMostPlayed");
const byStatusEl     = document.getElementById("byStatus");
const byPlatformEl   = document.getElementById("byPlatform");
const statsError     = document.getElementById("statsError");
const statsLoading   = document.getElementById("statsLoading");
const toast          = document.getElementById("toast");

const PLACEHOLDER = "https://placehold.co/300x200/1a2240/6aa7ff?text=No+Cover";

// ── Init page size from cookie ─────────────────────────────────────────────
pageSizeSelect.value = String(pageSize);

// ── API ────────────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}/api${path}`;
  const res  = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

// ── Toast ──────────────────────────────────────────────────────────────────
let toastTimeout;
function showToast(msg, type = "success") {
  clearTimeout(toastTimeout);
  toast.textContent = msg;
  toast.className = `toast toast-${type}`;
  toast.hidden = false;
  toastTimeout = setTimeout(() => { toast.hidden = true; }, 3000);
}

// ── Tabs ───────────────────────────────────────────────────────────────────
function setActiveTab(btn) {
  [tabList, tabForm, tabStats].forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}
function showView(name) {
  viewList.hidden  = name !== "list";
  viewForm.hidden  = name !== "form";
  viewStats.hidden = name !== "stats";
  if (name === "list")  { setActiveTab(tabList);  fetchAndRenderList(); }
  if (name === "form")  { setActiveTab(tabForm); }
  if (name === "stats") { setActiveTab(tabStats); fetchAndRenderStats(); }
}

// ── Escape HTML ────────────────────────────────────────────────────────────
function esc(s) {
  return String(s ?? "")
    .replaceAll("&","&amp;").replaceAll("<","&lt;")
    .replaceAll(">","&gt;").replaceAll('"',"&quot;");
}

// ── Status badge ───────────────────────────────────────────────────────────
function badgeClass(status) {
  return { Wishlist:"badge-wishlist", Backlog:"badge-backlog",
           Playing:"badge-playing", Completed:"badge-completed",
           Dropped:"badge-dropped" }[status] || "";
}

// ── List / Read ────────────────────────────────────────────────────────────
async function fetchAndRenderList() {
  listError.hidden  = true;
  emptyState.hidden = true;
  cardsGrid.innerHTML = "";
  loadingState.hidden = false;

  const params = new URLSearchParams({
    page: currentPage, page_size: pageSize,
    search: searchVal, status: statusFilter,
    platform: platformFilter, sort: sortVal, dir: sortDir,
  });

  const { ok, data } = await apiFetch(`/games?${params}`);
  loadingState.hidden = true;

  if (!ok) {
    listError.textContent = "Could not reach the backend. Check your API_BASE in config.js.";
    listError.hidden = false;
    return;
  }

  currentPage = data.page;
  totalPages  = data.total_pages;
  updatePaging(data.total);

  if (!data.games || data.games.length === 0) {
    emptyState.hidden = false;
    return;
  }

  for (const g of data.games) {
    cardsGrid.appendChild(buildCard(g));
  }
}

function buildCard(g) {
  const div = document.createElement("div");
  div.className = "game-card";
  const imgSrc = g.image_url || PLACEHOLDER;
  div.innerHTML = `
    <div class="card-img-wrap">
      <img class="card-img" src="${esc(imgSrc)}" alt="${esc(g.title)}"
           onerror="this.src='${PLACEHOLDER}'" loading="lazy" />
      <span class="card-badge ${badgeClass(g.status)}">${esc(g.status)}</span>
    </div>
    <div class="card-body">
      <div class="card-title">${esc(g.title)}</div>
      <div class="card-meta">${esc(g.platform)}</div>
      <div class="card-hours">${Number(g.hours).toFixed(1)} hrs</div>
      <div class="card-actions" style="margin-top:10px">
        <button class="btn-edit"   data-action="edit"   data-id="${g.id}">Edit</button>
        <button class="btn-delete" data-action="delete" data-id="${g.id}" data-title="${esc(g.title)}">Delete</button>
      </div>
    </div>`;
  return div;
}

function updatePaging(total) {
  pageIndicator.textContent  = `Page ${currentPage} of ${totalPages}`;
  totalIndicator.textContent = `${total} game${total !== 1 ? "s" : ""}`;
  btnPrev.disabled = currentPage <= 1;
  btnNext.disabled = currentPage >= totalPages;
}

// ── Search / filter / sort ─────────────────────────────────────────────────
searchInput.addEventListener("input", () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchVal   = searchInput.value.trim();
    currentPage = 1;
    fetchAndRenderList();
  }, 350);
});

filterStatus.addEventListener("change", () => {
  statusFilter = filterStatus.value;
  currentPage  = 1;
  fetchAndRenderList();
});

filterPlatform.addEventListener("change", () => {
  platformFilter = filterPlatform.value;
  currentPage    = 1;
  fetchAndRenderList();
});

sortSelect.addEventListener("change", () => {
  const [s, d] = sortSelect.value.split("|");
  sortVal = s; sortDir = d;
  currentPage = 1;
  fetchAndRenderList();
});

// ── Paging ─────────────────────────────────────────────────────────────────
btnPrev.addEventListener("click", () => { if (currentPage > 1)          { currentPage--; fetchAndRenderList(); } });
btnNext.addEventListener("click", () => { if (currentPage < totalPages) { currentPage++; fetchAndRenderList(); } });

pageSizeSelect.addEventListener("change", () => {
  pageSize    = parseInt(pageSizeSelect.value);
  currentPage = 1;
  setCookie("page_size", pageSize);
  fetchAndRenderList();
});

// ── Card click delegation ──────────────────────────────────────────────────
cardsGrid.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-action]");
  if (!btn) return;
  const { action, id, title } = btn.dataset;
  if (action === "edit")   handleEdit(parseInt(id));
  if (action === "delete") handleDelete(parseInt(id), title);
});

// ── Edit ───────────────────────────────────────────────────────────────────
async function handleEdit(id) {
  const { ok, data } = await apiFetch(`/games/${id}`);
  if (!ok) { showToast("Could not load game.", "error"); return; }
  setEditMode(data);
  showView("form");
}

// ── Delete ─────────────────────────────────────────────────────────────────
async function handleDelete(id, title) {
  if (!window.confirm(`Delete "${title}" from your library?`)) return;
  const { ok } = await apiFetch(`/games/${id}`, { method: "DELETE" });
  if (!ok) { showToast("Delete failed. Please try again.", "error"); return; }
  showToast(`"${title}" deleted.`);
  if (cardsGrid.querySelectorAll(".game-card").length === 1 && currentPage > 1) currentPage--;
  fetchAndRenderList();
}

// ── Form ───────────────────────────────────────────────────────────────────
function clearErrors() {
  [errTitle, errPlatform, errStatus, errHours, errImage].forEach(e => (e.hidden = true));
  formBanner.hidden  = true;
  formSuccess.hidden = true;
}

function setAddMode() {
  formTitle.textContent = "Add Game";
  itemId.value = "";
  itemForm.reset();
  imgPreview.src = PLACEHOLDER;
  clearErrors();
}

function setEditMode(g) {
  formTitle.textContent   = "Edit Game";
  itemId.value            = g.id;
  titleInput.value        = g.title;
  platformInput.value     = g.platform;
  statusInput.value       = g.status;
  hoursInput.value        = g.hours;
  imageInput.value        = g.image_url === PLACEHOLDER ? "" : (g.image_url || "");
  imgPreview.src          = g.image_url || PLACEHOLDER;
  clearErrors();
}

// Live image preview
imageInput.addEventListener("input", () => {
  const url = imageInput.value.trim();
  imgPreview.src = url || PLACEHOLDER;
});
imgPreview.addEventListener("error", () => { imgPreview.src = PLACEHOLDER; });

// Client-side validation
function validateClient() {
  clearErrors();
  let ok = true;
  const title   = titleInput.value.trim();
  const platform = platformInput.value;
  const status  = statusInput.value;
  const hours   = Number(hoursInput.value);
  const imgUrl  = imageInput.value.trim();

  if (title.length < 2 || title.length > 80)               { errTitle.hidden    = false; ok = false; }
  if (!platform)                                            { errPlatform.hidden = false; ok = false; }
  if (!status)                                              { errStatus.hidden   = false; ok = false; }
  if (!Number.isFinite(hours) || hours < 0 || hours > 9999){ errHours.hidden    = false; ok = false; }
  if (imgUrl.length > 600)                                  { errImage.hidden    = false; ok = false; }
  return ok;
}

function showServerErrors(errors) {
  if (errors.title)     { errTitle.textContent     = errors.title;    errTitle.hidden    = false; }
  if (errors.platform)  { errPlatform.textContent  = errors.platform; errPlatform.hidden = false; }
  if (errors.status)    { errStatus.textContent    = errors.status;   errStatus.hidden   = false; }
  if (errors.hours)     { errHours.textContent     = errors.hours;    errHours.hidden    = false; }
  if (errors.image_url) { errImage.textContent     = errors.image_url; errImage.hidden   = false; }
}

itemForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!validateClient()) return;

  btnSave.disabled    = true;
  btnSave.textContent = "Saving…";
  clearErrors();

  const payload = {
    title:     titleInput.value.trim(),
    platform:  platformInput.value,
    status:    statusInput.value,
    hours:     Number(hoursInput.value),
    image_url: imageInput.value.trim() || null,
  };

  const id = itemId.value;
  const { ok, data } = id
    ? await apiFetch(`/games/${id}`, { method: "PUT",  body: JSON.stringify(payload) })
    : await apiFetch("/games",       { method: "POST", body: JSON.stringify(payload) });

  btnSave.disabled    = false;
  btnSave.textContent = "Save Game";

  if (!ok) {
    if (data.errors) showServerErrors(data.errors);
    else { formBanner.textContent = data.error || "An error occurred."; formBanner.hidden = false; }
    return;
  }

  const action = id ? "updated" : "added";
  showToast(`"${data.title}" ${action} successfully!`);
  showView("list");
});

// ── Stats ──────────────────────────────────────────────────────────────────
async function fetchAndRenderStats() {
  statsError.hidden   = true;
  statsLoading.hidden = false;
  [statTotal, statCompletion, statHours, statAvgHours, statPageSize, statMostPlayed]
    .forEach(el => (el.textContent = "—"));
  byStatusEl.innerHTML = byPlatformEl.innerHTML = "";

  const { ok, data } = await apiFetch("/stats");
  statsLoading.hidden = true;

  if (!ok) { statsError.textContent = "Failed to load stats."; statsError.hidden = false; return; }

  statTotal.textContent      = data.total;
  statCompletion.textContent = `${data.completion_rate}%`;
  statHours.textContent      = `${data.total_hours} h`;
  statAvgHours.textContent   = `${data.avg_hours_completed} h`;
  statPageSize.textContent   = pageSize;
  statMostPlayed.textContent = data.most_played
    ? `${data.most_played.title} (${data.most_played.hours}h)`
    : "—";

  function renderBreakdown(container, obj, total) {
    for (const [label, count] of Object.entries(obj)) {
      const pct = total ? Math.round(count / total * 100) : 0;
      const row = document.createElement("div");
      row.className = "breakdown-row";
      row.innerHTML = `
        <span class="b-label">${esc(label)}</span>
        <div class="bar"><div class="bar-fill" style="width:${pct}%"></div></div>
        <span class="b-count">${count}</span>`;
      container.appendChild(row);
    }
  }
  renderBreakdown(byStatusEl,   data.by_status,   data.total);
  renderBreakdown(byPlatformEl, data.by_platform, data.total);
}

// ── Event bindings ─────────────────────────────────────────────────────────
tabList.addEventListener("click",   () => showView("list"));
tabForm.addEventListener("click",   () => { setAddMode(); showView("form"); });
tabStats.addEventListener("click",  () => showView("stats"));
btnAddNew.addEventListener("click", () => { setAddMode(); showView("form"); });
btnCancel.addEventListener("click", () => showView("list"));

// ── Boot ───────────────────────────────────────────────────────────────────
showView("list");
