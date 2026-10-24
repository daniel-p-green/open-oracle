import { validateMaps } from "./map-core.mjs";
import { immutableCopy } from "./core.mjs";
const ns = "http://www.w3.org/2000/svg";
const node = (tag, value) => {
  const e = document.createElement(tag);
  if (value !== undefined) e.textContent = value;
  return e;
};
export async function loadMapEvidence(signal) {
  const responses = await Promise.all(
    ["/maps.json", "/map-manifest.json", "/map-review-pin.json"].map((url) =>
      fetch(url, { cache: "no-store", signal }),
    ),
  );
  if (responses.some((r) => !r.ok)) throw Error("map_unavailable");
  const raw = await responses[0].text();
  if (raw.length > 8 * 1024 * 1024) throw Error("map_bound");
  const [registry, pin] = await Promise.all([
    responses[1].json(),
    responses[2].json(),
  ]);
  const bytes = new TextEncoder().encode(raw),
    hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  if (hash !== pin.sha256 || bytes.length !== pin.bytes)
    throw Error("map_integrity");
  return immutableCopy(validateMaps(JSON.parse(raw), registry));
}
export function mountMapComparison(
  host,
  data,
  { locale = "en", planLabels = {}, onChange = () => {} } = {},
) {
  let selected = null,
    viewId = "statewide",
    disposed = false;
  const es = locale === "es",
    controls = node("div"),
    viewControls = node("div"),
    districtControls = node("div"),
    status = node("p"),
    panels = node("div"),
    table = node("table");
  controls.className = "map-toolbar";
  viewControls.setAttribute("role", "group");
  viewControls.setAttribute(
    "aria-label",
    es ? "Vista de los dos mapas" : "View both maps",
  );
  districtControls.setAttribute("role", "group");
  districtControls.setAttribute(
    "aria-label",
    es ? "Número de distrito" : "District number",
  );
  panels.className = "comparison";
  status.setAttribute("role", "status");
  controls.append(viewControls, districtControls);
  host.append(controls, status, panels, table);
  const viewLabel = (v) =>
    ({
      statewide: es ? "Todo Missouri" : "Statewide",
      kc: es ? "Área de Kansas City" : "Kansas City area",
      stl: es ? "Área de St. Louis" : "St. Louis area",
    })[v.id];
  const planLabel = (p) => planLabels[p.id]?.[locale] ?? p.id;
  function draw() {
    if (disposed) return;
    const view = data.views.find((v) => v.id === viewId);
    panels.replaceChildren();
    table.replaceChildren();
    const caption = node(
      "caption",
      es
        ? "Distritos visibles en esta vista"
        : "Districts visible in this view",
    );
    table.append(caption);
    for (const plan of data.plans) {
      const article = node("article");
      article.className = "plan";
      const head = node("div");
      head.className = "plan-head";
      head.append(
        node("h3", planLabel(plan)),
        node(
          "p",
          plan.id === "baseline"
            ? "Census TIGER 2023 · CD118"
            : "HB1 · MSDIS / Missouri OA",
        ),
      );
      article.append(head);
      const svg = document.createElementNS(ns, "svg");
      svg.setAttribute("viewBox", view.bounds.join(" "));
      svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
      svg.setAttribute("role", "img");
      svg.setAttribute("aria-label", `${planLabel(plan)} · ${viewLabel(view)}`);
      for (const f of plan.features) {
        const path = document.createElementNS(ns, "path");
        path.setAttribute("d", f.path);
        path.setAttribute(
          "class",
          "district" +
            (selected === null
              ? ""
              : selected === f.id
                ? " selected"
                : " muted"),
        );
        svg.append(path);
      }
      for (const label of view.labels[plan.id]) {
        const t = document.createElementNS(ns, "text");
        t.setAttribute("x", label.x);
        t.setAttribute("y", label.y);
        t.setAttribute(
          "font-size",
          Math.max(view.bounds[2], view.bounds[3]) / 30,
        );
        t.setAttribute("class", "district-label");
        t.textContent = label.id;
        svg.append(t);
      }
      article.append(svg);
      panels.append(article);
      const tr = node("tr"),
        th = node("th", planLabel(plan));
      th.setAttribute("scope", "row");
      tr.append(
        th,
        node("td", view.labels[plan.id].map((l) => l.id).join(", ")),
      );
      table.append(tr);
    }
    for (const b of viewControls.children)
      b.setAttribute("aria-pressed", String(b.dataset.view === viewId));
    for (const b of districtControls.children)
      b.setAttribute(
        "aria-pressed",
        String(
          b.dataset.district === (selected === null ? "all" : String(selected)),
        ),
      );
    status.textContent =
      (es
        ? "No se dispone de una descripción territorial accesible verificada. "
        : "A verified accessible territorial description is not available. ") +
      (es
        ? "La escala y la vista son iguales en ambos mapas. El mismo número puede representar territorios diferentes."
        : "Both maps share scale and extent. Matching district numbers can cover different territory.");
  }
  for (const view of data.views) {
    const b = node("button", viewLabel(view));
    b.type = "button";
    b.dataset.view = view.id;
    b.onclick = () => {
      onChange();
      viewId = view.id;
      draw();
    };
    viewControls.append(b);
  }
  for (const id of [null, 1, 2, 3, 4, 5, 6, 7, 8]) {
    const b = node("button", id === null ? (es ? "Todos" : "All") : String(id));
    b.type = "button";
    b.dataset.district = id === null ? "all" : String(id);
    b.setAttribute(
      "aria-label",
      id === null
        ? es
          ? "Mostrar todos los distritos"
          : "Show all districts"
        : es
          ? `Resaltar distrito ${id}`
          : `Highlight district ${id}`,
    );
    b.onclick = () => {
      onChange();
      selected = id;
      draw();
    };
    districtControls.append(b);
  }
  draw();
  return {
    dispose() {
      disposed = true;
      host.replaceChildren();
    },
  };
}
