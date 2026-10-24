# Adversarial Opus review — October24,2026

**Actual review returned: not ready.** Existing [Claude conversation](https://claude.ai/chat/4c378210-7251-4026-9a90-700a23bc34d3),
Message35 submission/Message36 response. UI explicitly selected **Opus5.5High**
before submission and after return. The model cannot inspect its own effort
setting; High was observed in the interface. Reviewer read supplied source only,
ran no tests and used no computer/browser tools. No concept praise counted as
implementation evidence.

Immutable reviewed commit `57fd509bd5caa062bb8c6989589e2f5ea2e2def0`.
Allowlisted source/instructions/evidence bundle297,774bytes,
SHA256 `911bd678edb01c6a79c71c52c2cc7f68f62899b17acdb5fc3aacf433efb5ec38`.
23 tracked project files plus original verified stretch PRD. No credentials,
account IDs, operational ledger, unrelated files or raw human recordings.
Current failures, held native receipts, replay limitations and all remaining
acceptance rows were supplied. Only one adversarial submission was made; earlier
source reviews were already terminal.

| ID / reviewer severity | Concrete finding / reproduction | Disposition and actual evidence |
| --- | --- | --- |
| D1 Medium, code defect | `voice.mjs stop(true)` loses the completed request ID when `layout-client.mjs` cleanup calls onRequest(null); ready `Jobs.public` still serves retained captions. Finish then Erase. | Keep owned completed ID/token, invoke shared cancelProviderJob on Stop/Erase, fence stale callbacks. Async transport-after-ready revocation proof passes; existing server test verifies completed-row updates/result deletion. Fresh actual-browser outcome remains unverified. Failed network cannot promise remote/provider deletion. |
| D2 Low–Medium, code defect | Stop after a finalized run unconditionally sets spokenHeld and overwrites status. | Only pending request/checked_text can create a new held state. Final captions remain final. Independent read-only review closed the logic; current browser unavailable, so no visual pass claim. |
| D3 Medium, missing capability; runtime choice is hypothesis | Native delivery enum has no repeat, so an explicit repeat cannot select reuse; probable re-generation outcome is unmeasured. | Add repeat for the active session's last independently ASR-checked payload. Bind its previous view before routing; no new Responses/review, same independent buffered speech gate. Actual offline two-turn protocol proof generates/reviews once and repeats the identical payload through a second ASR check. No live repeat claim. |
| D4 Medium, acknowledged code mismatch | `answer()` sends maps through generic journey delivery, so speech re-explains the measure rather than its map view. | Open. Next implementation needs source-bound map context, not invented map facts or a prerecorded substantive answer. Not silently described as fixed. |
| D5 Low, dead branch | load_question already raises on hash changes, so text_sha256-is-None branch is unreachable. | Direct load_question recheck with accurate comment. Existing hash/ASR protocol guards preserved. |
| G1 High, demonstrated gap | Four newest trials: no usable command echo, zero bound input deltas. | Input remains unavailable. Did not adopt phase-only arrival binding: a delayed prior-turn fragment can cross that window. Prefer explicit turn-addressable public-input transcription or documented verified protocol correlation; not implemented/live-proven. |
| G2 High, measured architecture limitation | Earlier accepted196char audio consumed12.9s; checked text→accepted segment14.42s. Whole-waveform ASR imposes serial delay. | Retain independent pre-hearing gate. Rejected incremental release based solely on Live's own transcript because it weakens that gate. Sentence/claim-bound independently checked chunks or a disclosed synthesis comparison need implementation/evaluation; no new paid run. |
| G3 Medium, missing capability | Loop language fixed; UI switch Erases session. | Open: preserve a validated per-turn translation/context transition before claiming natural language switching. |
| G4 Medium, missing live evidence | Shared brief definition postdates all4 package trials. | Added narrow deterministic approval+legislative-origin omission backstop alongside existing attribution/congressional/length/fragment guards. Thresholds unchanged; latest live effect unmeasured. |
| H1 Hypothesis | Discarded pre-approval bytes may be silence or spontaneous voice. | Add bytes-above-existing-amplitude-threshold counter, prove fixture discard; it is not a speech-recognition/human-audibility measure. Historical data cannot be retroactively classified. |
| H2 Hypothesis | Essential update ceiling might reject a richer successful run. | No reproduced overflow; keep bounded ceiling until a real event sequence justifies change. New offline repeat sequence passes. |
| H3 Hypothesis | Natural Spanish complete briefs may exceed120. | Do not expand accepted bounds from speculation. Current Spanish failure preceded those checks; civic/latency evaluation still needed. |

**Correction to review arithmetic:** its G2 text labels newest trial4/6 outputs
“checked text.” Both held before any checked_text event. Their numeric
input-end→review-return intervals describe processing of held drafts, not useful
validated text latency. The earlier trial2 accepted-audio timing is real;
no new safe-audio latency improvement was measured. The review's two-option
latency framing is not an exhaustive architecture comparison.

Remaining original stretch gates include natural teach-back/adaptation, pace,
real cancellation/recovery, private-safe human input, protected public entry,
second individual ballot style/candidate admission, bilingual/assistive-device
review and uninterrupted real demonstration evidence. No independent reviewer
can establish these from source inspection. The finite matrix owns closure.


## Targeted Message38 returned on immutable104c7db

Opus5.5High visibly verified; source-only review, no execution. Bundle82,883bytes,
SHA2569f9a18c012a813740866fc9dea0c33d6f3933328af6a9b321e862ff101b562e8.
Reviewer explicitly withdrew its mislabeled checked-text latency claim.

| Finding | Latest local disposition |
| --- | --- |
| N1 Medium: approval/legislature regex misses aprueban/legisladores/lawmakers | Corrected exact stems/terms; natural Spanish positive cases pass. This new post-trial regression was not the cause of historical Spanish trial5. Semantic review unchanged. |
| L1 Low: failed revoke forgotten | Shared transport now owns an opaque revocation lease: failed cleanup retained, concurrent cleanup coalesced, deliberate Erase retries, no automatic retry. New run waits for confirmed prior cleanup. UI reports local versus unconfirmed server cleanup. Test exercises the exact helper wired into voice.mjs, including stale callback and failed-then-successful erase. |
| L2 Low: first-turn repeat ends session | Route to bounded clarification when no session-owned checked answer exists. Offline protocol verifies clarification through existing audio gate, no fresh factual generation. |
| L3 Low: map repeat resets highlight | Reuse already validated current map for unchanged/matching region; repeat carries the original checked region so exact navigation wording still binds. Existing map expiry/source controls stay owned by that view. Browser interaction remains unverified. |
| L4 Low: overstatement | Counter renamed discarded_chunks_with_energy_bytes (whole chunk with any sample above64). Source comment says fixture pin/embedded text hash, not original PDF. Status now says no checked audio available rather than claiming a nonexistent answer was held. |
| Missing UI wiring proof | Exact shared revocation helper is tested; current DOM Stop/failure-label/map highlight behavior still needs permitted browser QA. No static/helper test presented as that proof. |

An independent read-only review found successful Stop cleanup left Run disabled
because a preservation branch returned early. Fixed availability update before
that branch; no caption/source deletion just to recover the button.

D4 next local repair is intentionally narrow: show-maps receives an exact
application-owned navigation acknowledgment keyed to requested region and
language. It no longer generates an unrelated measure explanation. Client
accepts only the exact matching navigation text with null substantive result;
forged geographic claims or mismatched region text hold. No current-map/legal
fact or district assignment is generated. Actual map evidence remains the
separately validated official geometry/PDF view. Substantive geographic analysis
is unsupported; this does not close full conversational map interpretation.
Offline protocol covers map→exact repeat; no live/browser parity claim.


## Message40 returned on immutable21a5e55

Opus5.5High visibly selected; source-only follow-up. Bundle84,466bytes,
SHAbdc9d98eed9b16b39d525dd8e6b69009574d57c0469ccd4c9171d1096882fcbb.
Verdict: repairs hold in substance; no unsafe release path found by inspection.
This is not runtime or whole-product acceptance. Remaining findings:

- **R1 Medium hypothesis:** St./Saint Louis ASR spelling could hold. Added one
  closed proper-name equivalence to existing words normalization; exact alias
  proof passes and unrelated place/negation distinctions remain. No native
  St.Louis pronunciation/ASR success claim.
- **R2 Medium–Low proven:** expired owner made cleanup impossible indefinitely.
  Accept only authenticated local HTTP409 with exact owner_unavailable as already
  expired/cleared; every other failure stays unconfirmed. Same shared lease test
  covers expired owner versus busy/unexpected-origin; no generic409 bypass.
- **R3 Low:** brief lexical backstop can find the legislature's approval rather
  than voters'. Kept/documented as an omission backstop, never semantic proof.
  Unchanged independent entailment/polarity/request-fit checks still required;
  no new brittle voter-word constraint introduced.
- **R4 Low:** first maps/unchanged said same view before one existed. Resolve
  first/unmapped navigation to statewide, then exact speech/UI region binding;
  offline protocol case passes. Existing map-repeat behavior preserved.
- **R5 Low:** language-change button could look enabled during failed cleanup.
  All availability assignments now consider retained cleanup; guarded startup
  still requires successful revocation. Current DOM proof remains missing.
- Spanish statewide navigation uses en todo Missouri; human bilingual civic/
  acoustic review remains required. Current UI wiring/highlight/native choices,
  input captions and latency still need actual permitted end-to-end evidence.
