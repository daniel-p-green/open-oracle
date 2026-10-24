import { createSession, immutableCopy, validateCorpus } from "./core.mjs";
import {
  COPY,
  routeQuestion,
  experienceAnswer,
  baselineLayout,
  validateLayout,
} from "./experience-core.mjs";
import { loadMapEvidence, mountMapComparison } from "./map-view.mjs";
import { loadMapMeasure, loadMapStatus } from "./measure-source.mjs";
import { requestLayout, requestProviderJob } from "./layout-client.mjs";
import {
  publicJourneyAction,
  QUESTION_VERSION,
  validateJourney,
  recapUnits,
  journeyHeading,
  validateJourneySpeech,
} from "./journey-core.mjs";
import { admittedReadings, bindReading } from "./readings.mjs";
import { createSpeechOutput } from "./speech-output.mjs";
import { loadOfficeContext, INVENTORY_VERSION } from "./office-source.mjs";
import { mountContestInventory } from "./inventory-view.mjs";
import { draftPublicIntent, publicIntentLabel } from "./input-intent.mjs";
const $ = (id) => document.getElementById(id),
  session = createSession(),
  workspace = $("workspace");
let ready = false,
  renderComplete = false,
  legalExpiryTimer,
  remainingRuns = 0,
  currentTicket,
  reviewTools = false,
  corpus,
  manifest,
  readings = [],
  assets = [],
  locale = "en",
  intent = null,
  mapData,
  mapMeasure,
  mapMount,
  requestController,
  providerToken,
  activeRequest,
  preparedAudioRequest;
let journeyActive = false,
  journeyOperation = "overview",
  journeyUnits = [],
  journeyPending = false,
  journeyPendingKind = null;
let journeyCurrentUnit = null,
  journeyParentRequest = null,
  journeyRequestIds = [];
let pendingInput = null,
  inventoryActions = null;
const el = (tag, text) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  return n;
};
const speaker = createSpeechOutput({
  session,
  allowReview: () => reviewTools,
  fetchAudio: (url, signal) =>
    fetch(url, {
      signal,
      cache: "no-store",
      ...(url.startsWith("/api/provider/audio/")
        ? { headers: { "X-Session-Token": providerToken } }
        : {}),
    }),
  canPlay: async (asset, binding) => {
    if (
      !providerToken ||
      !journeyActive ||
      !journeyCurrentUnit ||
      asset.locale !== locale ||
      binding.parentRequest !== journeyParentRequest
    )
      return false;
    const response = await fetch("/api/provider/job/" + asset.id, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
      headers: { "X-Session-Token": providerToken },
    });
    if (!response.ok) return false;
    const job = await response.json();
    return (
      job.state === "ready" &&
      job.request_id === asset.id &&
      job.expires_in_seconds > 0 &&
      job.result?.source_version === asset.source_version &&
      job.result?.reading === asset.text &&
      job.result?.sha256 === asset.sha256 &&
      job.result?.independent_asr_match === true
    );
  },
  onChange: (state) => {
    const labels =
      locale === "es"
        ? {
            off: "Altavoces apagados",
            loading: "Verificando audio…",
            ready: "Lectura verificada y preparada",
            held: "Audio retenido",
            expired: "El audio preparado ha caducado",
            starting: "Iniciando audio",
            playing: "Reproduciendo",
            complete: "Lectura terminada",
            rehearsed: "Recorrido verificado sin sonido",
          }
        : {
            off: "Speaker off",
            loading: "Checking audio…",
            ready: "Reading checked and prepared",
            held: "Audio withheld",
            expired: "Prepared audio expired",
            starting: "Starting audio",
            playing: "Playing",
            complete: "Reading complete",
            rehearsed: "Lifecycle exercised without sound",
          };
    $("voice-state").textContent = labels[state.stage];
    $("transcript").textContent =
      state.reading || COPY[locale].speechUnavailable;
    $("play").disabled = !state.playable;
    $("rehearse").disabled = state.stage !== "ready";
    if (state.stage === "expired") {
      revokePreparedAudio();
      if (journeyActive && !journeyPending)
        $("journey-status").textContent =
          locale === "es"
            ? "El audio preparado ha caducado. La explicación escrita sigue disponible; no se genera más audio automáticamente."
            : "Prepared audio expired. The written explanation remains available; no new audio is generated automatically.";
    }
  },
});
function revokePreparedAudio() {
  if (preparedAudioRequest && providerToken)
    fetch("/api/provider/cancel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-Token": providerToken,
      },
      body: JSON.stringify({ request_id: preparedAudioRequest }),
      keepalive: true,
    }).catch(() => {});
  preparedAudioRequest = null;
}
function invalidate({ revokeConsent = false, keepVisuals = false } = {}) {
  clearInputDraft();
  session.reset();
  $("reorder").hidden = true;
  $("reorder").disabled = true;
  speaker.stop({ revokeConsent });
  requestController?.abort();
  requestController = null;
  if (activeRequest && providerToken)
    fetch("/api/provider/cancel", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-Token": providerToken,
      },
      body: JSON.stringify({ request_id: activeRequest }),
      keepalive: true,
    }).catch(() => {});
  activeRequest = null;
  revokePreparedAudio();
  if (journeyPending) {
    journeyPending = false;
    $("journey-status").textContent =
      locale === "es"
        ? "Se canceló la actividad pendiente. Puede consultar el original."
        : "Pending activity cancelled. You can read the original.";
  }
  journeyPendingKind = null;
  if (!keepVisuals) {
    inventoryActions = null;
    clearTimeout(legalExpiryTimer);
    renderComplete = false;
    mapMount?.dispose();
    mapMount = null;
  }
  if (revokeConsent) $("speaker-consent").checked = false;
}
function card(title, wide = false) {
  const n = el("article");
  n.className = "card" + (wide ? " card-wide" : "");
  n.append(el("h2", title));
  return n;
}
function link(url, title) {
  const n = el("a", title);
  n.href = url;
  n.target = "_blank";
  n.rel = "noopener noreferrer";
  n.className = "source-link";
  return n;
}
function appendSource(container, source) {
  container.append(
    link(source.url, source.title),
    el(
      "p",
      `${source.issuer} · ${locale === "es" ? "página" : "page"} ${source.page} · ${source.retrieved_date}`,
    ),
  );
}
function renderScope() {
  const c = card(COPY[locale].scope, true);
  c.classList.add("scope-card");
  c.append(el("p", COPY[locale].scopeText));
  return c;
}
function renderOriginal() {
  const s = corpus.sources[0],
    c = card(
      locale === "es"
        ? "Texto oficial original · inglés"
        : "Original official wording",
      true,
    );
  appendSource(c, s);
  const q = el("blockquote", s.text);
  q.className = "source-original";
  q.lang = "en";
  c.append(
    q,
    el(
      "p",
      `${locale === "es" ? "Versión SHA256" : "Version SHA256"}: ${s.text_sha256}`,
    ),
  );
  return c;
}
function renderClaim(claim) {
  const block = el("div"),
    p = el("p", claim.text);
  p.className = "fact-line";
  p.lang = "en";
  const quote = el("blockquote", claim.quote);
  quote.className = "source-original";
  quote.lang = "en";
  block.append(
    p,
    quote,
    link(
      corpus.sources[0].url + "#page=" + corpus.sources[0].page,
      `${COPY[locale].source} · p. ${corpus.sources[0].page}`,
    ),
  );
  return block;
}
function renderFacts(result, effects = false) {
  const c = card(
    effects
      ? locale === "es"
        ? "COMBAT · texto original: Yes / No"
        : "COMBAT · Yes / No"
      : locale === "es"
        ? "Explicación cívica · estado de revisión"
        : "Source-backed explanation",
    true,
  );
  if (result.status !== "answered") {
    c.append(
      el(
        "p",
        result.status === "translation_held"
          ? COPY[locale].translation
          : result.status === "advice_refused"
            ? COPY[locale].advice
            : result.status === "membership_unknown"
              ? COPY[locale].membership
              : result.status === "coverage_gap"
                ? COPY[locale].gap
                : locale === "es"
                  ? "Esta demostración aún no admite esa pregunta. Elija una pregunta de ejemplo."
                  : "This demo does not support that question yet. Choose an example question.",
      ),
    );
    return c;
  }
  const host = el("div");
  if (effects) host.className = "effects-grid";
  for (const claim of result.claims) {
    const d = renderClaim(claim);
    if (effects) {
      d.className = "effect";
      d.prepend(
        el(
          "h3",
          {
            yes: "Yes",
            no: "No",
            rate: "Printed rate",
            duration: "Duration",
            purpose: "Purpose",
            fund: "Separate fund",
          }[claim.id],
        ),
      );
    }
    host.append(d);
  }
  c.append(host);
  return c;
}
function renderGap(status) {
  const c = card(
    intent === "candidates"
      ? locale === "es"
        ? "Explorar concursos oficiales"
        : "Explore official contests"
      : locale === "es"
        ? "Cobertura y límites"
        : "Coverage and limits",
    true,
  );
  if (intent !== "candidates")
    c.append(
      el(
        "p",
        status === "advice_refused"
          ? COPY[locale].advice
          : status === "membership_unknown"
            ? COPY[locale].membership
            : status === "coverage_gap"
              ? COPY[locale].gap
              : locale === "es"
                ? "Esta demostración aún no admite esa pregunta. Elija un ejemplo para confirmar el tema."
                : "This demo does not support that question yet. Choose an example to confirm the topic.",
      ),
    );
  if (intent === "unknown") {
    const label = el(
      "h3",
      locale === "es"
        ? "¿Quiso decir uno de estos temas de la muestra pública?"
        : "Did you mean one of these public-sample topics?",
    );
    c.append(label);
    for (const text of publicExamples()) {
      const button = el("button", text);
      button.type = "button";
      button.onclick = () => {
        $("question").value = text;
        void explore(text);
      };
      c.append(button);
    }
  }
  if (intent === "candidates") {
    c.append(
      el(
        "p",
        locale === "es"
          ? "Explore los concursos impresos en los avisos públicos de KCEB y JCEB. No hemos verificado todos los estilos de boleta, su boleta personal ni su distrito."
          : "Browse the contests printed in KCEB and JCEB public notices. All ballot styles, your personal ballot and your district have not been verified.",
      ),
    );
    const contestHost = el("section");
    c.append(contestHost);
    void showContestInventory(contestHost);
  }
  return c;
}
function sourceReadContext() {
  requestController ??= new AbortController();
  const ticket = session.snapshot(),
    language = locale;
  return {
    signal: requestController.signal,
    current: () => locale === language && session.current(ticket),
  };
}
function showContestInventory(host) {
  const ticket = currentTicket,
    language = locale;
  return mountContestInventory(host, {
    language,
    signal: requestController.signal,
    isCurrent: () => locale === language && session.current(ticket),
    onRead: stopSpeechForReading,
    readContext: sourceReadContext,
    onActions: (context) => {
      inventoryActions = context;
      if (pendingInput?.kind === "inventory") clearInputDraft();
    },
    onOffice: showOffice,
    onMeasure: () => showJourney("overview"),
    translationNote: COPY[language].translation,
  });
}
async function renderMaps(ticket) {
  const c = card(
      locale === "es"
        ? "Compare los mapas oficiales"
        : "Compare the official maps",
      true,
    ),
    host = el("div");
  c.append(host);
  workspace.append(c);
  try {
    const sourceSignal = AbortSignal.any([
      requestController.signal,
      AbortSignal.timeout(5000),
    ]);
    mapMeasure = mapMeasure ?? (await loadMapMeasure(sourceSignal));
    if (!session.current(ticket)) return;
    try {
      if (!manifest) throw Error("map_manifest_unavailable");
      mapData = mapData ?? (await loadMapEvidence(sourceSignal));
      if (!session.current(ticket)) return;
      mapMount = mountMapComparison(host, mapData, {
        locale,
        planLabels: mapMeasure.plan_labels,
        onChange() {
          stopSpeechForReading();
          if (!journeyActive) {
            invalidate({ keepVisuals: true });
            currentTicket = session.begin();
            void prepareReading(currentTicket, true);
          }
        },
      });
    } catch {
      if (!session.current(ticket)) return;
      host.textContent =
        locale === "es"
          ? "Mapas no disponibles; el texto original sigue disponible."
          : "Map artifacts unavailable; the original wording remains readable.";
    }
    if (locale === "es")
      c.append(
        el(
          "p",
          "Estado legal: texto original en inglés; traducción cívica pendiente de revisión.",
        ),
      );
    const question = el("div");
    question.className = "map-question";
    question.lang = "en";
    question.append(
      el("h3", mapMeasure.label + " · official public sample"),
      el("blockquote", mapMeasure.text),
      link(
        mapMeasure.url + "#page=" + mapMeasure.page,
        mapMeasure.publisher +
          " · page " +
          mapMeasure.page +
          " · " +
          mapMeasure.retrieved_utc.slice(0, 10),
      ),
    );
    if (locale === "en") {
      question.append(
        el("h4", "Explanation of this wording"),
        el("p", mapMeasure.interpretation.yes),
        el("p", mapMeasure.interpretation.no),
      );
    } else
      question.prepend(
        el(
          "p",
          "Texto oficial en inglés; explicación cívica en español pendiente de revisión.",
        ),
      );
    const originalDetails = el("details"),
      originalSummary = el(
        "summary",
        locale === "es"
          ? "Pregunta oficial · texto original en inglés"
          : "Official question · original wording",
      );
    originalDetails.append(originalSummary, question);
    c.append(originalDetails);
    try {
      const legal = await loadMapStatus(
        AbortSignal.any([requestController.signal, AbortSignal.timeout(5000)]),
      );
      if (!session.current(ticket)) return;
      const note = el(
        "p",
        `As of ${legal.as_of_utc.slice(0, 10)} UTC: ${legal.claim} ${legal.uncertainty}`,
      );
      note.className = "map-legal";
      note.lang = "en";
      c.append(note);
      clearTimeout(legalExpiryTimer);
      legalExpiryTimer = setTimeout(
        () => {
          if (note.isConnected)
            note.textContent =
              "This legal-status snapshot has expired. Recheck the official docket; no current status is asserted.";
        },
        Math.min(
          2147483647,
          Math.max(0, Date.parse(legal.review_before_utc) - Date.now()),
        ),
      );
      const legalSources = el("ul");
      legalSources.className = "legal-sources";
      for (const source of legal.sources) {
        const item = el("li");
        item.append(
          link(
            source.url + (source.page ? "#page=" + source.page : ""),
            source.page
              ? source.publisher + " · page " + source.page
              : source.publisher +
                  " · docket retrieved " +
                  source.retrieved_utc.slice(0, 10),
          ),
        );
        legalSources.append(item);
      }
      c.append(legalSources);
    } catch {
      if (session.current(ticket))
        c.append(
          el(
            "p",
            locale === "es"
              ? "No se pudo verificar el estado legal vigente."
              : "Current legal status could not be verified.",
          ),
        );
    }
    c.append(el("p", COPY[locale].mapLimits));
  } catch {
    if (session.current(ticket))
      host.textContent =
        locale === "es"
          ? "La pregunta oficial no está disponible. Se retienen los mapas hasta verificar su fuente."
          : "Official question unavailable. Maps are withheld until their source binding can be verified.";
  }
}
function renderMapSources() {
  const c = card(
    locale === "es"
      ? "Fuentes y versiones de los mapas"
      : "Map sources and versions",
    true,
  );
  const disclosure = el("details");
  disclosure.append(
    el(
      "summary",
      locale === "es"
        ? "Consultar fuentes originales y versiones"
        : "Inspect original sources and versions",
    ),
  );
  for (const source of manifest?.sources ?? []) {
    const p = el("p");
    p.append(
      link(source.url, source.name),
      el(
        "span",
        ` · ${source.retrieved_utc.slice(0, 10)} · SHA256 ${source.sha256.slice(0, 16)}…`,
      ),
    );
    disclosure.append(p);
  }
  disclosure.append(
    el(
      "p",
      locale === "es"
        ? "Los números no prueban que el territorio sea el mismo. No se infiere su distrito."
        : "Matching numbers do not establish matching territory. Your district is not inferred.",
    ),
  );
  c.append(disclosure);
  return c;
}
async function planFor(currentIntent, ticket) {
  return requestLayout({
    intent: currentIntent,
    ticket,
    session,
    token: providerToken,
    signal: requestController.signal,
    onRequest: (id) => {
      if (session.current(ticket)) activeRequest = id;
    },
  });
}
async function explore(question, { focus = true } = {}) {
  const action = publicJourneyAction(question);
  if (action) return showJourney(action);
  journeyActive = false;
  $("experience-grid").classList.remove("journey-open");
  $("journey-panel").hidden = true;
  if (!ready) {
    $("status").textContent =
      locale === "es"
        ? "Las fuentes aún no están listas."
        : "Evidence is not ready yet.";
    return;
  }
  invalidate();
  const ticket = session.begin();
  currentTicket = ticket;
  let mapsVerified = false;
  requestController = new AbortController();
  intent = routeQuestion(question);
  document.body.classList.add("has-content");
  workspace.replaceChildren();
  $("status").textContent =
    locale === "es"
      ? "Consultando las fuentes admitidas…"
      : "Checking admitted evidence…";
  $("plan-mode").textContent = "";
  const result = await experienceAnswer(intent, corpus, locale),
    plan = {
      layout: validateLayout(baselineLayout(intent), intent),
      mode: "local",
    };
  if (!session.current(ticket) || !plan) return;
  $("status").textContent =
    result.status === "answered"
      ? locale === "es"
        ? "Fuente disponible"
        : "Source-backed explanation"
      : result.status === "maps"
        ? locale === "es"
          ? "Comparación de fuentes oficiales"
          : "Official-source comparison"
        : result.status === "translation_held"
          ? COPY[locale].translation
          : result.status === "advice_refused"
            ? COPY[locale].advice
            : result.status === "membership_unknown"
              ? COPY[locale].membership
              : result.status === "coverage_gap"
                ? COPY[locale].gap
                : locale === "es"
                  ? "Esta demostración aún no admite esa pregunta. Elija una pregunta de ejemplo."
                  : "This demo does not support that question yet. Choose an example question.";
  $("plan-mode").textContent =
    plan.mode === "live"
      ? locale === "es"
        ? "Composición de IA verificada · hechos de las fuentes"
        : "Checked AI composition · facts from sources"
      : plan.mode === "fallback"
        ? locale === "es"
          ? "Composición local · proveedor no disponible"
          : "Local composition · provider unavailable"
        : locale === "es"
          ? "Composición local · IA de diseño no ejecutada"
          : "Local composition · layout AI not run";
  $("reorder").hidden = true;
  $("reorder").disabled = true;
  for (const component of plan.layout.components) {
    if (!session.current(ticket)) return;
    if (component === "scope") workspace.append(renderScope());
    else if (component === "original") workspace.append(renderOriginal());
    else if (component === "facts" || component === "effects")
      workspace.append(renderFacts(result, component === "effects"));
    else if (component === "coverage")
      workspace.append(renderGap(result.status));
    else if (component === "map_sources") workspace.append(renderMapSources());
    else if (component === "maps") {
      await renderMaps(ticket);
      mapsVerified = !!mapMount;
    }
    if (workspace.lastElementChild)
      workspace.lastElementChild.dataset.component = component;
  }
  if (!session.current(ticket)) return;
  if (focus) workspace.focus({ preventScroll: true });
  renderComplete = true;
  $("reorder").hidden =
    !reviewTools || !providerToken || plan.layout.components.length < 3;
  $("reorder").disabled = remainingRuns <= 0;
  await prepareReading(ticket, mapsVerified);
  return session.current(ticket) ? ticket : null;
}
const journeyCopy = () =>
  locale === "es"
    ? {
        title: "Proposición A · comprender y comprobar",
        context:
          "Muestra pública KCEB W1-P7 · 3 de noviembre de 2026. Su boleta y su distrito no están verificados.",
        brief: "Explicación breve",
        overview: "Explique la pregunta",
        effects: "¿Qué significan Sí y No?",
        simpler: "Palabras más sencillas",
        detail: "Más detalles",
        limits: "¿Qué no sabemos?",
        source: "Consultar el texto original",
        challenge: "Esto no parece correcto",
        teach: "Comprobar mi comprensión · opcional",
        recap: "Mi resumen",
        office: "Ejemplo de cargo: Cámara de Representantes de EE. UU.",
        generate: "Generar explicación nueva",
        offline:
          "Puede leer el texto oficial y explorar los mapas. Las explicaciones nuevas por IA están desactivadas en esta vista.",
        pending: "Generando y comprobando una explicación nueva…",
        held: "La explicación no pasó la revisión de fuentes. Puede consultar el original.",
        checked: "Explicación por IA · revisión humana pendiente",
        unsupported:
          "El texto escrito permanece local. Confirme una pregunta pública con los botones; no se envía su texto.",
      }
    : {
        title: "Proposition A · understand and check",
        context:
          "KCEB W1-P7 public sample · November 3, 2026. Your ballot and district are unverified.",
        brief: "Brief explanation",
        overview: "Explain the question",
        effects: "What do Yes and No mean?",
        simpler: "Use simpler words",
        detail: "More detail",
        limits: "What don't we know?",
        source: "Check the exact wording",
        challenge: "That doesn't sound right",
        teach: "Check my understanding · optional",
        recap: "My recap",
        office: "Example office: U.S. House of Representatives",
        generate: "Generate a fresh explanation",
        offline:
          "Read the official wording and maps. Fresh AI explanations are off in this preview.",
        pending: "Generating and checking a fresh explanation…",
        held: "The explanation could not pass its source checks. You can still read the original.",
        checked: "AI explanation ready · human review pending",
        unsupported:
          "Your typed text stays local. Confirm a public question using the buttons; your text is not sent.",
      };
function publicExamples() {
  if (reviewTools) return COPY[locale].examples;
  return locale === "es"
    ? [
        "¿Qué pregunta la Proposición A?",
        "Mostrar los mapas oficiales",
        "¿Qué fuentes de candidatos están admitidas?",
      ]
    : [
        "What is Proposition A asking?",
        "Show the official maps",
        "What candidate evidence is admitted?",
      ];
}
function clearJourneyHistory() {
  for (const id of journeyRequestIds)
    if (providerToken)
      fetch("/api/provider/cancel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Session-Token": providerToken,
        },
        body: JSON.stringify({ request_id: id }),
        keepalive: true,
      }).catch(() => {});
  journeyRequestIds = [];
  journeyUnits = [];
  journeyCurrentUnit = null;
  journeyParentRequest = null;
  $("journey-tools").replaceChildren();
}
function showEffects() {
  stopSpeechForReading();
  const host = $("journey-tools");
  host.replaceChildren();
  if (!mapMeasure || (locale === "es" && !reviewTools)) {
    journeySource(host, "question");
    return;
  }
  host.append(
    el(
      "h3",
      locale === "es"
        ? "Explicación de lo que significan Sí y No"
        : "Explanation of what Yes and No mean",
    ),
  );
  for (const id of ["yes", "no"]) journeySource(host, id);
}
async function showOffice(host = $("journey-tools"), family = "us-house") {
  stopSpeechForReading();
  requestController ??= new AbortController();
  const anchor = el("section"),
    language = locale,
    ticket = session.snapshot();
  host.replaceChildren(anchor);
  anchor.append(
    el(
      "p",
      language === "es"
        ? "Consultando la fuente oficial…"
        : "Checking the official source…",
    ),
  );
  try {
    const source = await loadOfficeContext(
      family,
      AbortSignal.any([
        AbortSignal.timeout(5000),
        ...(requestController ? [requestController.signal] : []),
      ]),
    );
    if (!anchor.isConnected || locale !== language) return;
    if (!session.current(ticket)) {
      anchor.textContent =
        language === "es"
          ? "Se detuvo la carga de la fuente."
          : "Source loading stopped.";
      return;
    }
    anchor.replaceChildren(
      el(
        "h3",
        language === "es"
          ? source.office + " · fuente original en inglés"
          : source.office + " · original official explanation",
      ),
    );
    for (const passage of source.passages) {
      const quote = el("blockquote", passage.text);
      quote.lang = "en";
      anchor.append(quote, el("p", passage.locator));
    }
    const sources = new Map(
      source.passages.map((p) => [p.source.url, p.source]),
    );
    for (const record of sources.values())
      anchor.append(
        link(record.url, record.publisher),
        el(
          "p",
          `${language === "es" ? "Consultado" : "Retrieved"} ${record.retrieved_utc.slice(0, 10)} UTC`,
        ),
      );
    if (source.missing_fields?.includes("term_not_in_admitted_excerpt"))
      anchor.append(
        el(
          "p",
          language === "es"
            ? "No se ha cargado aquí una fuente para la duración del mandato."
            : "A source for the term length has not been loaded here.",
        ),
      );
    anchor.append(
      el(
        "p",
        language === "es"
          ? "Esta fuente describe el cargo; no demuestra el desempeño ni las promesas de ningún candidato. No determina su distrito ni su boleta. Traducción cívica pendiente de revisión."
          : "This source describes the office; it does not establish any candidate's performance or promises. It does not establish your district or ballot.",
      ),
    );
  } catch {
    if (anchor.isConnected && locale === language)
      anchor.textContent = !session.current(ticket)
        ? language === "es"
          ? "Se detuvo la carga de la fuente."
          : "Source loading stopped."
        : language === "es"
          ? "Fuente de la función del cargo no disponible."
          : "Official office explanation unavailable.";
  }
}
function journeyButton(host, label, action, disabled = false) {
  const b = el("button", label);
  b.type = "button";
  b.disabled = disabled;
  b.onclick = action;
  host.append(b);
  return b;
}
function journeySource(host, sourceId) {
  if (!mapMeasure) {
    host.append(
      el(
        "p",
        locale === "es"
          ? "Texto original no disponible."
          : "Original wording unavailable.",
      ),
    );
    return;
  }
  const q = el(
    "blockquote",
    sourceId === "yes"
      ? mapMeasure.interpretation.yes
      : sourceId === "no"
        ? mapMeasure.interpretation.no
        : mapMeasure.text,
  );
  q.lang = "en";
  q.className = "source-original";
  host.append(
    q,
    link(
      mapMeasure.url + "#page=" + mapMeasure.page,
      `${mapMeasure.publisher} · page ${mapMeasure.page} · original English`,
    ),
  );
  if (["yes", "no"].includes(sourceId))
    host.append(
      el(
        "p",
        locale === "es"
          ? "Explicación del texto por la aplicación; no es una cita de la boleta."
          : "Application explanation of the wording; not a ballot quotation.",
      ),
    );
  if (sourceId === "limits")
    host.append(
      el(
        "p",
        locale === "es"
          ? "Esta pregunta no establece su distrito ni el estado judicial actual."
          : "This question does not establish your district or current court status.",
      ),
    );
}
function drawJourney() {
  const c = journeyCopy();
  $("journey-panel").hidden = false;
  $("experience-grid").classList.add("journey-open");
  $("journey-title").textContent = c.title;
  $("journey-context").textContent = c.context;
  const actions = $("journey-actions");
  const next = $("journey-next");
  $("reorder").hidden = true;
  $("plan-mode").textContent = "";
  const locked = (op) =>
    !mapMeasure ||
    (locale === "es" && !reviewTools) ||
    (op !== "effects" &&
      (!providerToken || remainingRuns <= 0 || journeyPending));
  if (actions.dataset.language === locale && next.dataset.language === locale) {
    for (const button of actions.querySelectorAll("button"))
      button.disabled = locked(button.dataset.operation);
    return;
  }
  actions.replaceChildren();
  actions.dataset.language = locale;
  for (const op of [
    "brief",
    "overview",
    "effects",
    "simpler",
    "detail",
    "limits",
  ]) {
    const button = journeyButton(
      actions,
      c[op],
      () => {
        journeyOperation = op;
        if (op === "effects") showEffects();
        else void generateJourney();
      },
      locked(op),
    );
    button.dataset.operation = op;
  }
  next.replaceChildren();
  next.dataset.language = locale;
  journeyButton(next, c.source, () => performLocalJourney("source"));
  journeyButton(next, c.challenge, () => performLocalJourney("challenge"));
  journeyButton(next, c.teach, teachBack, locale === "es" && !reviewTools);
  journeyButton(next, c.recap, showRecap);
  journeyButton(next, c.office, () => void showOffice());
}
function performLocalJourney(operation) {
  if (!journeyActive) return;
  if (operation === "source") {
    stopSpeechForReading();
    const host = $("journey-tools");
    host.replaceChildren();
    journeySource(host, "question");
    host.focus();
  } else if (operation === "challenge") {
    invalidate({ keepVisuals: true });
    if (journeyParentRequest && providerToken)
      fetch("/api/provider/cancel", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Session-Token": providerToken,
        },
        body: JSON.stringify({ request_id: journeyParentRequest }),
        keepalive: true,
      }).catch(() => {});
    journeyParentRequest = null;
    $("journey-answer").replaceChildren();
    journeySource($("journey-answer"), "question");
    $("journey-status").textContent =
      locale === "es"
        ? "Se retiró la explicación de esta vista. Compare el original. No se envió ningún informe; no hay un servicio de correcciones conectado."
        : "Explanation withdrawn from this view. Compare the original. No report was sent; a staffed correction service is not connected.";
    journeyUnits = journeyUnits.filter((u) => u !== journeyCurrentUnit);
    journeyCurrentUnit = null;
    drawJourney();
  } else if (operation === "effects") showEffects();
  else if (operation === "recap") showRecap();
}
async function showJourney(operation = "overview") {
  const focusOrigin = document.activeElement;
  const ticket = await explore("maps", { focus: false });
  if (!ticket || !session.current(ticket) || intent !== "maps") return;
  journeyActive = true;
  journeyOperation = operation;
  speaker.stop();
  drawJourney();
  $("journey-tools").replaceChildren();
  $("journey-answer").replaceChildren();
  if (operation === "effects") showEffects();
  const c = journeyCopy();
  $("journey-status").textContent =
    locale === "es" && !reviewTools
      ? COPY.es.translation
      : !providerToken
        ? c.offline
        : remainingRuns <= 0
          ? locale === "es"
            ? "Se alcanzó el límite de explicaciones nuevas de esta sesión."
            : "This session's limit for fresh explanations has been reached."
          : c.unsupported;
  $("journey-panel").scrollIntoView({ block: "start", behavior: "instant" });
  if (
    document.activeElement === focusOrigin ||
    document.activeElement === document.body
  )
    $("journey-answer").focus({ preventScroll: true });
  return ticket;
}
async function generateJourney() {
  if (
    !journeyActive ||
    !mapMeasure ||
    !providerToken ||
    remainingRuns <= 0 ||
    (locale === "es" && !reviewTools)
  )
    return;
  invalidate({ keepVisuals: true });
  const ticket = session.begin();
  currentTicket = ticket;
  requestController = new AbortController();
  const language = locale,
    operation = journeyOperation;
  speaker.stop();
  remainingRuns--;
  journeyPending = true;
  journeyPendingKind = "text";
  drawJourney();
  for (const b of $("journey-actions").querySelectorAll("button"))
    b.disabled = true;
  $("journey-answer").replaceChildren();
  $("journey-status").textContent = journeyCopy().pending;
  let issuedRequest = null,
    notStarted = null;
  const result = await requestProviderJob({
    parentRequest: journeyParentRequest,
    task: `journey:${operation}:${language}`,
    ticket,
    session,
    token: providerToken,
    signal: requestController.signal,
    timeoutMs: 60000,
    onRequest: (id) => {
      if (session.current(ticket)) {
        activeRequest = id;
        if (id) {
          issuedRequest = id;
          journeyRequestIds.push(id);
        }
      }
    },
    fallback: () => null,
    onNotStarted: (reason) => {
      notStarted = reason;
    },
    decode: (value) =>
      validateJourney(value, operation, language, mapMeasure.source_version),
  });
  if (!session.current(ticket) || !journeyActive || locale !== language) return;
  journeyPending = false;
  journeyPendingKind = null;
  session.touch();
  if (notStarted) {
    remainingRuns = notStarted === "run_limit" ? 0 : remainingRuns + 1;
    journeyParentRequest = null;
  }
  drawJourney();
  $("journey-status").textContent = result
    ? journeyCopy().checked
    : journeyCopy().held;
  if (!result) {
    journeyParentRequest = null;
    if (notStarted)
      $("journey-status").textContent =
        locale === "es"
          ? "No se inició una llamada. El contexto anterior venció o el límite no está disponible. Elija una explicación nueva; no se reintenta automáticamente."
          : "No provider run started. Prior context expired or the run allowance is unavailable. Choose a fresh explanation deliberately; there is no automatic retry.";
    return;
  }
  journeyUnits = [...journeyUnits, result].slice(-6);
  journeyCurrentUnit = result;
  journeyParentRequest = issuedRequest;
  if (remainingRuns <= 0)
    $("journey-status").append(
      el(
        "p",
        locale === "es"
          ? "Se alcanzó el límite de explicaciones nuevas de esta sesión."
          : "This session's limit for fresh explanations has been reached.",
      ),
    );
  $("journey-answer").append(el("h3", journeyHeading(result, locale)));
  for (const part of result.sections) {
    const block = el("section");
    block.append(
      el(
        "p",
        locale === "es"
          ? "Explicación del texto de la pregunta · no es una cita."
          : "Explanation of the ballot question’s wording · not a quotation.",
      ),
    );
    block.append(el("p", part.text));
    const disclosure = el("details"),
      summary = el(
        "summary",
        locale === "es" ? "Comprobar la fuente" : "Check this source",
      );
    disclosure.append(summary);
    journeySource(disclosure, part.source_id);
    block.append(disclosure);
    $("journey-answer").append(block);
  }
  if (reviewTools && providerToken && remainingRuns > 0) {
    const button = journeyButton(
      $("journey-answer"),
      locale === "es"
        ? "Preparar voz nueva · revisión local"
        : "Prepare fresh voice · local review",
      () => {
        button.disabled = true;
        void prepareJourneySpeech();
      },
    );
    $("journey-answer").append(
      el(
        "p",
        locale === "es"
          ? "Genera audio desde esta explicación y comprueba la grabación completa. No activa altavoces ni micrófono. Revisión humana y de pronunciación pendientes."
          : "Generates speech from this explanation and checks the whole recording. Microphone and speakers stay off. Human and pronunciation review remain pending.",
      ),
    );
  }
  // The live status announces arrival; preserve the reader's chosen location.
}
async function prepareJourneySpeech() {
  if (
    !reviewTools ||
    !providerToken ||
    remainingRuns <= 0 ||
    journeyPending ||
    !journeyCurrentUnit ||
    !journeyParentRequest
  )
    return;
  const unit = journeyCurrentUnit,
    parent = journeyParentRequest,
    language = locale;
  invalidate({ keepVisuals: true });
  const ticket = session.begin();
  currentTicket = ticket;
  requestController = new AbortController();
  journeyPending = true;
  journeyPendingKind = "speech";
  remainingRuns--;
  drawJourney();
  $("journey-status").textContent =
    language === "es"
      ? "Preparando y transcribiendo audio nuevo antes de permitir su reproducción…"
      : "Preparing and independently transcribing fresh audio before making it playable…";
  let notStarted;
  const result = await requestProviderJob({
    task: "speech:" + language,
    parentRequest: parent,
    ticket,
    session,
    token: providerToken,
    signal: requestController.signal,
    timeoutMs: 115000,
    onRequest: (id) => {
      if (session.current(ticket)) {
        activeRequest = id;
        if (id) journeyRequestIds.push(id);
      }
    },
    onNotStarted: (reason) => {
      notStarted = reason;
    },
    fallback: () => null,
    decode: (value, job) => validateJourneySpeech(value, unit, job),
  });
  if (
    !session.current(ticket) ||
    !journeyActive ||
    locale !== language ||
    journeyCurrentUnit !== unit
  )
    return;
  journeyPending = false;
  journeyPendingKind = null;
  session.touch();
  if (notStarted)
    remainingRuns = notStarted === "run_limit" ? 0 : remainingRuns + 1;
  drawJourney();
  if (!result) {
    $("journey-status").textContent =
      notStarted === "speech_too_long"
        ? language === "es"
          ? "No se inició audio: la explicación es demasiado larga para esta lectura limitada. Puede elegir una explicación más breve; no se reintenta automáticamente."
          : "No audio run started: this explanation is too long for the bounded reading. Choose a shorter explanation deliberately; there is no automatic retry."
        : language === "es"
          ? "Audio retenido. La explicación escrita sigue disponible; no se reintenta automáticamente."
          : "Audio withheld. The written explanation remains available; there is no automatic retry.";
    return;
  }
  preparedAudioRequest = result.asset.id;
  const prepared = await speaker.prepare(result.asset, {
    ticket,
    locale: language,
    text: result.asset.text,
    sourceVersion: unit.source_version,
    parentRequest: parent,
    expiresAt: result.expiresAt,
  });
  if (!session.current(ticket)) return;
  if (prepared) $("speaker-consent").closest("label").hidden = false;
  $("voice-controls").open = true;
  $("journey-status").textContent = prepared
    ? language === "es"
      ? "Audio preparado para revisión local; sin aprobación humana. Altavoces apagados."
      : "Fresh audio prepared for local review; human approval pending. Speakers remain off."
    : language === "es"
      ? "Audio retenido; consulte la explicación escrita."
      : "Audio withheld; the written explanation remains available.";
}
function stopSpeechForReading() {
  // Same-parent source/map browsing never spends another preparation run.
  // Stop/Erase/Challenge/language/parent changes still revoke it immediately.
  speaker.halt();
}
function teachBack() {
  stopSpeechForReading();
  const host = $("journey-tools");
  host.replaceChildren();
  if (locale === "es" && !reviewTools) {
    $("journey-status").textContent = COPY.es.translation;
    journeySource(host, "question");
    return;
  }
  host.append(
    el(
      "p",
      locale === "es"
        ? "¿Qué significa un voto No en esta pregunta? Puede omitir esta actividad."
        : "What does a No vote do in this question? You can skip this activity.",
    ),
  );
  for (const [correct, label] of [
    [true, locale === "es" ? "Rechazar HB1" : "Reject HB1"],
    [false, locale === "es" ? "Aprobar HB1" : "Approve HB1"],
  ])
    journeyButton(host, label, () => {
      host.replaceChildren(
        el(
          "p",
          correct
            ? locale === "es"
              ? "Correcto. Un voto No rechaza el acto. Esto no establece qué mapa se usa en esta elección."
              : "Correct. A No vote rejects the act. This does not establish which map is used in this election."
            : locale === "es"
              ? "Un voto No rechaza el acto. Consulte la pregunta original; no establece el estado judicial actual."
              : "A No vote rejects the act. Check the original question; it does not establish current court status.",
        ),
      );
      journeySource(host, "question");
      host.focus({ preventScroll: true });
    });
  const notice = el(
    "p",
    locale === "es"
      ? "Actividad local opcional; no se guardan puntuaciones."
      : "Optional local activity; no scores are stored.",
  );
  notice.setAttribute("role", "status");
  host.append(notice);
}
function showRecap() {
  stopSpeechForReading();
  const host = $("journey-tools");
  host.replaceChildren();
  const units = recapUnits(journeyUnits, locale);
  host.append(el("h3", journeyCopy().recap));
  if (!units.length)
    host.append(
      el(
        "p",
        locale === "es"
          ? "Aún no hay explicaciones comprobadas en este idioma. Puede consultar el original."
          : "No checked explanations in this language yet. You can still read the original.",
      ),
    );
  for (const unit of units) {
    host.append(el("h4", journeyHeading(unit, locale)));
    for (const part of unit.sections) host.append(el("p", part.text));
  }
  host.append(
    el(
      "p",
      locale === "es"
        ? "Pendiente: su boleta, su distrito y el estado judicial actual no se establecen a partir de esta pregunta. Este resumen desaparece al borrar la sesión."
        : "Unresolved: your ballot, your district and current court status are not established by this question. This recap disappears when the session is cleared.",
    ),
  );
  journeySource(host, "question");
  const notice = el(
    "p",
    locale === "es"
      ? "Solo memoria local; sin cuenta ni exportación automática."
      : "Local tab memory only; no account or automatic export.",
  );
  notice.setAttribute("role", "status");
  host.append(notice);
}
async function prepareReading(ticket, mapsVerified) {
  const binding =
    (intent !== "maps" || mapsVerified) &&
    bindReading(
      assets.find((a) => a.intent === intent && a.locale === locale),
      readings,
      intent,
      locale,
    );
  if (binding)
    await speaker.prepare(binding.asset, {
      ticket,
      locale,
      text: binding.text,
      sourceVersion: binding.sourceVersion,
    });
  else speaker.stop();
}
function setCopy() {
  const t = COPY[locale];
  $("provider-data-note").textContent =
    locale === "es"
      ? "Solo se envían preguntas y fuentes públicas seleccionadas. Las respuestas y sesiones Live usan store:false. OpenOracle conserva el audio nuevo solo en memoria durante un máximo de dos minutos tras su preparación y cuatro minutos desde su solicitud. Los registros estándar de abuso de Responses, Decisions y Live pueden conservar contenido hasta 30 días, con excepciones legales o de seguridad. La documentación de transcripción indica que ese servicio no conserva contenido como estado ni registros de abuso. Borrar aquí no borra datos ya enviados al proveedor. No se ha verificado un acuerdo de retención cero para esta cuenta."
      : "Only selected public questions and evidence are sent. Responses and Live use store:false. OpenOracle keeps fresh audio in memory for at most two minutes after preparation and four minutes from its request. Standard Responses, Decisions and Live abuse logs may retain content for up to 30 days, with legal or safety exceptions. Transcription documentation lists no content retention for application state or abuse logs. Local Erase cannot delete data already sent to the provider. A zero-retention agreement has not been verified for this account.";
  $("voice-controls-summary").textContent =
    locale === "es"
      ? "Controles de voz · micrófono apagado"
      : "Voice controls · microphone off";
  document.documentElement.lang = locale;
  $("status").textContent = t.choose;
  workspace.setAttribute(
    "aria-label",
    locale === "es" ? "Explicación y fuentes" : "Explanation and evidence",
  );
  for (const [id, key] of Object.entries({
    title: "title",
    intro: "intro",
    "demo-label": "sample",
    "scope-label": "scope",
    privacy: "privacy",
    "question-label": "ask",
    explore: "submit",
    reset: "reset",
    "voice-title": "voice",
    "voice-note": "voiceNote",
    "speaker-consent-label": "consent",
    play: "play",
    rehearse: "silent",
    stop: "stop",
    "details-label": "details",
  }))
    $(id).textContent = t[key];
  document.querySelector(".skip").textContent =
    locale === "es" ? "Saltar a la explicación" : "Skip to explanation";
  $("examples").setAttribute(
    "aria-label",
    locale === "es" ? "Preguntas de ejemplo" : "Example questions",
  );
  $("reorder").textContent =
    locale === "es"
      ? "Probar orden de tarjetas con IA · opciones fijas"
      : "Try AI card ordering · fixed options";
  $("question").placeholder =
    locale === "es"
      ? "Por ejemplo: Mostrar los mapas oficiales"
      : "For example: Show the actual maps";
  $("question").value = "";
  $("examples").replaceChildren();
  for (const text of publicExamples()) {
    const b = el("button", text);
    b.type = "button";
    b.disabled = !ready;
    b.onclick = () => {
      $("question").value = text;
      void explore(text);
    };
    $("examples").append(b);
  }
  $("context-label").textContent =
    locale === "es"
      ? "Jackson County + Missouri · noviembre de 2026"
      : "Jackson County + Missouri · November 2026";
  $("footer-label").textContent =
    locale === "es"
      ? "Comprensión no partidista · Sin recomendaciones de voto · Sin grabación ambiental ni analítica"
      : "Nonpartisan comprehension · No vote recommendations · No ambient capture or analytics";
  $("review-limits").textContent =
    locale === "es"
      ? "Las explicaciones cívicas y la pronunciación en español requieren revisión. La preparación por IA, la admisión de fuentes, la revisión humana y la publicación son etapas distintas. No se ha importado una boleta personal."
      : "Spanish civic explanations and pronunciation require review. Prepared model output, source admission, human review and public release are separate states. No personal ballot has been imported.";
  $("capture-limit").textContent =
    locale === "es"
      ? "El micrófono está desactivado. Esta revisión usa preguntas escritas y ejemplos públicos preparados."
      : "Microphone capture is not enabled. This review uses typed questions and prepared public examples.";
  $("evidence-mode").textContent =
    locale === "es"
      ? "Las fuentes se guardan con sus versiones. Los datos de campaña y las traducciones cívicas no revisadas no se publican."
      : "Sources retain their versions. Unreviewed candidate material and civic translations are not published.";
  speaker.stop();
}
$("reorder").onclick = async () => {
  if (
    !providerToken ||
    remainingRuns <= 0 ||
    !intent ||
    !requestController ||
    !renderComplete ||
    !session.current(currentTicket)
  )
    return;
  const expected = baselineLayout(intent).components;
  if (
    expected.some(
      (id) => ![...workspace.children].some((n) => n.dataset.component === id),
    )
  )
    return;
  const ticket = session.begin();
  currentTicket = ticket;
  speaker.stop();
  $("reorder").disabled = true;
  remainingRuns--;
  const plan = await planFor(intent, ticket);
  if (!session.current(ticket) || !plan) return;
  if (plan.mode === "live") {
    const nodes = new Map(
      [...workspace.children].map((n) => [n.dataset.component, n]),
    );
    if (!plan.layout.components.every((id) => nodes.has(id))) {
      $("plan-mode").textContent =
        locale === "es"
          ? "Se conserva la vista local."
          : "Local view retained.";
      return;
    }
    workspace.replaceChildren(
      ...plan.layout.components.map((id) => nodes.get(id)),
    );
    $("plan-mode").textContent =
      locale === "es"
        ? "IA eligió el orden de tarjetas entre opciones fijas"
        : "AI chose card order from fixed options";
  } else
    $("plan-mode").textContent =
      locale === "es"
        ? "Se conserva el orden local; revisión de IA no completada"
        : "Local order retained; AI ordering check did not complete";
  if (remainingRuns <= 0) {
    // Keep the owner capability for Erase/cancel; the allowance gates inference.
    $("reorder").textContent =
      locale === "es"
        ? "Límite de pruebas de IA utilizado"
        : "AI test allowance used";
  } else $("reorder").disabled = false;
  await prepareReading(ticket, !!mapMount);
};
function clearInputDraft() {
  pendingInput = null;
  $("input-confirmation").hidden = true;
  $("input-action").textContent = "";
}
$("question-form").onsubmit = (e) => {
  e.preventDefault();
  clearInputDraft();
  const text = $("question").value;
  const draft = draftPublicIntent(text, {
    journeyActive,
    language: locale,
    sourceContext: inventoryActions
      ? {
          id: inventoryActions.id,
          version: inventoryActions.source_version,
          operations: Object.keys(inventoryActions.actions),
        }
      : null,
  });
  if (!draft) {
    const route = routeQuestion(text);
    $("status").textContent =
      route === "advice"
        ? COPY[locale].advice
        : route === "membership"
          ? COPY[locale].membership
          : locale === "es"
            ? "No se reconoció una acción admitida. El texto no se envió. Elija un botón o nombre la Proposición A."
            : "No supported action recognized. Your text was not sent. Choose a button or name Proposition A.";
    return;
  }
  pendingInput = draft;
  $("input-action").textContent =
    publicIntentLabel(draft, locale) +
    (draft.kind === "inventory" ? " · " + inventoryActions.title : "");
  $("input-note").textContent =
    locale === "es"
      ? "Compruebe la acción. Se envía solo la categoría pública y el idioma, nunca lo que escribió. Las acciones de lectura no usan IA."
      : "Check this action. Only the public category and language can be sent, never your words. Reading actions do not use AI.";
  $("confirm-input").textContent =
    locale === "es" ? "Confirmar acción" : "Confirm action";
  $("cancel-input").textContent =
    locale === "es" ? "Seguir escribiendo" : "Keep editing";
  $("input-confirmation").hidden = false;
  $("confirm-input").focus();
};
$("question").oninput = () => {
  clearInputDraft();
  // Drafting is local. Retain the checked parent, sources and map so "simpler"
  // can refer to the actual last answer. Stop any sound without starting work.
  stopSpeechForReading();
  $("status").textContent = COPY[locale].choose;
};
$("cancel-input").onclick = () => {
  clearInputDraft();
  $("question").focus();
};
$("confirm-input").onclick = async () => {
  const draft = pendingInput;
  clearInputDraft();
  $("question").value = "";
  if (!draft || (draft.kind !== "language" && draft.language !== locale))
    return;
  if (draft.kind === "inventory") {
    if (
      draft.source_version === INVENTORY_VERSION &&
      inventoryActions?.id === draft.context_id &&
      inventoryActions.source_version === draft.source_version
    ) {
      stopSpeechForReading();
      inventoryActions.actions[draft.operation]?.();
    }
    return;
  }
  if (draft.source_version !== QUESTION_VERSION) return;
  if (draft.kind === "language") {
    $("language").value = draft.language;
    $("language").dispatchEvent(new Event("change"));
    $("language").focus();
  } else if (
    draft.kind === "local" &&
    ["maps", "candidates"].includes(draft.operation)
  ) {
    await explore(draft.operation);
  } else {
    if (!journeyActive) {
      const ticket = await showJourney(draft.operation);
      if (!ticket || !session.current(ticket)) return;
    }
    if (!journeyActive) return;
    if (draft.kind === "local") performLocalJourney(draft.operation);
    else {
      journeyOperation = draft.operation;
      await generateJourney();
    }
  }
};
$("language").onchange = () => {
  const wasJourney = journeyActive,
    operation = journeyOperation;
  const old = intent;
  invalidate({ revokeConsent: true });
  locale = $("language").value;
  setCopy();
  if (wasJourney) {
    void showJourney(operation);
    return;
  }
  if (old)
    void explore(
      {
        maps: "maps",
        candidates: "candidates",
        rate: "tax rate",
        duration: "duration",
        purpose: "combat",
        effects: "yes and no",
        advice: "should i vote",
        membership: "my ballot",
        unknown: "unknown",
      }[old] ?? "unknown",
      { focus: false },
    );
  else workspace.replaceChildren();
};
$("reset").onclick = () => {
  invalidate({ revokeConsent: true });
  intent = null;
  document.body.classList.remove("has-content");
  $("experience-grid").classList.remove("journey-open");
  journeyActive = false;
  clearJourneyHistory();
  $("journey-panel").hidden = true;
  $("journey-answer").replaceChildren();
  $("question").value = "";
  workspace.replaceChildren();
  $("status").textContent = COPY[locale].clear;
  $("plan-mode").textContent = "";
  $("question").focus();
};
$("speaker-consent").onchange = () =>
  speaker.setConsent($("speaker-consent").checked);
$("play").onclick = () => void speaker.play();
$("rehearse").onclick = () => void speaker.play({ silent: true });
$("stop").onclick = () => {
  const keepVisuals = renderComplete;
  invalidate({ keepVisuals });
  if (!keepVisuals) workspace.replaceChildren();
  if (journeyActive) drawJourney();
  $("status").textContent =
    locale === "es"
      ? "Se detuvo la actividad pendiente."
      : "Pending activity stopped.";
};
for (const name of ["pointerdown", "keydown", "wheel", "scroll", "focusin"])
  document.addEventListener(name, () => {
    session.touch();
    $("idle-warning").hidden = true;
  });
setInterval(() => {
  $("idle-warning").hidden = !intent || !session.idle(Date.now() + 20000);
  $("idle-warning").textContent =
    locale === "es"
      ? "La sesión se borrará pronto por inactividad. Desplácese, toque o pulse una tecla para continuar."
      : "This session will clear soon for inactivity. Scroll, tap or press a key to continue.";
  if (intent && session.idle()) {
    invalidate({ revokeConsent: true });
    intent = null;
    document.body.classList.remove("has-content");
    $("experience-grid").classList.remove("journey-open");
    journeyActive = false;
    clearJourneyHistory();
    $("journey-panel").hidden = true;
    $("journey-answer").replaceChildren();
    $("question").value = "";
    workspace.replaceChildren();
    $("status").textContent = COPY[locale].clear;
    $("plan-mode").textContent = "";
    $("reorder").hidden = true;
  }
}, 1000);
addEventListener("pagehide", () => {
  invalidate({ revokeConsent: true });
  clearJourneyHistory();
});
addEventListener("pageshow", (event) => {
  if (event.persisted) {
    $("reset").click();
    $("question").blur();
  }
});
async function init() {
  setCopy();
  $("explore").disabled = true;
  if (
    typeof AbortSignal.any !== "function" ||
    typeof AbortSignal.timeout !== "function"
  ) {
    $("status").textContent =
      "This local review requires a current Chromium browser (120+).";
    return;
  }
  try {
    const r = await fetch("/fixture.json", {
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    if (!r.ok) throw Error();
    corpus = immutableCopy(await r.json());
    await validateCorpus(corpus);
  } catch {
    $("status").textContent =
      "Evidence unavailable. No explanation is released.";
    return;
  }
  const optional = async (url) => {
    try {
      const r = await fetch(url, {
        cache: "no-store",
        signal: AbortSignal.timeout(5000),
      });
      return r.ok ? await r.json() : null;
    } catch {
      return null;
    }
  };
  const [m, pin, prepared, caps] = await Promise.all(
    [
      "/map-manifest.json",
      "/map-review-pin.json",
      "/experience/manifest.json",
      "/api/capabilities",
    ].map(optional),
  );
  manifest = m;
  if (pin) readings = admittedReadings(corpus, pin);
  assets = immutableCopy(prepared?.audio ?? []);
  $("speaker-consent").closest("label").hidden = assets.length === 0;
  reviewTools = caps?.review_tools === true;
  remainingRuns = caps?.remaining_runs ?? 0;
  if (caps?.layout_enabled && remainingRuns > 0)
    providerToken = caps.session_token;
  $("review-links").hidden = !reviewTools;
  $("rehearse").hidden = !reviewTools;
  ready = true;
  setCopy();
  $("explore").disabled = false;
  $("status").textContent = COPY[locale].choose;
}
void init();
