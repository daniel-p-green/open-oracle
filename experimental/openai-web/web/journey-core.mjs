import { immutableCopy } from "./core.mjs";
import { QUESTION_VERSION } from "./measure-source.mjs";
export { QUESTION_VERSION };
export const OPERATIONS = ["brief", "overview", "simpler", "detail", "limits"];

// The current privacy contract permits explicit public categories only. Local
// free text never becomes a model prompt merely because it passed a regex.
export function publicJourneyAction(question) {
  if (typeof question !== "string" || question.length > 500) return null;
  const q = question
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim()
    .replace(/^[¿¡]+|[?!.]+$/g, "");
  const aliases = {
    overview: [
      "what is proposition a asking",
      "explain the redistricting question",
      "que pregunta la proposicion a",
    ],
    effects: [
      "what do yes and no mean for proposition a",
      "que significan si y no en la proposicion a",
    ],
    simpler: [
      "explain proposition a in simpler words",
      "explique la proposicion a con palabras mas sencillas",
    ],
    limits: [
      "does proposition a tell me my district",
      "la proposicion a indica mi distrito",
    ],
  };
  return (
    Object.entries(aliases).find(([, phrases]) => phrases.includes(q))?.[0] ??
    null
  );
}

export function validateJourney(
  result,
  operation,
  language,
  displayedVersion = QUESTION_VERSION,
) {
  const critical = [
    "entailed",
    "no_additions",
    "polarity_safe",
    "language_match",
    ...(["brief", "overview", "limits"].includes(operation)
      ? ["request_fit"]
      : []),
  ].sort();
  const advisory = [
    "attributed",
    ...(["simpler", "detail"].includes(operation) ? ["request_fit"] : []),
  ].sort();
  if (
    !OPERATIONS.includes(operation) ||
    !["en", "es"].includes(language) ||
    result?.source_version !== displayedVersion ||
    displayedVersion !== QUESTION_VERSION ||
    result?.mode !== "fresh_grounded_generation" ||
    result?.raw_visitor_input_sent !== false ||
    result?.playback_enabled !== false ||
    !["confirmed", "unconfirmed"].includes(result?.request_fit) ||
    JSON.stringify(result?.review_contract?.critical) !==
      JSON.stringify(critical) ||
    JSON.stringify(result?.review_contract?.advisory) !==
      JSON.stringify(advisory)
  )
    throw Error("journey_envelope");
  const unit = result.unit,
    ids =
      operation === "effects"
        ? ["yes", "no"]
        : operation === "limits"
          ? ["limits"]
          : ["question"];
  if (
    unit?.operation !== operation ||
    unit?.language !== language ||
    !Array.isArray(unit.sections) ||
    unit.sections.length !== ids.length
  )
    throw Error("journey_binding");
  for (const [index, part] of unit.sections.entries()) {
    if (
      !part ||
      Object.keys(part).sort().join() !== "source_id,text" ||
      part.source_id !== ids[index] ||
      typeof part.text !== "string" ||
      !part.text.trim() ||
      part.text.length > (operation === "brief" ? 260 : 700) ||
      /[<>]|https?:\/\/|www\./i.test(part.text)
    )
      throw Error("journey_section");
  }
  // Provider-returned sources/URLs never establish browser citation authority.
  return immutableCopy({
    ...unit,
    source_version: displayedVersion,
    request_fit: result.request_fit,
  });
}

export function journeyHeading(unit, language) {
  if (
    unit.request_fit === "unconfirmed" &&
    ["simpler", "detail"].includes(unit.operation)
  )
    return language === "es"
      ? unit.operation === "simpler"
        ? "Explicación · palabras más sencillas no confirmadas"
        : "Explicación · nivel de detalle no confirmado"
      : unit.operation === "simpler"
        ? "Explanation · simpler wording not confirmed"
        : "Explanation · requested detail not confirmed";
  return language === "es"
    ? "Explicación de la pregunta"
    : "Explanation of the question";
}

export function recapUnits(units, language) {
  return units
    .filter(
      (u) => u.language === language && u.source_version === QUESTION_VERSION,
    )
    .slice(-4)
    .map((u) => ({
      operation: u.operation,
      sections: u.sections,
      request_fit: u.request_fit,
    }));
}

export function journeyReading(unit) {
  const es = unit.language === "es";
  const notice = es
    ? "Explicación por IA, revisión humana pendiente."
    : "AI explanation, human review pending.";
  const label = es
    ? "Explicación del texto de la pregunta, no es una cita."
    : "Explanation of the ballot wording, not a quotation.";
  const quality =
    unit.request_fit === "unconfirmed"
      ? [
          es
            ? "El nivel de sencillez o detalle solicitado no está confirmado."
            : "The requested simplicity or detail is unconfirmed.",
        ]
      : [];
  return [
    notice,
    es
      ? "Esta muestra pública no verifica su boleta ni su distrito."
      : "This public sample does not verify your ballot or district.",
    label,
    ...quality,
    ...unit.sections.map((p) => p.text),
  ].join(" ");
}

export function validateJourneySpeech(value, unit, job) {
  const text = journeyReading(unit);
  if (
    value?.mode !== "fresh_checked_speech" ||
    value.source_version !== QUESTION_VERSION ||
    value.language !== unit.language ||
    value.reading !== text ||
    value.independent_asr_match !== true ||
    value.finalized !== true ||
    value.asr_model !== "gpt-transcribe" ||
    value.acoustic_human_review !== false ||
    value.raw_visitor_input_sent !== false ||
    value.playback_enabled !== false ||
    !/^[a-f0-9]{64}$/.test(value.sha256) ||
    !Number.isInteger(value.bytes) ||
    value.bytes < 44 ||
    value.bytes > 60 * 48000 + 44 ||
    !Number.isFinite(value.duration_seconds) ||
    value.duration_seconds <= 0 ||
    value.duration_seconds > 60 ||
    Math.abs(value.duration_seconds - (value.bytes - 44) / 48000) > 0.000001 ||
    !Number.isFinite(job?.expiresInSeconds) ||
    job.expiresInSeconds <= 0 ||
    job.expiresInSeconds > 120 ||
    !/^[a-zA-Z0-9_-]{16,64}$/.test(job.requestId)
  )
    throw Error("speech_binding");
  return immutableCopy({
    asset: {
      id: job.requestId,
      kind: "fresh_checked_voice",
      release_policy: "review_only",
      locale: unit.language,
      text,
      source_version: QUESTION_VERSION,
      sha256: value.sha256,
      bytes: value.bytes,
      independent_asr_match: true,
      duration_seconds: value.duration_seconds,
    },
    expiresAt: Date.now() + job.expiresInSeconds * 1000,
  });
}
