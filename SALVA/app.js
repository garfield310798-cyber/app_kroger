function $(id){ return document.getElementById(id); }

function safeOn(id, evt, fn){
  const el = $(id);
  if(!el){
    console.warn(`No existe el elemento #${id} en index.html`);
    return;
  }
  el.addEventListener(evt, fn);
}

function setText(idOrEl, txt){
  const el = (typeof idOrEl === "string") ? $(idOrEl) : idOrEl;
  if(!el) return;
  el.textContent = (txt == null) ? "" : String(txt);
}

function setHtml(idOrEl, html){
  const el = (typeof idOrEl === "string") ? $(idOrEl) : idOrEl;
  if(!el) return;
  el.innerHTML = html == null ? "" : String(html);
}

function pretty(obj){
  try { return JSON.stringify(obj, null, 2); }
  catch(e){ return String(obj); }
}

// ---------------------------
// Accordion
// ---------------------------
function toggleSection(secId){
  const sec = $(secId);
  if(!sec) return;
  sec.classList.toggle("collapsed");

  const btn = sec.querySelector(`[data-toggle="${secId}"]`);
  if(btn){
    btn.textContent = sec.classList.contains("collapsed") ? "▸" : "▾";
  }
}

function initAccordions(){
  document.querySelectorAll(".section-header").forEach(h => {
    const secId = h.getAttribute("data-target");
    if(!secId) return;

    h.addEventListener("click", (e) => {
      const isBtn = e.target && e.target.matches && e.target.matches(".section-toggle-btn");
      if(isBtn) return;
      toggleSection(secId);
    });
  });

  document.querySelectorAll(".section-toggle-btn").forEach(b => {
    const secId = b.getAttribute("data-toggle");
    if(!secId) return;
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleSection(secId);
    });
  });

  // icono correcto al iniciar (todas plegadas)
  document.querySelectorAll(".section").forEach(sec => {
    const btn = sec.querySelector(`[data-toggle="${sec.id}"]`);
    if(btn){
      btn.textContent = sec.classList.contains("collapsed") ? "▸" : "▾";
    }
  });
}

// ---------------------------
// Clipboard helpers
// ---------------------------
async function copyText(txt){
  try{
    await navigator.clipboard.writeText(txt);
    return true;
  }catch(e){
    try{
      const ta = document.createElement("textarea");
      ta.value = txt;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      return true;
    }catch(_){
      return false;
    }
  }
}

async function pasteToInput(inputId){
  const el = $(inputId);
  if(!el) return;
  try{
    const txt = await navigator.clipboard.readText();
    el.value = (txt || "").trim();
    el.focus();
  }catch(e){
    console.error(e);
    alert("No se pudo pegar. El navegador puede bloquear clipboard si no es HTTPS o sin permiso.");
  }
}

async function copyFromInput(inputId){
  const el = $(inputId);
  if(!el) return false;
  return await copyText((el.value || "").trim());
}

// ---------------------------
// Store (Kroger API)
// ---------------------------
function setStoreLabel(store){
  if($("storeLabel")) $("storeLabel").textContent = store || "—";
  if($("storeHeaderLabel")) $("storeHeaderLabel").textContent = store || "—";
}

function loadStore(){
  const store = localStorage.getItem("kroger_store") || "";
  if($("storeInput")) $("storeInput").value = store;
  setStoreLabel(store);
  return store;
}

function saveStore(){
  const store = ($("storeInput") ? $("storeInput").value : "").trim();
  localStorage.setItem("kroger_store", store);
  setStoreLabel(store);
}

function clearStoreInput(){
  if($("storeInput")) $("storeInput").value = "";
  // el header/title sigue mostrando el store guardado
  setStoreLabel(localStorage.getItem("kroger_store") || "");
}

function renderStoresTable(stores){
  if(!Array.isArray(stores) || stores.length === 0){
    setHtml("storesOut", "No se encontraron stores.");
    return;
  }

  let html = `
    <table>
      <thead>
        <tr>
          <th style="width:120px;">Copiar</th>
          <th style="width:180px;">locationId</th>
          <th>address</th>
        </tr>
      </thead>
      <tbody>
  `;

  for(const s of stores){
    const locationId = s.locationId || "";
    const addr = `${s.addressLine1 || ""}, ${s.city || ""}, ${s.state || ""} ${s.zipCode || ""}`.trim();

    html += `
      <tr>
        <td><button class="copy-btn" data-copy="${locationId}">Copiar</button></td>
        <td><b>${locationId}</b></td>
        <td>${addr}</td>
      </tr>
    `;
  }

  html += `</tbody></table>`;
  setHtml("storesOut", html);

  document.querySelectorAll("[data-copy]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const val = btn.getAttribute("data-copy") || "";
      const ok = await copyText(val);
      btn.textContent = ok ? "Copiado" : "Error";
      setTimeout(() => (btn.textContent = "Copiar"), 900);
    });
  });
}

async function fetchStores(){
  const zip = ($("zipInput") ? $("zipInput").value : "").trim();
  setText("storesOut", "Cargando...");

  try{
    const r = await fetch(`/api/stores?zip=${encodeURIComponent(zip)}`);
    const data = await r.json();

    if(!r.ok){
      setText("storesOut", pretty(data));
      return;
    }

    renderStoresTable(data.data);
  }catch(e){
    console.error(e);
    setText("storesOut", `Error: ${e.message}`);
  }
}

// ---------------------------
// Buscar en tienda (Kroger API)
// ---------------------------
function clearProductImages(){
  const wrap = $("prodImgs");
  if(!wrap) return;
  wrap.innerHTML = "";
}

function renderProductImages(urls){
  const wrap = $("prodImgs");
  if(!wrap) return;

  wrap.innerHTML = "";

  if(!Array.isArray(urls) || urls.length === 0){
    wrap.innerHTML = `<span class="muted">Sin imágenes</span>`;
    return;
  }

  for(const u of urls){
    const img = document.createElement("img");
    img.src = u;
    img.alt = "product image";
    wrap.appendChild(img);
  }
}

async function fetchProduct(){
  const upc = ($("upcInput") ? $("upcInput").value : "").trim();
  const store = loadStore();

  setText("prodOut", "Cargando...");
  clearProductImages();

  if(!store){
    setText("prodOut", "Selecciona un store primero.");
    return;
  }

  try{
    const r = await fetch(`/api/product?upc=${encodeURIComponent(upc)}&store=${encodeURIComponent(store)}`);
    const data = await r.json();

    if(!r.ok){
      setText("prodOut", pretty(data));
      return;
    }

    if(!data.found){
      setText("prodOut", "Producto no encontrado.");
      return;
    }

    renderProductImages(data.image_urls || []);

    // Ubicación: Aisle, Bay, Shelf, Posición (ya viene en ese orden del backend)
    setText("prodOut",
      `Nombre:    ${data.name}\n` +
      `UPC:       ${data.upc}\n` +
      `Ubicación: ${data.location}\n` +
      `Store:     ${data.store}\n`
    );
  }catch(e){
    console.error(e);
    setText("prodOut", `Error: ${e.message}`);
  }
}

function clearUPC(){
  if($("upcInput")) $("upcInput").value = "";
  setText("prodOut", "—");
  clearProductImages();
}

// ---------------------------
// Projects (JSON en repo)
// ---------------------------
function getSelectedProject(){
  const sel = $("projectSelect");
  const p = (sel && sel.value) ? sel.value : "";
  localStorage.setItem("kroger_project", p);
  return p;
}

async function refreshProjects(){
  const sel = $("projectSelect");
  if(!sel){
    console.warn("No existe #projectSelect en index.html");
    return;
  }

  sel.innerHTML = "";
  setText("projectOut", "Cargando lista de projects...");

  try{
    const r = await fetch(`/api/projects`);
    const data = await r.json();

    if(!r.ok){
      setText("projectOut", pretty(data));
      return;
    }

    const list = data.data || [];

    const opt0 = document.createElement("option");
    opt0.value = "";
    opt0.textContent = "Selecciona un project...";
    sel.appendChild(opt0);

    if(list.length === 0){
      setText("projectOut", "No hay projects. Crea carpeta /projects y sube JSON ahí.");
      return;
    }

    const saved = localStorage.getItem("kroger_project") || "";

    for(const p of list){
      const opt = document.createElement("option");
      opt.value = p.id;
      opt.textContent = `${p.id} (${p.filename})`;
      sel.appendChild(opt);
    }

    if(saved){
      const found = list.some(x => x.id === saved);
      if(found) sel.value = saved;
    }

    setText("projectOut", `Lista cargada: ${list.length} project(s). Selecciona uno y presiona Load Project.`);
  }catch(e){
    console.error(e);
    setText("projectOut", `Error: ${e.message}`);
  }
}

async function loadProject(){
  const project = getSelectedProject();
  if(!project){
    setText("projectOut", "Selecciona un project primero.");
    return;
  }

  setText("projectOut", "Cargando project...");

  try{
    const r = await fetch(`/api/project?project=${encodeURIComponent(project)}`);
    const data = await r.json();

    if(!r.ok){
      setText("projectOut", pretty(data));
      return;
    }

    setText("projectOut", pretty(data.data));
  }catch(e){
    console.error(e);
    setText("projectOut", `Error: ${e.message}`);
  }
}

// ---------------------------
// Buscar en projecto (UPC dentro del Project)
// ---------------------------
async function scanProjectUPC(){
  const project = getSelectedProject();
  const upc = ($("projUpcInput") ? $("projUpcInput").value : "").trim();

  if(!project){
    setText("projOut", "Selecciona un project primero (arriba).");
    return;
  }
  if(!upc){
    setText("projOut", "Escribe un UPC.");
    return;
  }

  setText("projOut", "Buscando UPC en el project...");

  try{
    const r = await fetch(`/api/project_lookup?project=${encodeURIComponent(project)}&upc=${encodeURIComponent(upc)}`);
    const data = await r.json();

    if(!r.ok){
      setText("projOut", pretty(data));
      return;
    }

    if(!data.found){
      setText("projOut", `No encontrado.\nProject: ${data.project}\nUPC: ${data.upc}`);
      return;
    }

    setText("projOut",
      `Project:    ${data.project}\n` +
      `UPC:        ${data.upc}\n` +
      `Producto:   ${data.description}\n` +
      `Ubicación:  ${data.location}\n`
    );
  }catch(e){
    console.error(e);
    setText("projOut", `Error: ${e.message}`);
  }
}

function clearProjUPC(){
  if($("projUpcInput")) $("projUpcInput").value = "";
  setText("projOut", "—");
}

// ---------------------------
// Wire up
// ---------------------------
safeOn("zipGo", "click", fetchStores);
safeOn("storePaste", "click", () => pasteToInput("storeInput"));
safeOn("storeSave", "click", saveStore);
safeOn("storeClear", "click", clearStoreInput);

safeOn("upcPaste", "click", () => pasteToInput("upcInput"));
safeOn("upcCopy", "click", async () => {
  const ok = await copyFromInput("upcInput");
  if(!ok) alert("No se pudo copiar.");
});
safeOn("upcGo", "click", fetchProduct);
safeOn("upcClear", "click", clearUPC);

safeOn("projectsRefresh", "click", refreshProjects);
safeOn("projectLoad", "click", loadProject);

safeOn("projUpcPaste", "click", () => pasteToInput("projUpcInput"));
safeOn("projUpcCopy", "click", async () => {
  const ok = await copyFromInput("projUpcInput");
  if(!ok) alert("No se pudo copiar.");
});
safeOn("projUpcGo", "click", scanProjectUPC);
safeOn("projUpcClear", "click", clearProjUPC);

// init
initAccordions();
loadStore();
refreshProjects();
