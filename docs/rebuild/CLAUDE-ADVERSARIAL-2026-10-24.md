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
