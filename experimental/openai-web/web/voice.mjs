import { createSession } from "./core.mjs";
import { requestProviderJob } from "./layout-client.mjs";
import { voiceUpdate, voiceFinalTurns } from "./voice-core.mjs";
import {
  loadMapMeasure,
  loadMapStatus,
  mapStatusCurrent,
} from "./measure-source.mjs";
import { loadMapEvidence, mountMapComparison } from "./map-view.mjs";

const $ = (id) => document.getElementById(id),
  session = createSession();
let language = "en",
  capability = null,
  abort,
  request,
  revision = 0,
  turn = 0,
  visualRevision = 0,
  map,
  measure,
  geometry;
let legalExpiryTimer;
let hasConversation = false;
function transcript(role, number, text, state) {
  const host = $("conversation-turns");
  let item = host.querySelector(
    `[data-turn="${number}"][data-speaker="${role}"]`,
  );
  if (!item) {
    item = make("li");
    item.dataset.turn = number;
    item.dataset.speaker = role;
    host.append(item);
  }
  item.lang = language;
  item.dataset.transcriptState = state;
  const labels = {
    provisional: es()
      ? "Transcripción provisional · idioma seleccionado"
      : "Provisional transcript · selected language",
    checked_text: es()
      ? "Respuesta comprobada · audio pendiente"
      : "Checked answer text · audio pending",
    final: es()
      ? "Transcripción final del audio comprobado · sin reproducción"
      : "Final checked audio transcript · not played",
  };
  const label = make(
    "p",
    (role === "user" ? (es() ? "Usted" : "You") : "OpenOracle") +
      " · " +
      labels[state],
  );
  label.className = "small";
  item.replaceChildren(label, make("p", text));
}
const make = (tag, text) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  return n;
};
const es = () => language === "es";
const fixtureAvailable = () =>
  capability?.voice_fixture_enabled &&
  capability.voice_fixture_languages?.includes(language);
function welcome() {
  const box = make("div");
  box.className = "canvas-welcome";
  box.append(
    make(
      "h2",
      es()
        ? "La vista adecuada, en el momento adecuado."
        : "The right view, at the right moment.",
    ),
    make(
      "p",
      es()
        ? "Mapas oficiales, comparaciones claras y texto original, conectados con la conversación."
        : "Official maps, clear comparisons and the original wording—connected to the conversation.",
    ),
  );
  return box;
}
const status = (text) => {
  $("connection").textContent = text;
};
function stop(erase = false) {
  session.reset();
  abort?.abort();
  abort = null;
  request = null;
  revision = 0;
  turn = 0;
  visualRevision++;
  clearTimeout(legalExpiryTimer);
  if (erase) {
    hasConversation = false;
    $("voice-idle").hidden = true;
    $("conversation-turns").replaceChildren();
    map?.dispose();
    map = null;
  }
  const legalNote = document.querySelector("[data-legal-status]");
  if (legalNote) {
    legalNote.lang = language;
    legalNote.textContent = es()
      ? "Conversación detenida. No se afirma el estado judicial vigente; consulte el expediente oficial."
      : "Conversation stopped. Current court status is not asserted; check the official docket.";
  }
  if (erase) {
    $("caption").textContent = es() ? "Sesión borrada." : "Session erased.";
    $("answer-state").textContent = "";
    $("visual").replaceChildren(welcome());
  }
  status(
    es()
      ? "Detenido · micrófono y altavoces apagados"
      : "Stopped · microphone and speakers off",
  );
  $("synthetic-run").disabled = !fixtureAvailable();
}
function original(host) {
  if (!measure) return;
  const details = make("details"),
    summary = make(
      "summary",
      es()
        ? "Texto original y fuente · inglés"
        : "Original wording and source · English",
    );
  const quote = make("blockquote", measure.complete_wording);
  quote.lang = "en";
  quote.className = "source-original";
  const a = make("a", measure.publisher + " · page " + measure.page);
  a.href = measure.url + "#page=" + measure.page;
  a.target = "_blank";
  a.rel = "noopener noreferrer";
  details.append(
    summary,
    quote,
    a,
    make(
      "p",
      "Retrieved: " +
        measure.retrieved_utc.slice(0, 10) +
        " · SHA256 " +
        measure.source_version,
    ),
  );
  host.append(details);
}
async function view(action, ticket) {
  clearTimeout(legalExpiryTimer);
  const ownRevision = ++visualRevision;
  const current = () =>
    session.current(ticket) && ownRevision === visualRevision;
  const host = $("visual");
  map?.dispose();
  map = null;
  host.replaceChildren(
    make("p", es() ? "Comprobando la fuente…" : "Checking the source…"),
  );
  try {
    const signal = AbortSignal.any([abort.signal, AbortSignal.timeout(5000)]);
    measure = measure ?? (await loadMapMeasure(signal));
    if (!current()) return;
    host.replaceChildren();
    if (action.view === "maps") {
      const title = make(
        "h2",
        es() ? "Dos planes. La misma vista." : "Two plans. One shared view.",
      );
      host.append(title);
      geometry = geometry ?? (await loadMapEvidence(signal));
      if (!current()) return;
      const maps = make("div");
      host.append(maps);
      map = mountMapComparison(maps, geometry, {
        locale: language,
        planLabels: measure.plan_labels,
      });
      if (action.mapFocus !== "unchanged")
        map.setView(
          { statewide: "statewide", kansas_city: "kc", st_louis: "stl" }[
            action.mapFocus
          ],
        );
      host.append(
        make(
          "p",
          es()
            ? "La descripción territorial accesible y los derechos de reutilización siguen pendientes. No se infiere su distrito."
            : "Accessible territorial description and reuse clearance remain pending. Your district is not inferred.",
        ),
      );
      const legal = await loadMapStatus(signal).catch(() => null);
      if (!current()) return;
      const note = make(
        "p",
        legal && mapStatusCurrent(legal)
          ? "As of " +
              legal.as_of_utc.slice(0, 10) +
              ": " +
              legal.claim +
              " " +
              legal.uncertainty
          : es()
            ? "Estado legal vigente no verificado."
            : "Current legal status is unverified.",
      );
      note.lang = "en";
      note.dataset.legalStatus = "snapshot";
      host.append(note);
      if (legal && mapStatusCurrent(legal)) {
        legalExpiryTimer = setTimeout(
          () => {
            if (current() && note.isConnected) {
              note.lang = language;
              note.textContent = es()
                ? "La revisión del estado legal ha vencido. Consulte el expediente oficial; no se afirma el estado vigente."
                : "This legal-status snapshot has expired. Check the official docket; no current status is asserted.";
            }
          },
          Math.min(
            2147483647,
            Math.max(0, Date.parse(legal.review_before_utc) - Date.now()),
          ),
        );
        const sources = make("details"),
          summary = make(
            "summary",
            es() ? "Fuentes del estado legal" : "Legal-status sources",
          );
        sources.append(summary);
        for (const source of legal.sources) {
          const a = make(
            "a",
            source.publisher +
              " · " +
              (source.page ? "page " + source.page : source.locator),
          );
          a.href = source.url + (source.page ? "#page=" + source.page : "");
          a.target = "_blank";
          a.rel = "noopener noreferrer";
          const item = make("p");
          item.append(a);
          sources.append(item);
        }
        host.append(sources);
      }
    } else if (action.view === "measure") {
      host.append(
        make(
          "h2",
          es()
            ? "La decisión que plantea el texto"
            : "The choice in the wording",
        ),
      );
      const pair = make("div");
      pair.className = "choice-pair";
      for (const id of ["yes", "no"]) {
        const card = make("section"),
          label = make("h3", id === "yes" ? "Yes" : "No"),
          text = make("p", measure.interpretation[id]);
        label.lang = text.lang = "en";
        card.append(label, text);
        pair.append(card);
      }
      host.append(
        pair,
        make(
          "p",
          es()
            ? "Explicaciones de la aplicación, no citas. Traducción cívica pendiente de revisión."
            : "Application explanations of the wording, not ballot quotations.",
        ),
      );
    } else if (action.view === "limits") {
      host.append(
        make(
          "h2",
          es() ? "Lo que aún no sabemos" : "What we still do not know",
        ),
        make(
          "p",
          es()
            ? "Esta muestra no establece su boleta ni su distrito. El texto no verifica el estado judicial ni qué mapa se usa en una elección."
            : "This sample does not establish your ballot or district. Its wording does not verify current court status or which map is used for an election.",
        ),
      );
    } else if (action.view === "clarify") {
      host.append(
        make(
          "h2",
          es()
            ? "¿Qué pregunta pública desea comprender?"
            : "Which public election question would you like to understand?",
        ),
        make(
          "p",
          es()
            ? "Este ejemplo cubre la Proposición A de Missouri. No necesitamos su dirección ni fecha de nacimiento."
            : "This example covers Missouri Proposition A. We do not need your address or date of birth.",
        ),
      );
    } else if (action.view === "abstain") {
      host.append(
        make(
          "h2",
          es()
            ? "Podemos explicar. No recomendar un voto."
            : "We can explain. We cannot recommend a vote.",
        ),
      );
    } else
      host.append(
        make("h2", es() ? "La pregunta oficial" : "The official question"),
      );
    if (current()) original(host);
  } catch {
    if (current())
      host.replaceChildren(
        make(
          "p",
          es()
            ? "La fuente no está disponible. No se muestra una explicación sin verificar."
            : "Source unavailable. An unchecked explanation is not shown.",
        ),
      );
  }
}
function progress(values, ticket) {
  if (!session.current(ticket)) return;
  for (const value of values) {
    if (value.revision <= revision) continue;
    const action = voiceUpdate(value, language, revision, turn);
    revision = action.revision;
    turn = action.turn;
    if (action.stage === "input_partial") {
      transcript("user", action.turn, action.text, "provisional");
      continue;
    }
    const labels = {
      connected: es()
        ? "GPT-Live conectado · entrada sintética pública"
        : "GPT-Live connected · public synthetic input",
      listening: es()
        ? "Recibiendo audio sintético…"
        : "Receiving synthetic audio…",
      routing: es()
        ? "Decisions está eligiendo la vista…"
        : "Decisions is choosing the view…",
      checked_text: es()
        ? "Respuesta contrastada con la fuente"
        : "Answer checked against the source",
      checking_speech: es()
        ? "Comprobando el audio · altavoces apagados"
        : "Checking generated speech · speakers off",
      speech_checked: es()
        ? "Segmento contrastado · finalización pendiente · sin reproducción"
        : "Segment checked · session finalization pending · not played",
      complete: es()
        ? "Interacción sintética terminada · revisión humana pendiente"
        : "Synthetic interaction finished · human review pending",
    };
    status(labels[action.stage]);
    if (action.stage === "routing") void view(action, ticket);
    if (action.stage === "checked_text") {
      transcript("assistant", action.turn, action.text, "checked_text");
      $("caption").textContent = es()
        ? "La respuesta está en la transcripción. El audio sigue retenido."
        : "The answer is in the transcript. Audio remains held.";
      $("answer-state").textContent = es()
        ? "Texto comprobado · audio aún retenido · revisión humana pendiente"
        : "Checked answer text · audio still held · human review pending";
    }
  }
}
async function synthetic() {
  if (!fixtureAvailable() || !capability.session_token) return;
  stop(true);
  const ticket = session.begin();
  hasConversation = true;
  abort = new AbortController();
  $("synthetic-run").disabled = true;
  status(
    es()
      ? "Iniciando prueba pública sintética…"
      : "Starting public synthetic conversation…",
  );
  const result = await requestProviderJob({
    task: "voice:synthetic:" + language,
    ticket,
    session,
    token: capability.session_token,
    signal: abort.signal,
    timeoutMs: 105000,
    onRequest: (id) => {
      request = id;
    },
    onProgress: (values) => progress(values, ticket),
    fallback: () => null,
    decode: (value) => {
      return voiceFinalTurns(value, language);
    },
  });
  if (!session.current(ticket)) return;
  if (!result)
    status(
      es()
        ? "La interacción no completó todas las comprobaciones. No se reproduce audio ni se reintenta automáticamente."
        : "The interaction did not complete all checks. No audio is played and there is no automatic retry.",
    );
  else {
    for (const action of result)
      transcript("assistant", action.turn, action.text, "final");
    $("answer-state").textContent = es()
      ? "Transcripciones finales comprobadas · altavoces apagados · revisión humana pendiente"
      : "Final transcripts checked · speakers off · human review pending";
  }
  $("synthetic-run").disabled = true;
}
$("interrupt").onclick = () => stop();
$("erase").onclick = () => stop(true);
$("synthetic-run").onclick = () => void synthetic();
$("start-talking").onclick = () =>
  status(
    es()
      ? "La captura humana aún no está habilitada."
      : "Human capture is not enabled yet.",
  );
$("language").onchange = () => {
  stop(true);
  language = $("language").value;
  $("synthetic-run").disabled = !fixtureAvailable();
  document.documentElement.lang = language;
  $("visual").replaceChildren(welcome());
  $("eyebrow").textContent = es()
    ? "COMPRENDA LA BOLETA"
    : "UNDERSTAND YOUR BALLOT";
  $("voice-title").textContent = es()
    ? "Pregunte. Vea. Comprenda."
    : "Ask. See. Understand.";
  $("voice-intro").textContent = es()
    ? "Una conversación sobre la pregunta. La evidencia aparece mientras explora."
    : "A conversation about the question. The evidence appears as you explore.";
  $("start-talking").textContent = es() ? "Empezar a hablar" : "Start talking";
  $("interrupt").textContent = es() ? "Detener" : "Stop";
  $("erase").textContent = es() ? "Terminar y borrar" : "End and erase";
  $("caption-label").textContent = es() ? "Conversación" : "Conversation";
  $("conversation-turns").setAttribute(
    "aria-label",
    es() ? "Turnos de conversación" : "Conversation turns",
  );
  $("caption").textContent = es()
    ? "La captura y reproducción humanas aún no están habilitadas."
    : "Human capture and playback are not enabled yet.";
  $("media-state").textContent = es()
    ? "Micrófono apagado · altavoces apagados"
    : "Microphone off · speakers off";
  $("source-label").textContent = es()
    ? "Fuentes, privacidad y estado de la vista"
    : "Sources, privacy and preview status";
  $("scope").textContent = es()
    ? "Ejemplo público: Proposición A de Missouri · KCEB W1-P7 · 3 de noviembre de 2026. Su boleta y su distrito no están verificados. Sin recomendaciones de voto."
    : "Public example: Missouri Proposition A · KCEB W1-P7 · November 3, 2026. Your personal ballot and district are unverified. No vote recommendations.";
  $("source-details").replaceChildren(
    make(
      "p",
      es()
        ? "La captura y reproducción humanas no están habilitadas. Esta página no inicia grabaciones. No ingrese datos privados del votante."
        : "Human microphone and speaker use is not enabled. No recording begins on this page. Do not enter private voter information.",
    ),
    make(
      "p",
      es()
        ? "El texto comprobado, el audio comprobado y la aceptación humana son estados distintos. Esta vista no es una demostración terminada de voz en tiempo real."
        : "Checked text, checked audio and human acceptance are separate states. This preview is not a finished realtime voice demonstration.",
    ),
  );
  status(
    es()
      ? "Vista de desarrollo · conversación humana aún no habilitada"
      : "Development preview · human conversation not yet enabled",
  );
};
addEventListener("pagehide", () => stop(true));
session.touch();
for (const name of ["pointerdown", "click", "keydown", "wheel", "focusin"])
  document.addEventListener(name, (event) => {
    // Suspended timers cannot let returning activity revive expired content.
    if (hasConversation && session.idle()) {
      stop(true);
      if (["pointerdown", "click", "keydown"].includes(name) && event.cancelable)
        event.preventDefault();
      event.stopImmediatePropagation();
    } else if ($("voice-idle").contains(event.target)) return;
    else session.touch();
    $("voice-idle").hidden = true;
  }, { capture: true });
$("voice-continue").onclick = () => {
  session.touch();
  $("visual").focus({ preventScroll: true });
  $("voice-idle").hidden = true;
};
setInterval(() => {
  if (hasConversation && session.idle()) {
    stop(true);
  } else if (hasConversation && session.idle(Date.now() + 20000)) {
    $("voice-idle").hidden = false;
    const message = es()
      ? "Esta sesión se borrará por inactividad. Puede continuar."
      : "This session will clear after inactivity. You can keep reading.";
    if ($("voice-idle-message").textContent !== message)
      $("voice-idle-message").textContent = message;
    const label = es()
      ? "Continuar la sesión"
      : "Keep this session";
    if ($("voice-continue").textContent !== label)
      $("voice-continue").textContent = label;
  } else $("voice-idle").hidden = true;
}, 1000);
try {
  const response = await fetch("/api/capabilities", {
    cache: "no-store",
    signal: AbortSignal.timeout(5000),
  });
  capability = await response.json();
  $("development").hidden = !capability.review_tools;
  $("synthetic-run").disabled = !fixtureAvailable();
  status("Development preview · human conversation not yet enabled");
} catch {
  status("Connection unavailable · microphone and speakers off");
}
