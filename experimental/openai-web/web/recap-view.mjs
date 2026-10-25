import { immutableCopy } from "./core.mjs";
import { INVENTORY_VERSION } from "./office-source.mjs";
import { journeyHeading } from "./journey-core.mjs";
const NEXT_STEPS_PIN =
  "af7758008f478eca9b5a5b6878e7cc2e8817975bd0827809e5944da34fcf7ae0";
export async function loadOfficialNextSteps(signal) {
  const response = await fetch("/official-nextsteps.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("nextsteps_unavailable");
  const bytes = await response.arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
  if (hash !== NEXT_STEPS_PIN) throw Error("nextsteps_integrity");
  const value = JSON.parse(new TextDecoder().decode(bytes));
  if (
    value.schema !== "openoracle-official-nextsteps/v1" ||
    Object.values(value.limits).some((v) => v !== false) ||
    value.sources.kceb.url !== "https://kceb.org/voters/status/" ||
    value.sources.jceb.url !== "https://jcebmo.org/sample-ballot/"
  )
    throw Error("nextsteps_scope");
  return immutableCopy(value);
}

// Explicit recap choices only. Navigation, check answers, visitor text and vote
// choices never enter this bounded, application-owned source contract.
function resolve(selection, inventory) {
  if (
    !selection ||
    Object.keys(selection).sort().join(",") !==
      "browse_version,contest_id,source_id" ||
    selection.browse_version !== INVENTORY_VERSION ||
    inventory.browse_version !== INVENTORY_VERSION
  )
    throw Error("recap_version");
  const contest = inventory.contests.find((c) => c.id === selection.contest_id);
  const occurrence = contest?.occurrences.find(
    (o) => o.source_id === selection.source_id,
  );
  const source = inventory.sources[selection.source_id];
  if (!contest || !occurrence || !source) throw Error("recap_context");
  if (
    !["candidate_election", "judicial_retention", "measure"].includes(
      contest.kind,
    )
  )
    throw Error("recap_component");
  const url = new URL(source.url);
  if (
    url.protocol !== "https:" ||
    url.username ||
    url.password ||
    url.port ||
    !["kceb.org", "jcebmo.org", "drive.google.com"].includes(url.hostname)
  )
    throw Error("recap_url");
  if (!url.hostname.includes("drive.google.com"))
    url.hash = "page=" + occurrence.page;
  return immutableCopy({
    selection,
    kind: contest.kind,
    label: contest.label,
    context: source.jurisdiction,
    publisher: source.publisher,
    retrieved: source.retrieved_utc,
    original_sha256: source.original_sha256,
    url: url.href,
    page: occurrence.page,
    rows: (occurrence.candidate_rows ?? []).map((r) => ({
      name: r.printed_name,
      party: r.printed_party,
    })),
    instruction: occurrence.instruction?.text ?? null,
    statuses: (occurrence.source_statuses ?? []).map((s) => ({
      text: s.text,
      party: s.party,
    })),
    wording: occurrence.wording ?? null,
    background_missing: contest.kind !== "measure",
  });
}

export function addRecapSource(entries, selection, inventory) {
  resolve(selection, inventory);
  const rest = entries.filter(
    (s) =>
      s.source_id !== selection.source_id ||
      s.contest_id !== selection.contest_id,
  );
  return immutableCopy([...rest, selection].slice(-6));
}

export function recapSourceCards(selections, inventory) {
  if (!Array.isArray(selections) || selections.length > 6)
    throw Error("recap_bounds");
  return selections.map((selection) => resolve(selection, inventory));
}

const el = (tag, text) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  return node;
};

// Presentation only. The existing application owns source choices, validated
// generated units, request lifetime, erasure and the callbacks supplied here.
export function mountRecapFrame(
  panel,
  { language, units, hasSources, onClose, renderSource },
) {
  const text = (en, es) => (language === "es" ? es : en);
  const host = el("div");
  panel.hidden = false;
  panel.replaceChildren(host);
  const heading = el(
    "h2",
    text("My recap · this tab only", "Mi resumen · solo en esta pestaña"),
  );
  heading.id = "session-recap-title";
  host.append(
    heading,
    el(
      "p",
      text(
        "Sources are added only when you choose. This is not a personal ballot or a voting record. Up to six sources; older entries are replaced. AI explanations still require human review.",
        "Solo se agregan fuentes cuando usted lo elige. No es una boleta personal ni un registro de votos. Hasta seis fuentes; las anteriores se reemplazan. Las explicaciones por IA requieren revisión humana.",
      ),
    ),
  );
  const close = el("button", text("Close recap", "Cerrar resumen"));
  close.type = "button";
  close.onclick = onClose;
  host.append(
    close,
    el(
      "h3",
      text(
        "Checked explanations in this language",
        "Explicaciones comprobadas en este idioma",
      ),
    ),
  );
  if (!units.length)
    host.append(
      el(
        "p",
        text(
          "No checked explanations in this language yet. You can still read the original.",
          "Aún no hay explicaciones comprobadas en este idioma. Puede consultar el original.",
        ),
      ),
    );
  for (const unit of units) {
    host.append(
      el("h4", journeyHeading(unit, language)),
      el(
        "p",
        text(
          "AI explanation · not a quotation · human review pending.",
          "Explicación por IA · no es una cita · revisión humana pendiente.",
        ),
      ),
    );
    for (const part of unit.sections) host.append(el("p", part.text));
    const original = el("details");
    original.append(
      el(
        "summary",
        text("Source for this explanation", "Fuente de esta explicación"),
      ),
    );
    for (const id of new Set(unit.sections.map((p) => p.source_id)))
      renderSource(original, id);
    host.append(original);
  }
  const sourceHost = el("section");
  sourceHost.textContent = hasSources
    ? text("Checking source versions…", "Comprobando versiones de fuentes…")
    : text(
        "No sources added. Browsing a source does not add it automatically.",
        "No ha agregado fuentes. Explorar una fuente no la agrega automáticamente.",
      );
  host.append(
    el(
      "h3",
      text("Sources you chose to keep here", "Fuentes que eligió guardar aquí"),
    ),
    sourceHost,
  );
  host.append(
    el(
      "p",
      text(
        "Unresolved: these public sources do not verify your personal ballot, district, current certification or eligible write-ins. They do not establish current court status. The recap disappears when the session is cleared.",
        "Pendiente: estas fuentes públicas no verifican su boleta personal, su distrito, la certificación actual ni candidatos elegibles por escrito. No establecen el estado judicial actual. El resumen desaparece al borrar la sesión.",
      ),
    ),
  );
  const notice = el(
    "p",
    text(
      "Local tab memory only; no account or automatic export.",
      "Solo memoria local; sin cuenta ni exportación automática.",
    ),
  );
  notice.setAttribute("role", "status");
  const nextSteps = el(
    "section",
    text("Checking official references…", "Comprobando referencias oficiales…"),
  );
  host.append(
    notice,
    el("h3", text("Official next steps", "Siguientes pasos oficiales")),
    nextSteps,
  );
  return { host, sourceHost, nextSteps };
}

export function mountRecapSources(host, cards, { language, onRemove }) {
  const text = (en, es) => (language === "es" ? es : en);
  for (const card of cards) {
    const article = el("article");
    article.append(el("h4", card.label), el("p", card.context));
    article.append(
      el(
        "p",
        text(
          "Source you explicitly added · not a personal ballot",
          "Fuente que agregó explícitamente · no es una boleta personal",
        ),
      ),
    );
    if (card.kind === "candidate_election") {
      if (card.instruction)
        article.append(
          el(
            "p",
            text(
              "Original printed instruction: ",
              "Instrucción original impresa: ",
            ) + card.instruction,
          ),
        );
      const list = el("ul");
      for (const row of card.rows)
        list.append(el("li", row.name + " · " + row.party));
      article.append(
        el(
          "p",
          text(
            "Printed source order, not a ranking. Eligible write-ins remain unverified.",
            "Orden impreso, no una clasificación. Candidatos elegibles por escrito sin verificar.",
          ),
        ),
        list,
      );
      for (const status of card.statuses)
        article.append(
          el(
            "p",
            status.text +
              " · " +
              status.party +
              text(
                " · printed status, not a candidate",
                " · estado impreso, no es un candidato",
              ),
          ),
        );
    } else if (card.wording) {
      const original = el("blockquote", card.wording);
      original.lang = "en";
      original.className = "original-wording";
      article.append(
        el("p", text("Original English wording", "Texto original en inglés")),
        original,
      );
    } else
      article.append(
        el(
          "p",
          text(
            "Full wording remains in the linked original; no local transcription is admitted for this occurrence.",
            "El texto completo está en el original enlazado; no se ha admitido una transcripción local para esta aparición.",
          ),
        ),
      );
    if (card.background_missing)
      article.append(
        el(
          "p",
          text(
            "Background evidence remains unadmitted. Missing evidence does not establish a position or performance.",
            "Fuentes de contexto aún no admitidas. La falta de fuentes no establece una postura ni un desempeño.",
          ),
        ),
      );
    const originalLink = el(
      "a",
      card.publisher + text(" · page ", " · página ") + card.page,
    );
    originalLink.href = card.url;
    originalLink.target = "_blank";
    originalLink.rel = "noopener noreferrer";
    article.append(
      originalLink,
      el("p", text("Retrieved: ", "Obtenido: ") + card.retrieved),
    );
    const details = el("details");
    details.append(
      el("summary", text("Source version", "Versión de la fuente")),
      el("p", "SHA256 " + card.original_sha256),
    );
    const remove = el(
      "button",
      text("Remove from recap", "Quitar del resumen"),
    );
    remove.type = "button";
    remove.onclick = () => onRemove(card.selection);
    article.append(details, remove);
    host.append(article);
  }
}

export function mountOfficialNextSteps(host, record, { language }) {
  const text = (en, es) => (language === "es" ? es : en);
  host.replaceChildren(
    el(
      "p",
      text(
        "These references cover only the two jurisdiction descriptions below; other election authorities are outside this preview. This recap cannot assign your jurisdiction. Use your own device for the official lookup: those sites ask for name and date of birth. This shared-terminal preview opens no lookup tab, sends no lookup details and imports no results. Erase here cannot clear activity on another site.",
        "Estas referencias cubren solo las dos jurisdicciones descritas a continuación; otras autoridades electorales quedan fuera de esta vista. Este resumen no determina su jurisdicción. Use su propio dispositivo para la consulta oficial: esos sitios piden nombre y fecha de nacimiento. Esta vista para terminal compartida no abre pestañas de consulta, no envía datos ni importa resultados. Borrar aquí no borra la actividad en otro sitio.",
      ),
    ),
  );
  for (const source of Object.values(record.sources)) {
    const section = el("section");
    section.append(el("h4", source.publisher), el("p", source.jurisdiction));
    section.append(
      el(
        "p",
        text(
          "Official lookup reference · use your own device",
          "Referencia de consulta oficial · use su propio dispositivo",
        ),
      ),
    );
    const lookup = el("p", source.url);
    lookup.lang = "en";
    section.append(
      lookup,
      el(
        "p",
        text("Navigation checked: ", "Navegación comprobada: ") +
          source.retrieved_utc.slice(0, 10),
      ),
    );
    const details = el("details");
    details.append(
      el(
        "summary",
        text("Navigation source version", "Versión de la fuente de navegación"),
      ),
      el("p", "SHA256 " + source.original_sha256),
    );
    section.append(details);
    host.append(section);
  }
}
