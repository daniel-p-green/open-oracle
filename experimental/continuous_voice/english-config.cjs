'use strict';
// Startup selection only. Core merges this into its existing guarded configuration.
// The installed Live SDK, not the Realtime voice list, supplies supportedVoices.
function englishVoiceSelection({model, language, supportedVoices}) {
  if (model !== 'gpt-live-1') throw Error('Configured Live model is unverified');
  if (language !== 'en') throw Error('No voice selected for this language');
  if (!Array.isArray(supportedVoices) || !supportedVoices.includes('cedar'))
    throw Error('Cedar support not verified; no fallback selected');
  return Object.freeze({model, language, voice: 'cedar', startup: true});
}
module.exports = {englishVoiceSelection};
