import test from "node:test";
import assert from "node:assert/strict";
import { voiceUpdate, voiceFinalTurns, voiceControlText } from "../web/voice-core.mjs";
import { QUESTION_VERSION } from "../web/journey-core.mjs";

test("native voice view events require the current source, language, turn and checked text before display", () => {
  const event = {
    stage: "routing",
    turn: 1,
    revision: 2,
    source_version: QUESTION_VERSION,
    language: "en",
    at_ms: 100,
    view: "maps",
    map_focus: "kansas_city",
  };
  assert.equal(voiceUpdate(event, "en", 1, 1).mapFocus, "kansas_city");
  for (const mutation of [
    { revision: 1 },
    { turn: 0 },
    { turn: 4 },
    { language: "es" },
    { source_version: "foreign" },
    { view: "candidate_ranking" },
    { view: "measure" },
    { html: "<script>" },
  ])
    assert.throws(() => voiceUpdate({ ...event, ...mutation }, "en", 1, 1));
  const switched={...event,session_language:"en",language:"es"};
  assert.equal(voiceUpdate(switched,"en",1,1).language,"es");
  assert.throws(()=>voiceUpdate({...switched,session_language:"es"},"en",1,1),/binding/);
  assert.throws(()=>voiceUpdate({...switched,language:"unknown"},"en",1,1),/binding/);
  const checked = {
    ...event,
    stage: "checked_text",
    view: "measure",
    map_focus: "unchanged",
    text: "unreviewed",
    result: null,
  };
  assert.throws(() => voiceUpdate(checked, "en", 1, 1), /without_review/);
  assert.equal(
    voiceUpdate(
      {
        ...checked,
        view: "clarify",
        text: "Please name the public election question you want to understand.",
      },
      "en",
      1,
      1,
    ).unit,
    null,
  );
  assert.throws(
    () => voiceUpdate({ ...checked, view: "clarify" }, "en", 1, 1),
    /control_text/,
  );
  const navigation = {...checked, view:"maps", map_focus:"kansas_city", text:voiceControlText("maps","en","kansas_city")};
  assert.equal(voiceUpdate(navigation,"en",1,1).text,navigation.text);
  assert.throws(()=>voiceUpdate({...navigation,text:"District boundaries moved north."},"en",1,1),/control_text/);
  assert.throws(()=>voiceUpdate({...navigation,map_focus:"st_louis"},"en",1,1),/control_text/);
  const partial = {
    ...event,
    stage: "input_partial",
    text: "Could you show the maps?",
    transcript_state: "provisional",
    start_ms: 0,
    end_ms: 100,
  };
  assert.equal(voiceUpdate(partial, "en", 1, 1).text, partial.text);
  assert.throws(
    () => voiceUpdate({ ...partial, transcript_state: "final" }, "en", 1, 1),
    /transcript_binding/,
  );
  const finalInput={...event,stage:"input_final",text:"Could you show the official source?",transcript_state:"final",
    input_audio_sha256:"b".repeat(64),transcript_origin:"independent_bounded_input_asr"};
  assert.equal(voiceUpdate(finalInput,"en",1,1).text,finalInput.text);
  for (const change of [{transcript_state:"provisional"},{transcript_origin:"arrival_guess"},{input_audio_sha256:"bad"},{text:""}])
    assert.throws(()=>voiceUpdate({...finalInput,...change},"en",1,1),/input_final_binding/);
  assert.throws(
    () => voiceUpdate({ ...partial, start_ms: 200 }, "en", 1, 1),
    /transcript_binding/,
  );
});

test("a slow poll recovers every final checked caption from the complete receipt", () => {
  const receipt = {
    mode: "native_live_public_synthetic", source_version: QUESTION_VERSION,
    language: "en", all_turns_checked: true, finalized: true,
    close_reason: "close_requested", errors: [],
    turns: [1,2].map(turn => ({
      turn, source_version: QUESTION_VERSION, language: "en",
      independent_asr_match: true, audio_sha256: "a".repeat(64),
      audio_seconds: 2, ready_at_ms: turn*4000,
      checked: { view: "source", map_focus: "unchanged", result: null,
        text: voiceControlText("source", "en") },
    })),
  };
  receipt.inputs=[{turn:1,language:"en",text:"Show the source.",input_audio_sha256:"b".repeat(64),transcript_origin:"independent_bounded_input_asr"}];
  assert.deepEqual(voiceFinalTurns(receipt,"en").map(part=>part.turn),[1,2]);
  assert.equal(voiceFinalTurns(receipt,"en")[0].inputText,"Show the source.");
  assert.equal(voiceFinalTurns(receipt,"en")[1].inputText,null);
  const switched=structuredClone(receipt);
  switched.turns[1].language="es";
  switched.turns[1].checked.text=voiceControlText("source","es");
  assert.deepEqual(voiceFinalTurns(switched,"en").map(x=>x.language),["en","es"]);
  assert.equal(voiceFinalTurns(switched,"en")[0].inputLanguage,"en");
  const back=structuredClone(receipt.turns[0]);back.turn=3;back.ready_at_ms=12000;
  switched.turns.push(back);
  assert.deepEqual(voiceFinalTurns(switched,"en").map(x=>x.language),["en","es","en"]);
  const extra=structuredClone(back);extra.turn=4;switched.turns.push(extra);
  assert.throws(()=>voiceFinalTurns(switched,"en"),/final_receipt/);
  for (const mutate of [
    value=>{value.inputs.push(value.inputs[0])},
    value=>{value.inputs[0].language="unknown"},
    value=>{value.errors=["late_audio"]},
    value=>{value.turns[1].turn=1},
    value=>{value.turns[1].source_version="foreign"},
    value=>{value.turns[1].independent_asr_match=false},
    value=>{value.turns[1].checked.text="An unchecked factual assertion"},
  ]) {
    const bad=structuredClone(receipt);mutate(bad);
    assert.throws(()=>voiceFinalTurns(bad,"en"));
  }
});
