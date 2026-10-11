# Isolated continuous voice interface — core and language adapter seam

Core owns canonical import, endpoints, consent, provider orchestration and cancellation.
These files are a prototype in task-6, not replacements already imported into the app.
No GUI, recording, speaker output, paid call, uploader or gesture producer is included.

## Identity and normalized events

Base ticket: `{epoch, generation, turn_id, transcript_id, request_id}`.
Released ticket also has unique `{release_id, speech_id, playback_id}` minted by backend.
Capture lease: `{epoch, generation, capture_id}`; every capture opening has a new ID.
Epoch fences Erase/session replacement; generation fences Stop/Resume/interruption and
any source/document/language/recognition revision. IDs correlate; they do not authorize.

`inputDelta({epoch,generation,capture_id,text}, lease)` is local preview only.
`inputFinal({epoch,generation,capture_id,transcript_id,text,finality}, lease)` is an
APPLICATION adapter event. It is not an OpenAI `transcript.done` event. Both client
`verifyFinal` and server `finalize(snapshot,ticket)` must validate actual finality and
identity bindings. Missing adapters fail closed. Synthetic adapters are tests only.
GPT-Live input/output deltas, delegation offsets and silence timers are not finality.

## Adapter API (client.cjs)

| Method | Contract |
| --- | --- |
| `control('listen', context, signal)` | Serialized backend ack returning matching `{epoch,generation}` before capture; bind deliberate Start/Resume on server. |
| `settleEcho(context, signal)` | `true` only when capture can safely reopen. Fake proof in simulations; actual acoustic proof unrun. |
| `openCapture(lease, {delta,final}, signal)` | Promise of cancellable `{close()}`; close delayed permission results after invalidation. No capture while work/playback is active. |
| `verifyFinal(event, lease)` | Trusted finalized-input adapter; no delta/delegation/timer heuristic. Recognition language/revision belong here. |
| `ask({ticket,question,finality}, signal)` | One canonical source/review-gated request, returns `{ticket:releasedTicket,result}`. Drafts never enter the speech route. |
| `render(releasedTicket, signal)` | Identity only to server. Server revalidates accepted speech before and after its bounded renderer; returns fully closed/acknowledged/transcript-matched PCM16 mono24k WAV decoded to `Uint8Array` in `audio`, plus identity/text/language/report/usage. |
| `play(media,ticket,{started,ended,failed},signal)` | Synchronous cancellable `{cancel()}`; callbacks reflect actual player events, never inferred from generation or elapsed time. |
| `complete(ticket,signal)` | Ack playback completion once; next capture waits for this ack and echo settling. This ack is a client event, not evidence of provider/device audibility. |
| `invalidate(context,state)` | Queue ordered control with HTTP work/renderer cancellation. Local cancellation occurs immediately even if ack is delayed. |
| `erase(context)` | Queue after old-epoch invalidation, bind new epoch to canonical visitor session and clear server state; no provider deletion promise. |
| `clearDocument(opaqueDocumentRef)` | Intake owner clears its bytes/previews/object URLs. Prototype drops its ref; it cannot prove cleanup of an unimplemented uploader. |

Control messages must be serialized. A failed/out-of-order/missing ack cannot enable
capture. Default limits: two attempts per epoch (configurable 2..8), one active turn,
180s client/server conversation, 30s client listening, 5s client settling/control,
75s research/render/play. The trusted core must preserve a global spending ledger
across epochs; Erase is not authorization to reset spending or increase allowances.
Attempts survive Stop/Resume. No automatic paid retry. Backend turn watchdog must be
scheduled by the core host. Existing renderer separately imposes its 65s process cap.

## Language owner boundary

Use these identifiers rather than introducing another audio controller. Explicit
language choice, correction of recognition, mixed-language routing or document/source
revision must synchronously call `stop()` (or equivalent core cancellation preserving
content), transmit its new generation and wait for acknowledged deliberate Resume.
It must invalidate buffered/player output before updating locale/language revisions.
Carry locale/recognition/translation revision metadata in the app-owned adapter and
validate it on both sides; this prototype does not treat language detection as consent.
An old accepted text can remain marked in its original language after Stop; it cannot
authorize speech for the new revision. Original-source and translated-display checks
remain separate. English canonical gates currently accept only `en/not_requested`;
they must not be weakened to admit an unchecked translation.

English Cedar is selected by Daniel. Other-language voices remain unselected and must
fail closed. The staged English selection is SDK-verified for GPT-Live; audible/provider
acceptance is unrun. No language-registry files or canonical speech/release code are
modified by this prototype.

## Existing core hooks

Reuse `open_oracle.session_control.accepted_speech` and `operation` on server;
reuse `web/live.js` `speechContract`/`speechWords` for client structural checks;
reuse `scripts/live-ws/ws-buffer.cjs` for closed output validation, and the existing
`ws_speech.render_speech(contract,cancel)` behind a reviewed adapter (not called here).
Do not attach the conversational model's remote track to speakers. Each approved
answer can use a separately closed speech-render session within one logical
conversation; latency, capture-session reuse and spending remain acceptance gates.
This is a conservative simulation against the existing closed-render gate, not a
completed persistent GPT-Live full duplex protocol. Candidate audio and transcript
must be buffered and bound to a checked answer before release. Live commentary can
paraphrase, and an append acknowledgement proves neither speech completion nor exact
audible wording; instructions alone cannot guarantee it. See the official
[delegation guide](https://developers.openai.com/api/docs/guides/live-delegation) and
[playback controls](https://developers.openai.com/api/docs/guides/voice-server-controls).
Do not map Stop to `VisitorSessions.erase`: that tombstones the session and deletes
context. Erase must call canonical erase and rotate session/epoch. Existing one-voice
server allowance, research `speech=False` and disabled voice flags remain unchanged.

Explicit Start is the only activation here. Wave producer/arming decisions remain
with their canonical owner. Upload/intake and visual components remain core-owned.
