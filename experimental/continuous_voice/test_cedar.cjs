'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {englishVoiceSelection} = require('./english-config.cjs');
const root = process.env.OPEN_ORACLE_ROOT;
assert(root, 'OPEN_ORACLE_ROOT required');
const sdk = process.env.OPEN_ORACLE_NODE_DEPENDENCIES || '/opt/homebrew/lib/node_modules/promptfoo/node_modules';
const declarations = fs.readFileSync(path.join(sdk, 'openai/resources/live/live.d.ts'), 'utf8');
const literal = declarations.match(/export type BuiltInVoice = ([^;]+);/)[1];
const voices = [...literal.matchAll(/'([^']+)'/g)].map(m => m[1]);
const {speechSession} = require(path.join(root, 'scripts/live-ws/ws-speech.cjs'));

test('installed Live SDK lists Cedar for actual gpt-live-1 SessionConfig', () => {
  assert(voices.includes('cedar'));
  const config = declarations.slice(declarations.indexOf('export interface SessionConfig {'));
  assert(config.includes("model: (string & {}) | 'gpt-live-1'"));
  assert(config.includes('voice?: string | LiveAPI.BuiltInVoice | LiveAPI.CustomVoice'));
  assert.equal(englishVoiceSelection({model: 'gpt-live-1', language: 'en', supportedVoices: voices}).voice, 'cedar');
});
test('actual core speechSession startup seam selects Cedar without invoking renderer', () => {
  for (let i = 0; i < 2; i++) {
    const session = speechSession();
    assert.equal(session.model, 'gpt-live-1'); assert.equal(session.audio.output.voice, 'cedar');
    assert.equal(session.audio.format.rate, 24000); assert.equal(session.store, false);
    assert.equal(session.delegation.type, 'client'); assert(session.instructions.includes('withheld'));
  }
});
test('unverified voice/model or other language never silently substitutes', () => {
  for (const input of [{model: 'gpt-live-1', language: 'en', supportedVoices: ['marin']},
    {model: 'gpt-live-1', language: 'es', supportedVoices: voices},
    {model: 'other-model', language: 'en', supportedVoices: voices}])
    assert.throws(() => englishVoiceSelection(input));
});
