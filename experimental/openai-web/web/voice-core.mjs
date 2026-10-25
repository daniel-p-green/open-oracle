import { QUESTION_VERSION, validateJourney } from "./journey-core.mjs";
const STAGES = [
  "connected",
  "listening",
  "input_partial",
  "input_final",
  "input_unavailable",
  "routing",
  "checked_text",
  "checking_speech",
  "speech_checked",
  "complete",
];
const VIEWS = ["measure", "maps", "limits", "source", "clarify", "abstain"];
export function voiceControlText(view, language, focus = "unchanged") {
  const copy =
    language === "es"
      ? {
          clarify: "Indique la pregunta pública que desea comprender.",
          abstain:
            "Puedo explicar esta pregunta pública, pero no recomendar cómo votar ni verificar su boleta personal.",
          source:
            "El texto oficial completo está disponible con su fuente en pantalla.",
        }
      : {
          clarify:
            "Please name the public election question you want to understand.",
          abstain:
            "I can explain this public question, but cannot recommend a vote or verify your personal ballot.",
          source:
            "The complete official wording is available with its source on screen.",
        };
  if (view === "maps") {
    const regions = language === "es"
      ? {statewide:"en todo Missouri",kansas_city:"del área de Kansas City",st_louis:"del área de St. Louis",unchanged:"en la misma vista"}
      : {statewide:"across Missouri",kansas_city:"around Kansas City",st_louis:"around St. Louis",unchanged:"in the same view"};
    if (!Object.hasOwn(regions,focus)) return null;
    return language === "es"
      ? "Comparemos ambos planes "+regions[focus]+". Esto no determina su distrito."
      : "Let’s compare both plans "+regions[focus]+". This does not determine your district.";
  }
  return copy[view] ?? null;
}
export function voiceUpdate(value, language, revision, turn) {
  if (
    !value ||
    Object.keys(value).some(
      (k) =>
        ![
          "stage",
          "turn",
          "source_version",
          "language",
          "session_language",
          "at_ms",
          "view",
          "map_focus",
          "text",
          "result",
          "revision",
          "transcript_state",
          "input_audio_sha256",
          "transcript_origin",
          "start_ms",
          "end_ms",
        ].includes(k),
    ) ||
    value.source_version !== QUESTION_VERSION ||
    (value.session_language === undefined ? value.language !== language :
      value.session_language !== language || !["en","es"].includes(value.language)) ||
    !STAGES.includes(value.stage) ||
    !Number.isInteger(value.revision) ||
    value.revision <= revision ||
    !Number.isInteger(value.turn) ||
    value.turn < turn ||
    value.turn > 2 ||
    value.turn < (value.stage === "connected" ? 0 : 1) ||
    !Number.isFinite(value.at_ms) ||
    value.at_ms < 0 ||
    value.at_ms > 120000
  )
    throw Error("voice_update_binding");
  if (
    ["routing", "checked_text"].includes(value.stage) &&
    (!VIEWS.includes(value.view) ||
      !["statewide", "kansas_city", "st_louis", "unchanged"].includes(
        value.map_focus,
      ) ||
      (value.view !== "maps" && value.map_focus !== "unchanged"))
  )
    throw Error("voice_view_unadmitted");
  let unit = null;
  if (
    value.stage === "input_partial" &&
    (value.transcript_state !== "provisional" ||
      typeof value.text !== "string" ||
      value.text.length > 500 ||
      !Number.isFinite(value.start_ms) ||
      !Number.isFinite(value.end_ms) ||
      value.start_ms < 0 ||
      value.end_ms > 120000 ||
      value.end_ms < value.start_ms)
  )
    throw Error("voice_transcript_binding");
  if (value.stage === "input_final" &&
      (value.transcript_state !== "final" || value.transcript_origin !== "independent_bounded_input_asr" ||
       !/^[a-f0-9]{64}$/.test(value.input_audio_sha256) || typeof value.text !== "string" ||
       !value.text.trim() || value.text.length > 500)) throw Error("voice_input_final_binding");
  if (value.stage === "checked_text" && value.result !== null) {
    unit = validateJourney(
      value.result,
      value.result?.unit?.operation,
      value.language,
    );
    if (value.text !== unit.sections.map((part) => part.text).join(" "))
      throw Error("voice_text_binding");
  }
  if (
    value.stage === "checked_text" &&
    !unit &&
    !["source", "clarify", "abstain", "maps"].includes(value.view)
  )
    throw Error("voice_text_without_review");
  if (
    value.stage === "checked_text" &&
    !unit &&
    value.text !== voiceControlText(value.view, value.language, value.map_focus)
  )
    throw Error("voice_control_text");
  return {
    language: value.language,
    stage: value.stage,
    turn: value.turn,
    revision: value.revision,
    view: value.view,
    mapFocus: value.map_focus,
    unit,
    text:
      ["checked_text", "input_partial", "input_final"].includes(value.stage)
        ? value.text
        : null,
  };
}

// Ready carries canonical checked turns. A slow poll cannot turn an incomplete
// event history into a claim that every final caption was delivered.
export function voiceFinalTurns(receipt,language){
  if(receipt?.mode!=="native_live_public_synthetic"||receipt.source_version!==QUESTION_VERSION||receipt.language!==language||
    receipt.all_turns_checked!==true||receipt.finalized!==true||receipt.close_reason!=="close_requested"||
    !Array.isArray(receipt.errors)||receipt.errors.length||!Array.isArray(receipt.turns)||receipt.turns.length<1||receipt.turns.length>2)
    throw Error("voice_final_receipt");
  const inputs = receipt.inputs ?? [];
  if (!Array.isArray(inputs) || inputs.length > receipt.turns.length ||
      new Set(inputs.map(item=>item?.turn)).size !== inputs.length || inputs.some(item=>
        !item || !Number.isInteger(item.turn) || item.turn < 1 || item.turn > receipt.turns.length ||
        !["en","es"].includes(item.language) || item.transcript_origin !== "independent_bounded_input_asr" ||
        !/^[a-f0-9]{64}$/.test(item.input_audio_sha256) || typeof item.text !== "string" ||
        !item.text.trim() || item.text.length > 500)) throw Error("voice_final_input");
  return receipt.turns.map((part,index)=>{
    if(part.turn!==index+1||part.source_version!==QUESTION_VERSION||!["en","es"].includes(part.language)||part.independent_asr_match!==true||
      !/^[a-f0-9]{64}$/.test(part.audio_sha256)||!Number.isFinite(part.audio_seconds)||part.audio_seconds<=0||part.audio_seconds>60||
      !part.checked||Object.keys(part.checked).sort().join()!=="map_focus,result,text,view")throw Error("voice_final_turn");
    const action = voiceUpdate({...part.checked,stage:"checked_text",turn:part.turn,revision:part.turn,source_version:QUESTION_VERSION,
      session_language:language,language:part.language,at_ms:part.ready_at_ms},language,0,0);
    return {...action, inputText: inputs.find(item=>item.turn===part.turn)?.text ?? null, inputLanguage: inputs.find(item=>item.turn===part.turn)?.language ?? null};
  });
}
