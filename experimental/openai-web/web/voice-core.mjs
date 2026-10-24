import { QUESTION_VERSION, validateJourney } from "./journey-core.mjs";
const STAGES = [
  "connected",
  "listening",
  "input_partial",
  "routing",
  "checked_text",
  "checking_speech",
  "speech_checked",
  "complete",
];
const VIEWS = ["measure", "maps", "limits", "source", "clarify", "abstain"];
export function voiceControlText(view, language) {
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
          "at_ms",
          "view",
          "map_focus",
          "text",
          "result",
          "revision",
          "transcript_state",
          "start_ms",
          "end_ms",
        ].includes(k),
    ) ||
    value.source_version !== QUESTION_VERSION ||
    value.language !== language ||
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
  if (value.stage === "checked_text" && value.result !== null) {
    unit = validateJourney(
      value.result,
      value.result?.unit?.operation,
      language,
    );
    if (value.text !== unit.sections.map((part) => part.text).join(" "))
      throw Error("voice_text_binding");
  }
  if (
    value.stage === "checked_text" &&
    !unit &&
    !["source", "clarify", "abstain"].includes(value.view)
  )
    throw Error("voice_text_without_review");
  if (
    value.stage === "checked_text" &&
    !unit &&
    value.text !== voiceControlText(value.view, language)
  )
    throw Error("voice_control_text");
  return {
    stage: value.stage,
    turn: value.turn,
    revision: value.revision,
    view: value.view,
    mapFocus: value.map_focus,
    unit,
    text:
      value.stage === "checked_text" || value.stage === "input_partial"
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
  return receipt.turns.map((part,index)=>{
    if(part.turn!==index+1||part.source_version!==QUESTION_VERSION||part.language!==language||part.independent_asr_match!==true||
      !/^[a-f0-9]{64}$/.test(part.audio_sha256)||!Number.isFinite(part.audio_seconds)||part.audio_seconds<=0||part.audio_seconds>60||
      !part.checked||Object.keys(part.checked).sort().join()!=="map_focus,result,text,view")throw Error("voice_final_turn");
    return voiceUpdate({...part.checked,stage:"checked_text",turn:part.turn,revision:part.turn,source_version:QUESTION_VERSION,
      language,at_ms:part.ready_at_ms},language,0,0);
  });
}
