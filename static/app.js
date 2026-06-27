function renderDateBoard() {
  const board = document.getElementById("date-board");
  const today = new Date();
  const str = today.toLocaleDateString("es-PE", { day: "2-digit", month: "short", year: "numeric" })
    .toUpperCase().replace(/\./g, "");
  board.innerHTML = "";
  [...str].forEach((ch, i) => {
    const flap = document.createElement("div");
    flap.className = "flap";
    flap.textContent = ch === " " ? "\u00A0" : ch;
    flap.style.animationDelay = `${i * 0.04}s`;
    board.appendChild(flap);
  });
}

function setStatus(msg, isError) {
  const el = document.getElementById("status-line");
  if (!msg) { el.hidden = true; return; }
  el.hidden = false;
  el.textContent = msg;
  el.style.color = isError ? "var(--terracotta)" : "var(--paper-dim)";
}

function clearPanels() {
  document.querySelectorAll(".panel__body").forEach(body => {
    body.innerHTML = '<p class="panel__empty">Cargando...</p>';
  });
}

function renderPanels(data) {
  let totalHeadlines = 0;
  const secciones = data.secciones || {};
  document.querySelectorAll(".panel").forEach(panel => {
    const key = panel.dataset.section;
    const body = panel.querySelector(".panel__body");
    const items = secciones[key] || [];
    if (items.length === 0) {
      body.innerHTML = '<p class="panel__empty">Sin titulares disponibles para esta seccion hoy.</p>';
      return;
    }
    body.innerHTML = items.map(item => `
      <div class="headline">
        <p class="headline__title">${escapeHtml(item.titulo || "")}</p>
        <p class="headline__context">${escapeHtml(item.contexto || "")}</p>
        <span class="headline__source">${escapeHtml(item.fuente || "")}</span>
      </div>
    `).join("");
    totalHeadlines += items.length;
  });
  updateReadMeter(totalHeadlines);
}

function updateReadMeter(totalHeadlines) {
  const estMinutes = Math.min(30, Math.round(totalHeadlines * 1.2));
  document.getElementById("read-fill").style.width = `${(estMinutes / 30) * 100}%`;
  document.getElementById("read-time").textContent = `${estMinutes} / 30 MIN`;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

async function generateDigest() {
  const btn = document.getElementById("generate-btn");
  const label = btn.querySelector(".btn-generate__label");
  const spinner = btn.querySelector(".btn-generate__spinner");

  btn.disabled = true;
  spinner.hidden = false;
  label.textContent = "Buscando titulares...";
  setStatus(null);
  clearPanels();

  try {
    const res = await fetch("/api/news-digest", { method: "POST" });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || "Error desconocido");
    }
    renderPanels(data);
    setStatus(`Actualizado · ${new Date().toLocaleTimeString("es-PE")}`, false);
  } catch (err) {
    setStatus(`No se pudo generar el resumen: ${err.message}`, true);
    document.querySelectorAll(".panel__body").forEach(body => {
      body.innerHTML = '<p class="panel__empty">Error al cargar. Intenta de nuevo.</p>';
    });
  } finally {
    btn.disabled = false;
    spinner.hidden = true;
    label.textContent = "Generar resumen de hoy";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderDateBoard();
  document.getElementById("generate-btn").addEventListener("click", generateDigest);
});
