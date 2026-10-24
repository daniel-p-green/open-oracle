import { QUESTION_VERSION } from "./measure-source.mjs";
import { publicJourneyAction } from "./journey-core.mjs";

// Local intent drafting is deliberately bounded. The visitor's words are never
// returned, interpolated into prompts, or treated as evidence. A separate user
// confirmation selects this public operation; this is not a general chatbot.
export function draftPublicIntent(
  text,
  { journeyActive = false, language = "en" } = {},
) {
  if (
    !["en", "es"].includes(language) ||
    typeof text !== "string" ||
    !text.trim() ||
    text.length > 500
  )
    return null;
  let q = text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .trim();
  q = q.replace(/^[¿¡]+|[?!.]+$/g, "").replace(/\s+/g, " ");
  q = q.replace(
    /^(?:please |por favor,? |could you |can you |would you |puede |puedes |me puede |me puedes )/,
    "",
  );
  q = q.replace(/,? (?:please|por favor)$/, "");
  if (
    /\b(ignore|system|override|ignora|sistema|address|direccion|dob|birth|nacimiento|eligible|recommend|recomiend\w*|persuad\w*|best candidate|mejor candidato|should i vote|deberia votar|por quien votar)\b/.test(
      q,
    )
  )
    return null;
  const fixed = (kind, operation, selectedLanguage = language) =>
    Object.freeze({
      kind,
      operation,
      language: selectedLanguage,
      source_version: QUESTION_VERSION,
    });
  const exact = publicJourneyAction(text);
  if (exact) return fixed(exact === "effects" ? "local" : "journey", exact);
  if (
    /^(?:(?:switch|change) (?:to )?|hablar en |cambiar a )(?:spanish|espanol)$/.test(
      q,
    )
  )
    return fixed("language", "language", "es");
  if (
    /^(?:(?:switch|change) (?:to )?|hablar en |cambiar a )(?:english|ingles)$/.test(
      q,
    )
  )
    return fixed("language", "language", "en");
  if (
    /^(?:show (?:me )?(?:the |actual |official )?maps|compare (?:the |official )?maps|mostrar (?:los )?mapas(?: oficiales)?|muestrame los mapas)$/.test(
      q,
    )
  )
    return fixed("local", "maps");
  if (
    /^(?:show (?:me )?(?:the )?candidates|who are the candidates|mostrar (?:los )?candidatos|quienes son los candidatos)$/.test(
      q,
    )
  )
    return fixed("local", "candidates");
  const topic =
    /(?:proposition a|proposicion a|the redistricting question|la pregunta de redistribucion)/;
  if (topic.test(q)) {
    if (
      /^(?:explain |explain what |tell me (?:about|what) |what (?:is|does) |explica |explique |que (?:es|pregunta) )(?:proposition a|proposicion a|the redistricting question|la pregunta de redistribucion)(?: (?:mean|means|ask|asking))?$/.test(
        q,
      )
    )
      return fixed("journey", "brief");
    if (
      /^(?:explain |explain what |explica |explique )(?:proposition a|proposicion a)(?: in (?:plain|simple|simpler) (?:words|language)| con palabras (?:mas )?sencillas)$/.test(
        q,
      )
    )
      return fixed("journey", "simpler");
    return null;
  }
  if (!journeyActive) return null; // Never resolve "it" to an unrelated measure.
  if (
    /^(?:say that (?:more simply|in simpler words)|explain (?:it|that) (?:more simply|in (?:plain|simple|simpler) (?:words|language))|make (?:it|that) simpler|use simpler words|expli(?:ca|que)(?:me|melo|lo)?(?: eso)? con palabras (?:mas )?sencillas)$/.test(
      q,
    )
  )
    return fixed("journey", "simpler");
  if (
    /^(?:tell me more|more detail|explain (?:it|that) in more detail|cuentame mas|mas detalles)$/.test(
      q,
    )
  )
    return fixed("journey", "detail");
  if (
    /^(?:give me (?:a )?(?:short|brief) (?:answer|explanation)|briefly|resumen breve|una explicacion breve)$/.test(
      q,
    )
  )
    return fixed("journey", "brief");
  if (
    /^(?:what (?:do|does) yes and no mean|what changes (?:with|for) yes and no|que significan si y no)$/.test(
      q,
    )
  )
    return fixed("local", "effects");
  if (
    /^(?:show (?:me )?(?:the )?(?:original|source|exact wording)|where does that come from|show me where that comes from|mostrar (?:la )?fuente|de donde viene eso)$/.test(
      q,
    )
  )
    return fixed("local", "source");
  if (
    /^(?:that (?:seems|sounds|looks) wrong|that doesn't (?:sound|look) right|i think that is wrong|eso (?:parece|esta) mal|eso no parece correcto)$/.test(
      q,
    )
  )
    return fixed("local", "challenge");
  if (
    /^(?:what don't we know|what is missing|que no sabemos|que falta)$/.test(q)
  )
    return fixed("journey", "limits");
  if (/^(?:show (?:me )?my recap|recap|mostrar mi resumen|mi resumen)$/.test(q))
    return fixed("local", "recap");
  return null;
}

export function publicIntentLabel(draft, language = "en") {
  const labels = {
    en: {
      overview: "Proposition A · explanation of the question",
      brief: "Proposition A · brief explanation",
      simpler: "Proposition A · simpler wording",
      detail: "Proposition A · more detail",
      limits: "Proposition A · evidence limits",
      effects: "Proposition A · Yes and No",
      maps: "Compare the official maps",
      candidates: "Public sample · candidate roster and evidence gaps",
      source: "Proposition A · original wording",
      challenge: "Withdraw this explanation and check the original",
      recap: "This tab's recap",
      language:
        draft?.language === "es" ? "Switch to Spanish" : "Switch to English",
    },
    es: {
      overview: "Proposición A · explicación de la pregunta",
      brief: "Proposición A · explicación breve",
      simpler: "Proposición A · palabras más sencillas",
      detail: "Proposición A · más detalles",
      limits: "Proposición A · límites de las fuentes",
      effects: "Proposición A · Sí y No",
      maps: "Comparar los mapas oficiales",
      candidates: "Muestra pública · candidatos y fuentes que faltan",
      source: "Proposición A · texto original",
      challenge: "Retirar esta explicación y consultar el original",
      recap: "Resumen de esta pestaña",
      language:
        draft?.language === "es" ? "Cambiar a español" : "Cambiar a inglés",
    },
  };
  return labels[language]?.[draft?.operation] ?? "";
}
