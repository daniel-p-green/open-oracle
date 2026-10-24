import { immutableCopy } from "./core.mjs";
const GUIDE_PIN =
  "ce86fc958df059fecf6969a4f856577051d5c963f830ca9af401d2d81c217a91";
const INVENTORY_PIN =
  "0eda572a493274e25e845a1276b8ec28c3321dc40a8c2f13b7d761ad95645773";
const sha = async (text) =>
  [
    ...new Uint8Array(
      await crypto.subtle.digest(
        "SHA-256",
        typeof text === "string" ? new TextEncoder().encode(text) : text,
      ),
    ),
  ]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
const el = (tag, text) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  return n;
};

export async function checkedReadingGuide(bytes, contestId, occurrence) {
  if ((await sha(bytes)) !== GUIDE_PIN) throw Error("guide_integrity");
  const data = JSON.parse(new TextDecoder().decode(bytes));
  if (
    data.inventory_sha256 !== INVENTORY_PIN ||
    data.civic_interpretations_admitted !== false
  )
    throw Error("guide_scope");
  const guide = data.guides.find(
    (g) => g.contest_id === contestId && g.source_id === occurrence.source_id,
  );
  const text = occurrence.wording?.replace(/\s+/g, " ");
  if (
    !guide ||
    guide.wording_sha256 !== occurrence.wording_sha256 ||
    (await sha(occurrence.wording)) !== guide.wording_sha256 ||
    (await sha(text)) !== guide.normalized_wording_sha256
  )
    throw Error("guide_source_binding");
  for (const part of guide.ranges)
    if (
      !Number.isInteger(part.start) ||
      !Number.isInteger(part.end) ||
      part.start < 0 ||
      part.end > text.length ||
      part.end <= part.start ||
      text.slice(part.start, part.end) !== part.text ||
      (await sha(part.text)) !== part.sha256
    )
      throw Error("guide_span");
  return immutableCopy({ text, ranges: guide.ranges });
}

export function mountReadingGuide(
  host,
  original,
  contest,
  occurrence,
  { language, readContext, onRead },
) {
  const es = language === "es";
  const button = el(
    "button",
    es ? "Leer por partes · texto original" : "Read in parts · original words",
  );
  button.type = "button";
  const panel = el("section");
  panel.className = "source-reading-guide";
  host.append(button, panel);
  let pending = false;
  button.onclick = async () => {
    if (pending) return;
    pending = true;
    onRead();
    button.setAttribute("aria-disabled", "true");
    panel.replaceChildren(
      el(
        "p",
        es
          ? "Comprobando el pasaje original…"
          : "Checking the original passage…",
      ),
    );
    try {
      const context = readContext();
      const response = await fetch("/reading-guides.json", {
        cache: "no-store",
        signal: AbortSignal.any([context.signal, AbortSignal.timeout(2500)]),
      });
      if (!response.ok) throw Error("guide_unavailable");
      const guide = await checkedReadingGuide(
        await response.arrayBuffer(),
        contest.id,
        occurrence,
      );
      if (!panel.isConnected) return;
      if (!context.current()) {
        panel.textContent = es
          ? "Se detuvo la lectura de la fuente."
          : "Source reading stopped.";
        return;
      }
      const note = el(
        "p",
        es
          ? "Solo se resaltan palabras del original en inglés. No se ha generado una interpretación; se simplificaron los saltos de línea."
          : "Only original English words are highlighted. No interpretation was generated; line breaks are simplified.",
      );
      const status = el("p");
      status.setAttribute("role", "status");
      const controls = el("div");
      controls.className = "question-examples";
      panel.replaceChildren(note, controls, status);
      const labels = {
        conditions: ["Conditions", "Condiciones"],
        condition: ["Condition", "Condición"],
        full_condition: ["Full condition", "Condición completa"],
        full_question: ["Full question", "Pregunta completa"],
        rate_and_duration: ["Rate and time period", "Tasa y duración"],
        separate_fund: ["Separate fund", "Fondo separado"],
        rate_and_condition: ["Rate and condition", "Tasa y condición"],
        amount_and_purpose: ["Amount and purpose", "Importe y propósito"],
      };
      const highlight = (part) => {
        onRead();
        if (!original.isConnected) return;
        const mark = el("mark", part.text);
        mark.dataset.sourceId = occurrence.source_id;
        mark.lang = "en";
        original.replaceChildren(
          document.createTextNode(guide.text.slice(0, part.start)),
          mark,
          document.createTextNode(guide.text.slice(part.end)),
        );
        status.textContent = es
          ? "Pasaje resaltado. Lea también las palabras que lo rodean."
          : "Passage highlighted. Read the surrounding words too.";
      };
      for (const part of guide.ranges) {
        const choice = el("button", labels[part.role][es ? 1 : 0]);
        choice.type = "button";
        choice.onclick = () => highlight(part);
        controls.append(choice);
      }
      const clear = el(
        "button",
        es ? "Mostrar sin resaltar" : "Show without highlighting",
      );
      clear.type = "button";
      clear.onclick = () => {
        onRead();
        original.textContent = occurrence.wording;
        status.textContent = "";
      };
      controls.append(clear);
      highlight(guide.ranges[0]);
    } catch {
      if (panel.isConnected)
        panel.textContent = es
          ? "La guía no está disponible o se detuvo. El texto original sigue disponible."
          : "The reading aid is unavailable or stopped. The original remains readable.";
    } finally {
      pending = false;
      if (button.isConnected) button.removeAttribute("aria-disabled");
    }
  };
  return button;
}

export function mountSourceCheck(host, { language, onRead }) {
  const es = language === "es",
    section = el("section"),
    summary = el(
      "button",
      es ? "Comprobar esta fuente · opcional" : "Check this source · optional",
    );
  summary.type = "button";
  summary.setAttribute("aria-expanded", "false");
  host.append(summary, section);
  summary.onclick = () => {
    onRead();
    if (summary.getAttribute("aria-expanded") === "true") {
      section.replaceChildren();
      summary.setAttribute("aria-expanded", "false");
      return;
    }
    summary.setAttribute("aria-expanded", "true");
    section.replaceChildren(
      el(
        "p",
        es
          ? "¿Leer este aviso público verifica su boleta personal? Puede omitir esta actividad."
          : "Does reading this public notice verify your personal ballot? You can skip this activity.",
      ),
    );
    const feedback = el("p");
    feedback.setAttribute("role", "status");
    for (const [label, correct] of [
      [es ? "Sí, porque es oficial" : "Yes, because it is official", false],
      [
        es
          ? "No, solo consulté un aviso público"
          : "No, I only read a public notice",
        true,
      ],
    ]) {
      const button = el("button", label);
      button.type = "button";
      button.onclick = () => {
        onRead();
        feedback.textContent = correct
          ? es
            ? "Exacto: esta vista no ha verificado su asignación personal. Puede consultar los originales sin responder nada más."
            : "That's right: this view has not verified your personal assignment. You can read the originals without answering anything else."
          : es
            ? "Una fuente oficial puede cubrir muchas boletas distintas. Esta vista no ha verificado su asignación personal; no se guarda ni se envía su respuesta."
            : "An official source can cover many different ballots. This view has not verified your personal assignment; your answer is not saved or sent.";
      };
      section.append(button);
    }
    const skip = el("button", es ? "Omitir" : "Skip");
    skip.type = "button";
    skip.onclick = () => {
      section.replaceChildren();
      summary.setAttribute("aria-expanded", "false");
      summary.focus();
    };
    section.append(skip, feedback);
  };
  return summary;
}
