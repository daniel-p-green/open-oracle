# Recovered implementation reuse — October 24, 2026

Reviewed the later `2026-10-11/task-16/open-oracle-pi` architecture, retrospective,
OpenAI contracts and engineering review in addition to its original product/
acceptance/checkpoint records. Targeted source reads covered `src/contracts.ts`,
`src/session.ts`, `src/playback.ts`, `server/operator.ts`, `server/evidence.ts`,
`server/pipeline.ts` and `server/audio.ts`. This is not a complete fresh audit of
its sideband/transport implementation, nor a rerun of its reported checks.

| Reusable asset/lesson | Current implementation decision |
| --- | --- |
| One owner, epoch/turn/source/language bindings | Extend current `createSession`, `Jobs` and the existing provider-job transport. No second media/session controller or wholesale React/SDK migration. |
| Explicit language/detail/simpler/repetition preferences | Public operation/language selectors now adapt the server's previously checked public unit; visitor text never becomes context. More conversation/input work remains. |
| Complete source role/span/hash/version contract | Pinned public question supplies app-owned source IDs/URLs and effect wording. Missing geometry does not suppress its original. Broader registry/coverage remains unfinished. |
| Stop distinct from Erase; partial speech is not delivery | Stop invalidates pending work while readable content remains; Erase clears local recap/preferences and revokes server public context. Fresh voice integration remains open. |
| Exact PCM/transcript/lease release | Retain as required design for fresh speech; do not copy untested pause-as-completion assumptions or deprecated transcription choices. Existing clips are fixtures only. |
| Expiring operator/source admission | Preserve source expiry; no old approval is imported. Shared current ledger and explicit provider mode remain authoritative. |
| Reported old local tests are not heard/Pi evidence | Current proof distinguishes code/mocks, actual bounded inference, browser behavior and unrun human/device checks. |

Original repos remain preserved. Old architecture/dependency/model names are not
automatically current. Official current docs verified Structured Outputs, Luna/
Sol pricing, Sol's supported Low reasoning (None unsupported), and current
`gpt-transcribe`; no new credential or software installation was needed.

Next engineering issue is the reviewed semantic interface: critical fact/scope/
polarity must remain separate from requested delivery quality and deterministic
source attribution. Do not lower a joint score simply to force a demo through.
The original stretch outcome remains resident understanding through a complete
adaptive, accessible journey, not successful model calls.
