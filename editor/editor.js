import { boxPxToPoints } from "./coords.js";

const pdfjsLib = await import("./vendor/pdf.mjs");
pdfjsLib.GlobalWorkerOptions.workerSrc = "./vendor/pdf.worker.mjs";

const RENDER_SCALE = 1.5; // pixels per point
let job = null;
let selected = null;

async function main() {
  job = await (await fetch("./job.json")).json();
  const pdfBytes = await (await fetch("./input.pdf")).arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: pdfBytes }).promise;
  const stage = document.getElementById("stage");

  for (const pageMeta of job.pages) {
    const page = await pdf.getPage(pageMeta.page);
    const viewport = page.getViewport({ scale: RENDER_SCALE });
    const wrap = document.createElement("div");
    wrap.className = "pagewrap";
    wrap.style.width = `${viewport.width}px`;
    wrap.style.height = `${viewport.height}px`;
    wrap.dataset.page = pageMeta.page;
    const canvas = document.createElement("canvas");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    wrap.appendChild(canvas);
    stage.appendChild(wrap);
    await page.render({ canvasContext: canvas.getContext("2d"), viewport }).promise;

    for (const f of job.fields.filter((f) => f.page === pageMeta.page)) {
      wrap.appendChild(makeBox(f));
    }
  }
  buildSidebar();
  document.getElementById("export").addEventListener("click", exportLayout);
  window.addEventListener("keydown", nudgeSelected);
}

function makeBox(f) {
  const el = document.createElement("div");
  el.className = "box" + (f.type === "signature" ? " signature" : "");
  el.dataset.id = f.id;
  el.style.left = `${f.x * RENDER_SCALE}px`;
  el.style.top = `${f.y * RENDER_SCALE}px`;
  el.style.minWidth = `${f.w * RENDER_SCALE}px`;
  el.style.height = `${f.h * RENDER_SCALE}px`;
  el.textContent = f.type === "signature" ? "sign here" : (f.value || f.label);
  // Signature stays blank; comb cells are auto-detected and precise, so neither drags.
  if (f.type !== "signature" && f.type !== "comb") enableDrag(el);
  el.addEventListener("mousedown", () => select(el));
  return el;
}

function select(el) {
  document.querySelectorAll(".box.selected").forEach((b) => b.classList.remove("selected"));
  el.classList.add("selected");
  selected = el;
}

function enableDrag(el) {
  let startX, startY, origLeft, origTop;
  el.addEventListener("mousedown", (e) => {
    startX = e.clientX; startY = e.clientY;
    origLeft = parseFloat(el.style.left); origTop = parseFloat(el.style.top);
    const move = (ev) => {
      el.style.left = `${origLeft + (ev.clientX - startX)}px`;
      el.style.top = `${origTop + (ev.clientY - startY)}px`;
    };
    const up = () => { document.removeEventListener("mousemove", move); document.removeEventListener("mouseup", up); };
    document.addEventListener("mousemove", move);
    document.addEventListener("mouseup", up);
  });
}

function nudgeSelected(e) {
  if (!selected) return;
  const step = e.shiftKey ? 10 : 1;
  const deltas = { ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step] };
  const d = deltas[e.key];
  if (!d) return;
  e.preventDefault();
  selected.style.left = `${parseFloat(selected.style.left) + d[0]}px`;
  selected.style.top = `${parseFloat(selected.style.top) + d[1]}px`;
}

function buildSidebar() {
  const container = document.getElementById("fields");
  for (const f of job.fields) {
    if (f.type === "signature") continue;
    const label = document.createElement("label");
    label.textContent = f.label;
    const input = document.createElement("input");
    input.value = f.value || "";
    input.addEventListener("input", () => {
      f.value = input.value;
      const box = document.querySelector(`.box[data-id="${f.id}"]`);
      if (box) box.textContent = input.value || f.label;
    });
    container.appendChild(label);
    container.appendChild(input);
  }
}

async function exportLayout() {
  const out = { fields: [] };
  for (const f of job.fields) {
    const box = document.querySelector(`.box[data-id="${f.id}"]`);
    const rect = { left: parseFloat(box.style.left), top: parseFloat(box.style.top),
                   width: box.offsetWidth, height: box.offsetHeight };
    const pts = boxPxToPoints(rect, RENDER_SCALE);
    out.fields.push({ ...f, x: pts.x, y: pts.y, w: pts.w, h: pts.h });
  }
  const res = await fetch("./export", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(out) });
  document.getElementById("status").textContent = res.ok ? "Exported. Ready to sign." : "Export failed.";
}

main();
