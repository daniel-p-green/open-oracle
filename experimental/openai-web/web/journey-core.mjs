import { immutableCopy } from "./core.mjs";
import { QUESTION_VERSION } from "./measure-source.mjs";
export { QUESTION_VERSION };
export const OPERATIONS = ["overview", "simpler", "detail", "limits"];

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
    ...(["overview", "limits"].includes(operation) ? ["request_fit"] : []),
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
      part.text.length > 700 ||
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
