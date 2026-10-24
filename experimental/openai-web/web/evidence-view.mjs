import { immutableCopy } from "./core.mjs";
import { QUESTION_VERSION } from "./measure-source.mjs";

// The response chooses component names only. All facts, sources, controls and
// geometry stay application-owned; this module never creates a request/session.
const OPTIONAL = {
  brief: ["map_reference"],
  overview: ["choice_comparison", "map_reference"],
  simpler: ["map_reference"],
  detail: ["choice_comparison", "map_reference"],
  limits: [],
};
const REQUIRED = ["explanation", "original", "uncertainty"];
export function validateEvidencePlan(draft, operation) {
  const optional = OPTIONAL[operation];
  if (
    !optional ||
    !draft ||
    Object.keys(draft).join() !== "components" ||
    !Array.isArray(draft.components) ||
    draft.components.length < REQUIRED.length ||
    draft.components.length > REQUIRED.length + optional.length ||
    new Set(draft.components).size !== draft.components.length ||
    REQUIRED.some((id) => !draft.components.includes(id)) ||
    draft.components.some((id) => ![...REQUIRED, ...optional].includes(id))
  )
    throw Error("evidence_plan_unadmitted");
  return immutableCopy({ components: draft.components });
}

export function composeEvidence({
  operation,
  language,
  sourceVersion,
  unit = null,
}) {
  if (!["en", "es"].includes(language) || sourceVersion !== QUESTION_VERSION)
    throw Error("evidence_context");
  if (
    !Object.hasOwn(OPTIONAL, operation) &&
    !["source", "effects"].includes(operation)
  )
    throw Error("evidence_operation");
  if (
    unit &&
    (unit.operation !== operation ||
      unit.language !== language ||
      unit.source_version !== sourceVersion)
  )
    throw Error("evidence_unit_binding");
  const fallback =
    operation === "source"
      ? ["original", "uncertainty"]
      : operation === "effects"
        ? ["choice_comparison", "original", "uncertainty", "map_reference"]
        : operation === "limits"
          ? ["uncertainty", "explanation", "original"]
          : [
              "explanation",
              ...(operation === "overview" || operation === "detail"
                ? ["choice_comparison"]
                : []),
              "original",
              "uncertainty",
              "map_reference",
            ];
  const plan = unit?.presentation
    ? validateEvidencePlan(unit.presentation, operation)
    : { components: fallback };
  return immutableCopy({
    components: plan.components,
    mode:
      unit?.presentation_mode === "model_selected" ? "model_selected" : "local",
    source_version: sourceVersion,
    language,
  });
}

const node = (tag, text) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  return n;
};

// Presentation adapter: the existing application supplies admitted source and
// map renderers, and retains all cancellation, audio, focus and erase ownership.
export function mountEvidencePresentation(
  host,
  plan,
  { unit = null, renderSource, onMaps, mapsAvailable = false },
) {
  const es = plan.language === "es";
  host.replaceChildren();
  const mode = node(
    "p",
    plan.mode === "model_selected"
      ? es
        ? "IA eligió componentes admitidos · hechos de las fuentes"
        : "AI selected admitted components · facts from sources"
      : es
        ? "Composición local de evidencia · IA de diseño no ejecutada"
        : "Local evidence composition · layout AI not run",
  );
  mode.className = "small";
  host.append(mode);
  for (const kind of plan.components) {
    const card = node("section");
    card.dataset.evidenceComponent = kind;
    if (kind === "explanation") {
      card.append(
        node("h3", es ? "Comprender la pregunta" : "Understand the question"),
      );
      if (!unit)
        card.append(
          node(
            "p",
            es
              ? "No hay una explicación nueva por IA en esta vista. Puede leer y comparar las fuentes originales."
              : "No fresh AI explanation is available in this view. Read and compare the original sources below.",
          ),
        );
      else {
        card.append(
          node(
            "p",
            es
              ? "Explicación por IA · no es una cita · revisión humana pendiente"
              : "AI explanation · not a quotation · human review pending",
          ),
        );
        if (unit.request_fit === "unconfirmed")
          card.append(
            node(
              "p",
              es
                ? "El nivel de sencillez o detalle solicitado no está confirmado."
                : "The requested simplicity or detail is unconfirmed.",
            ),
          );
        for (const part of unit.sections) {
          card.append(node("p", part.text));
          const details = node("details");
          details.append(
            node(
              "summary",
              es ? "Comprobar esta explicación" : "Check this explanation",
            ),
          );
          renderSource(details, part.source_id);
          card.append(details);
        }
      }
    } else if (kind === "original") {
      const details = node("details");
      details.append(
        node(
          "summary",
          es
            ? "Pregunta oficial completa · inglés original"
            : "Complete official question · original English",
        ),
      );
      renderSource(details, "question");
      card.append(details);
    } else if (kind === "choice_comparison") {
      card.append(
        node(
          "h3",
          es
            ? "Sí y No · explicación del texto"
            : "Yes and No · explanation of the wording",
        ),
      );
      if (es)
        card.append(
          node(
            "p",
            "Explicación cívica en español pendiente de revisión. Las explicaciones originales en inglés siguen disponibles.",
          ),
        );
      const pair = node("div");
      pair.className = "effects-grid";
      for (const id of ["yes", "no"]) {
        const item = node("section");
        item.className = "effect";
        item.append(node("h4", id === "yes" ? "Yes" : "No"));
        renderSource(item, id);
        pair.append(item);
      }
      card.append(pair);
    } else if (kind === "uncertainty") {
      card.append(
        node(
          "h3",
          es
            ? "Lo que esta fuente no establece"
            : "What this source does not establish",
        ),
        node(
          "p",
          es
            ? "Esta muestra pública no verifica su boleta ni su distrito. El texto de la pregunta no establece el estado judicial actual ni qué mapa se usa en esta elección. La falta de fuentes no prueba una postura."
            : "This public sample does not verify your ballot or district. The question's wording does not establish current court status or which map is used in this election. Missing evidence does not establish a position.",
        ),
      );
    } else if (kind === "map_reference") {
      card.append(
        node(
          "h3",
          es ? "Consultar los mapas oficiales" : "Inspect the official maps",
        ),
        node(
          "p",
          es
            ? "Use las versiones verificadas que se muestran en esta página. Los números de distrito iguales no significan territorios iguales; no se infiere su distrito."
            : "Use the verified versions shown on this page. Matching district numbers do not mean matching territory; your district is not inferred.",
        ),
      );
      const button = node(
        "button",
        es ? "Ir a los mapas vinculados" : "Go to linked maps",
      );
      button.type = "button";
      button.disabled = !mapsAvailable;
      button.onclick = onMaps;
      card.append(button);
      if (!mapsAvailable)
        card.append(
          node(
            "p",
            es
              ? "Los mapas no están disponibles; el texto original permanece disponible."
              : "Map artifacts are unavailable; the original wording remains readable.",
          ),
        );
    } else throw Error("evidence_renderer_unadmitted");
    host.append(card);
  }
}
