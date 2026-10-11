# Speech release contract — prepared, not verified

Use one accepted application payload for the card, readable text and speech script. It must identify visitor epoch, request, utterance, language, translation status, ordered segments, accepted evidence references and original-language source references. Original wording remains available through Sources. A translation is a separately labelled rendition and must preserve names, numbers, dates, negation and qualifiers.

Text must be visible before its corresponding audio plays and remain readable during playback. Without measured timing, show the whole accepted segment; make no word-synchronization claim. “Speaking” follows actual local playback start/stop callbacks. Generation/transcript events alone do not establish what was heard. Unchecked GPT-Live output stays held. Changing question/language or resetting cancels queued output and invalidates stale captions/audio across both capture and display clients.

Required actual checks: ordinary audible answer versus accepted text/source; translated audible and visible content in the same selected language; text present before playback; stop/reset during sound; stale callback; source gap/conflict; denied microphone/provider failure; keyboard/reflow/reduced motion. Label unplayed text if playback stops. Avoid automatic screen-reader speech over provider audio.

Current result: transport only verified, no microphone or playback, no translation. These criteria are **unrun**. See the design-discovery sibling's speech-text-acceptance.md and runtime-proof-2026-10-10.md. No permission for capture is implied by this document.
