import { answer, immutableCopy } from "./core.mjs";
export const INTENTS = Object.freeze([
  "effects",
  "rate",
  "duration",
  "purpose",
  "maps",
  "candidates",
  "unknown",
]);
const normalize = (text) =>
  text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim()
    .replace(/\s+/g, " ");
export function routeQuestion(text) {
  if (typeof text !== "string" || !text.trim() || text.length > 500)
    return "unknown";
  const q = normalize(text);
  if (
    /\b(ignore|system prompt|override|ignora|instrucciones del sistema)\b/.test(
      q,
    )
  )
    return "unknown";
  if (
    /\b(should i vote|who should|recommend|best candidate|persuade|convince|deberia votar|por quien votar|recomienda|mejor candidato)\b/.test(
      q,
    )
  )
    return "advice";
  if (
    /\b(my ballot|my district|my address|eligible|birth|dob|mi boleta|mi distrito|mi direccion|nacimiento)\b/.test(
      q,
    )
  )
    return "membership";
  // Finite aliases preserve the actual question's scope. A keyword such as
  // "rate" must never turn a different tax/measure/jurisdiction into COMBAT.
  const aliases = {
    maps: [
      "show the actual maps",
      "show the official maps",
      "compare the official maps",
      "compare missouri's congressional maps",
      "comparar los mapas del congreso de missouri",
      "mostrar los mapas oficiales",
      "mostrar los mapas",
      "maps",
      "mapas",
    ],
    candidates: [
      "show the candidates",
      "mostrar los candidatos",
      "what candidate evidence is available",
      "what candidate evidence is admitted",
      "que fuentes de candidatos estan admitidas",
      "what candidate evidence is admitted",
      "que fuentes de candidatos estan admitidas",
      "what sources are available about candidates",
      "que fuentes hay sobre los candidatos",
      "candidates",
      "candidatos",
    ],
    rate: [
      "what is the tax rate",
      "what is the combat tax rate",
      "what is the printed combat sales tax rate",
      "cual es la tasa del impuesto",
      "cual es la tasa de combat",
      "tax rate",
    ],
    duration: [
      "how long would it last",
      "how long would the combat continuation last",
      "cuanto dura",
      "cuanto duraria",
      "duration",
    ],
    effects: [
      "what do yes and no change",
      "what do yes and no change for combat",
      "what does yes mean",
      "what does no mean",
      "que cambian los votos si y no",
      "que cambian si y no para combat",
      "que significa votar si",
      "que significa votar no",
      "yes and no",
    ],
    purpose: [
      "what is combat",
      "what is the purpose of combat",
      "que es combat",
      "combat",
    ],
  };
  const plain = q.replace(/^[¿¡]+|[?!.]+$/g, "");
  for (const [intent, phrases] of Object.entries(aliases))
    if (phrases.includes(plain)) return intent;
  return "unknown";
}
const recipes = {
  effects: ["scope", "effects", "original"],
  rate: ["scope", "facts", "original"],
  duration: ["scope", "facts", "original"],
  purpose: ["scope", "facts", "original"],
  maps: ["scope", "maps", "map_sources"],
  candidates: ["scope", "coverage"],
  unknown: ["scope", "coverage"],
};
export function validateLayout(draft, intent) {
  const expected = recipes[intent] ?? recipes.unknown;
  if (
    !draft ||
    draft.intent !== intent ||
    !Array.isArray(draft.components) ||
    draft.components.length !== expected.length ||
    new Set(draft.components).size !== expected.length ||
    expected.some((id) => !draft.components.includes(id))
  )
    throw Error("layout_unadmitted");
  if (draft.components[0] !== "scope") throw Error("scope_first");
  return immutableCopy({ intent, components: draft.components });
}
export function baselineLayout(intent) {
  return { intent, components: [...(recipes[intent] ?? recipes.unknown)] };
}
const canonical = {
  effects: "what do yes and no change?",
  rate: "what is the tax rate?",
  duration: "how long would it last?",
  purpose: "what is combat?",
};
export async function experienceAnswer(intent, corpus, locale) {
  if (canonical[intent]) return answer(canonical[intent], corpus, locale);
  return {
    status:
      intent === "maps"
        ? "maps"
        : intent === "advice"
          ? "advice_refused"
          : intent === "membership"
            ? "membership_unknown"
            : intent === "candidates"
              ? "coverage_gap"
              : "unsupported",
    claims: [],
    sources: [],
  };
}
export const COPY = Object.freeze({
  en: {
    title: "Understand the ballot. See the evidence.",
    intro:
      "Ask a question, explore the original sources, and make your own choice.",
    sample: "Public-source demonstration · personal ballot not loaded",
    privacy:
      "Do not enter your address, date of birth or private voter records. Your typed text stays in this tab. For supported questions, optional AI checks send only your selected public question category and language, plus public evidence.",
    ask: "What would you like to understand?",
    submit: "Explore",
    reset: "Start over",
    stop: "Stop",
    source: "Original source",
    scope: "What these sources cover",
    scopeText:
      "This retained public sample cannot tell us what is on your personal ballot. Current applicability has not been reverified.",
    choose: "Choose a question or type your own.",
    examples: [
      "What do Yes and No change for COMBAT?",
      "What is the COMBAT tax rate?",
      "Compare Missouri's congressional maps",
      "What candidate evidence is admitted?",
    ],
    gap: "Printed rosters from a public sample and public notices are available. Candidate background evidence remains incomplete. Missing sources do not establish a position.",
    membership:
      "Your personal ballot and district have not been verified. No location is requested or inferred.",
    advice:
      "I can explain sources and wording. I cannot recommend how to vote.",
    translation:
      "Spanish civic wording is awaiting human review. The original English source remains available.",
    voice: "Listen, read and stay in control",
    voiceNote:
      "AI-generated voice. No microphone is active. Prepared speech must match the current language, question and evidence before playback.",
    consent:
      "Allow this page to play a prepared AI voice through this device’s speakers when I select Play.",
    play: "Play prepared reading",
    silent: "Exercise silently",
    speechUnavailable:
      "A matched reading is not prepared for this question. The source remains readable.",
    notReady: "Microphone off · speaker off",
    clear: "Session cleared.",
    mapLimits:
      "Local review only. No population or partisan-impact calculations. Same projection and extent; state-map reuse rights remain unconfirmed.",
    details: "Source and demonstration details",
  },
  es: {
    title: "Comprenda la boleta. Consulte las fuentes.",
    intro:
      "Haga una pregunta, consulte las fuentes originales y tome su propia decisión.",
    sample: "Demostración con fuentes públicas · boleta personal no cargada",
    privacy:
      "No ingrese su dirección, fecha de nacimiento ni datos privados. El texto escrito permanece en esta pestaña. Las revisiones opcionales con IA envían solo la categoría pública elegida, el idioma y las fuentes públicas.",
    ask: "¿Qué desea entender?",
    submit: "Explorar",
    reset: "Empezar de nuevo",
    stop: "Detener",
    source: "Fuente original",
    scope: "Alcance de estas fuentes",
    scopeText:
      "Esta muestra pública guardada no permite saber qué aparece en su boleta personal. No se ha vuelto a verificar su vigencia.",
    choose: "Elija una pregunta o escriba la suya.",
    examples: [
      "¿Qué cambian sí y no para COMBAT?",
      "¿Cuál es la tasa de COMBAT?",
      "Comparar los mapas del Congreso de Missouri",
      "¿Qué fuentes de candidatos están admitidas?",
    ],
    gap: "Están disponibles las listas impresas de una muestra pública y de avisos públicos. Las fuentes de contexto de los candidatos siguen incompletas. La falta de información no representa una postura.",
    membership:
      "No hemos verificado su boleta ni su distrito. No solicitamos ni inferimos su ubicación.",
    advice: "Puedo explicar fuentes y textos. No puedo recomendar cómo votar.",
    translation:
      "El texto cívico en español está pendiente de revisión humana. Puede consultar la fuente original en inglés.",
    voice: "Escuche, lea y mantenga el control",
    voiceNote:
      "Voz generada por IA. El micrófono está apagado. Antes de reproducirse, la lectura debe coincidir con el idioma, la pregunta y las fuentes actuales.",
    consent:
      "Permito que esta página reproduzca una voz de IA en los altavoces de este dispositivo cuando seleccione Reproducir.",
    play: "Reproducir lectura preparada",
    silent: "Probar sin sonido",
    speechUnavailable:
      "No hay una lectura coincidente preparada para esta pregunta. Puede leer la fuente.",
    notReady: "Micrófono apagado · altavoces apagados",
    clear: "Se borró la sesión.",
    mapLimits:
      "Solo revisión local. No se calculan efectos demográficos ni partidistas. La proyección y la vista son iguales; los derechos de reutilización de los mapas estatales no están confirmados.",
    details: "Fuentes y detalles de la demostración",
  },
});
