# OpenOracle demonstration acceptance

Target: a source-backed, nonpartisan English/Spanish web experience worthy of a
public developer-profile demonstration. **Not complete or publicly ready.** No
public deployment, microphone/speaker activation or new credentials follow from
this checklist. Managed Agents is deferred; it must not block product work.

**Current native milestone, October24:** voice-first interaction remains the
acceptance target, not a source dashboard. The default screen centers Start
 talking, EN/ES, connection/media state, captions and a focused visual canvas;
human capture/playback remain disabled. Six actual native synthetic sessions
exist: the earlier corrected EN run accepted one audio segment and routed a KC
map follow-up, then held. The newly approved four-purpose package is consumed:
all four closed with usage, all held before accepted audio, and the recovery
trigger was not reached. Estimated package cost0.025895, reservation0.40 within
shared200. No full EN/ES native conversation, improved safe-audio latency or new
browser integration success is claimed. See [actual trial evidence](NATIVE-VOICE-TRIALS-2026-10-24.json).
The source-only Opus5.5High critique and explicit adversarial Message36 returned; [dispositions](CLAUDE-REVIEW-2026-10-24.md)
remain distinct from runtime acceptance. Native paid web-fixture activation is
closed so a review switch cannot start another session outside that package.

Current transcript implementation separates timed provisional input, checked
answer text awaiting speech validation and final checked-audio transcript state,
bound to language/source/turn/revision and cleared on Erase. Native input deltas
without an echoed owned command/timing binding are marked unavailable; they are never called final
utterances. The input-language field is a preference, not language detection.
This remains unverified through an actual full EN/ES voice/UI interaction.

October24 later caption/settlement repair: an optional public-synthetic-only
input-ASR path now binds final input captions to the exact submitted PCM hash
and turn, in parallel with the native response. Late provisional text cannot
replace its final caption; the complete receipt recovers captions after slow
polling. Input language mismatch and uncertain settlement hold the run. It is
off by default, has protocol/client contract proof, and has **no real-provider or
current-browser evidence**. No human capture or privacy-policy expansion follows.
The exact new six-stage bundle is approved but its first text launch was again
automatically denied before execution; [current blocker and limits](API-TEST-APPROVAL-BUNDLE.md).

**October25 actual progress:** a complete two-turn native English synthetic
session passed on09b02d3: fresh grounded explanation, native KC map selection,
exact-clip input captions, independent complete-output ASR and final usage/closure.
A separate recovery session reached checked text, cancelled and confirmed no
accepted audio. [Immutable staged evidence](STAGED-VOICE-RESULTS-2026-10-25.json).
This is CLI/API evidence, not current primary-browser rendering, human-heard or
unanticipated human-conversation acceptance. From input completion, checked text
was3.014s/1.114s and independently checked audio10.678s/8.814s; these are individual
samples, not percentiles. Whole-utterance buffering remains a latency limitation.

Later local implementation adds an owned per-turn EN/ES Decisions choice,
source-preserving fresh language adaptation, distinct session/input/response
language metadata and correct caption language tags. Both switch directions pass
the protocol owner with input/output ASR mocks, including preserved previous unit
and sources. A reviewer caught provisional input using the response language;
fixed to the owned clip language and rechecked. **The newer four-choice contract admitted one actual native decision on9e28ff5,
but its speech never matched checked text and the run held at deadline. It has
no complete native pass.** The two-turn fixture bound and UI preference
selector's existing Erase behavior remain; no continuous3turn EN→ES→EN claim.
Spanish brief engineering limit now150 rather than120characters (English stays
120), in both server/browser, to avoid dropping supported meaning for translation
expansion. Current-status/polarity/source/numeric/independent review and20s output
waveform gates remain. This change does not retroactively accept Spanish trials:
both text slots are consumed and Spanish independent review/live speech remain
unverified. Do not reuse a consumed purpose or spare money as stage authority.

Current API roles, checked against official documentation and actual local code:

| Service | Actual role / endpoint | Evidence and limit |
| --- | --- | --- |
| GPT-Live `gpt-live-1` | Native audio session `wss://api.openai.com/v1/live/sessions` | Actual synthetic sessions/usage; human path off; [current migration contract](https://developers.openai.com/api/docs/guides/live-migration) does not guarantee verbatim commentary or pause all spontaneous speech. |
| Decisions `gpt-6-luna` | Native voice view/focus/delivery choices; separate `/v1/decisions` review | Actual choices/checks; [native Decisions guide](https://developers.openai.com/api/docs/guides/decisions-voice). It is not the substantive answer generator. |
| Responses `gpt-6-luna` | `/v1/responses` source-bound fresh explanation/component selection | Actual generated briefs and holds; deterministic constraints plus separate review, not blanket correctness. |
| `gpt-transcribe` | Independent buffered waveform check `/v1/audio/transcriptions` | Earlier accepted EN segment; newest package never reached output-ASR. Whole-waveform gating limits first safe-audio latency. |
| Managed Agents API | Documented `/v1/agents/sessions` for bounded background evidence jobs | [Managed Codex harness](https://developers.openai.com/api/docs/guides/agents-api/overview), distinct from SDK; no managed trial executed, eligibility/cost envelope not demonstrated. Canonical source library remains application-owned. |

This is the finite requirement → implementation → evidence matrix. IDs stay
stable as work closes; source or product changes require updating these rows,
not adding disconnected features. D2 refers to the original stretch PRD;
D3–D6 to its later adaptive-voice decisions, inventoried in the reconciliation.

| ID / original requirement | Implemented | Verified evidence | Remaining acceptance |
| --- | --- | --- | --- |
| R01 D2§3/6A context | Election/authority/sample distinctions; administrator/public selection, no personal inference | Pinned KCEB W1P7 and separate JCEB notice; wrong-scope guards | Second JCEB individual style/current certification; final county variant reconciliation; no notice-as-ballot claim |
| R02 D2§3/5 approachable voice-first entry | Primary Talk/EN–ES/state/transcript/canvas, support progressively disclosed | Prior provider-off desktop voice UI replay | Natural public question through primary live UI; current mobile/manual accessibility proof |
| R03 D2§3/5 fresh voice loop | Native GPT-Live→Decisions choices→Responses→independent review→buffered Live→ASR gate | Earlier one EN accepted segment; contextual maps/KC native choice; newest four holds/usage documented | Successful full unanticipated question and follow-up with synchronized actual visuals/speech; acceptable measured latency |
| R04 D2§4 comprehension/adaptation | Fresh brief/simpler/detail with server-owned checked parent; session-owned repeat; separate exact effects | Earlier real EN overview→simpler→ES text adaptation in review mode; offline two-turn fresh-generation→repeat proof | Adapt based on explicit requests/demonstrated understanding, slower/repeat/clarification in real voice; no education/accent inference; brief contract live revalidation |
| R05 D2§4 strongest language | EN/ES UI and generated text paths; original English retained; translation status | Earlier ES text adaptation; new native Spanish input routed but attribution held | Full fresh ES speech/captions and mid-conversation language switch; human civic meaning/pronunciation review |
| R06 D2§4 captions/text alternative | Partial/input-gap/optional exact-clip final input/checked-text/final-audio states bound to turn/language/revision | Offline lifecycle/replay; actual four runs had no usable command echo, marked unavailable | Reliable language-appropriate input captions; no guessed clock association; usable silent core journey |
| R07 D2§5 controlled generative UI | Allowlisted evidence components, actual pinned maps, region-bound navigation acknowledgment; matching map reuse preserves local selection | Prior native maps/KC routing and offline browser render; source/prop checks | Actual conversation-selected summary/comparison/map updates; map-specific speech parity; no arbitrary code or invented facts |
| R08 D2§3/6C verify/challenge | Exact original, citations/version/uncertainty, held challenged parent, source access | Passage/hash/context guards; earlier browser source/challenge paths | First-class natural challenge/correction and visible correction history; conflicts/accessible originals/editorial admission |
| R09 D2 candidate journey/6B coverage | Printed roster gaps, equal fields, official office records, held campaign excerpt | 55-contest notice union,62 printed candidate entries/11 judges; source-specific office context | Individual styles/current certification, complete county/judicial office coverage, candidate identity/rights/primary-evidence admission; no inferred positions |
| R10 D2 optional teach-back/recap | Local optional checks, Skip, source-bound ephemeral recap | Earlier provider-off selected-source/withdrawal/Erase behaviors | Connected natural optional teach-back with gentle correction and same-language recap; actual comprehension evidence |
| R11 D2§4/5 accessibility | Semantic controls, text paths, keyboard, reduced motion, idle warning/extension | Prior scoped desktop/390px source-review checks; native replay1002px | Actual primary voice keyboard/screen-reader/zoom/mobile and geographic text equivalent; no blanket WCAG/Pi claim |
| R12 D2§4/6F privacy | Human media off, no private voter transport, ephemeral state/Erase; provider disclosure | Source/secret/client/reset checks, synthetic-only actual calls | Resolve private-safe natural input policy; local ASR alone cannot authorize private text downstream; human consent and retention verification |
| R13 D2§6D failure/interruption | Cancel/reset/stale revisions, deadlines, fail-closed review, exact-source fallback | Offline protocol/job/client checks; real held sessions closed with usage | Live cancellation trigger actually reached, wrong-turn UI/audio recovery, measured human interruption-to-silence; newest recovery did not reach trigger |
| R14 D2§6F/7 cost/operations | Shared ledger, distinct exhausted four-purpose and new six-stage packages; dispatch/usage/closure gates, rollback Git | Four package rows0.40 reserved/0.025895 estimate; exact prior CI; no new access | Public access/cost protection, source/editorial/language/on-call ownership and rollback rehearsal before deployment |
| R15 D2§8/9 repeatable proof | Local run/review artifacts and retained original demo reference | Actual source-only Opus critiques; original video frames/transcript inspected | Uninterrupted real interaction recording/event trace, nonauthor and bilingual/AT review, no mock-as-success claim |
| R16 D2 statewide/Pi ambition | Application-owned versioned source boundaries; web-first implementation | Local Mac contracts only | Jurisdiction adapters/source coverage and actual Pi memory/display/device tests; no current statewide/Pi readiness |

D2's consented resident research, proposed numerical pilot outcomes and staffing
are separate release-evidence requirements, not results or newly authorized
research spending. The October11 video is an interaction reference, not a live
acceptance recording: [exact asset and transferable patterns](PRIOR-DEMO-REVIEW.md).

English contract tests do not validate Spanish civic meaning. Synthetic audio
and model transcript matches do not establish pronunciation, acoustic fidelity or
a human-heard journey. A typed UI envelope never authorizes invented geography,
statistics, ballot membership or a recommendation. Every milestone updates this
matrix with implemented, verified and remaining evidence.


Actual Opus 5.5 critique returned **not ready**; High was verified in the client
UI. Substantive fixes and review limits are recorded in
[the disposition record](CLAUDE-REVIEW-2026-10-24.md). Focused re-review and narrow closure returned; the latter explicitly relies on
reported logic/browser proof. Independent code review inspected the key repairs.
No such closure is treated as whole-product acceptance. A public live demo still cannot be described as built.

Browser review target: current Chromium 120+ with `AbortSignal.any` and
`AbortSignal.timeout`; startup feature-checks these requirements. Older Safari,
physical phone/Pi browsers and screen readers are not covered by viewport tests.

Legal refresh procedure: retain the current official opinion/docket originals,
review intervening orders, update the legal record's as-of/review deadline and
source hashes, recompute its application pin in `measure-source.mjs`, rerun the
withholding proof and inspect the displayed assertion. A code change is deliberate
for this bounded corpus; no automatic rights/legal admission is inferred.


October24 input/latency increment: bounded natural-phrase confirmation and
contextual source/challenge/language/Stop paths exercised in the provider-off
browser. Brief mode preserves checks but has no paid result yet. Optional local
Whisper adapter ran with existing verified weights and network disabled; Spanish
errors require local correction, and no microphone route is enabled. The prior
33.02s English preparation is not acceptable conversational latency. New paid
Spanish trial and renewed Opus source upload were denied/pending exact approval;
independent local code review passed its narrower scope. See
[measured limits and next comparison](INPUT-AND-LATENCY-REVIEW.md). This is no
change to the overall not-ready verdict.


October24 public-notice increment: both retained official notice inventories
reconcile55 printed contests/62 candidate entries by contest and11 retention
judges. Local browsing now displays every printed roster with gaps, exact JCEB
measure and retention wording, source-specific dates/pages, office context,
source-only recap and transcription withdrawal. Independent pinned rebuild and
scoped code review passed; real provider-off desktop/390px Spanish navigation
was exercised. This does not close individual-style/current certification/
write-in, candidate-background, new-measure interpretation, human accessibility
or provider/multilingual voice gates. KCEB bytes are still the explicitly dated
October9 snapshot. A fresh Congress.gov read returned restricted URL and was
stopped; no alternative access or new background admission followed.


Late office-source Stop race repaired using a read-only revision snapshot from
the existing owner. Actual delayed local HTTP response was withheld after Stop;
a deliberate new read and Erase succeeded. Independent narrow review closed the
repair. No human/media/provider acceptance is implied.


October24 source-reading increment: all10 JCEB measure questions have exact,
hash-bound reading aids preserving complete conditions, not new interpretations.
Selected-notice follow-ups confirm the authority/contest before reading parts,
showing office duties, checking source comprehension, challenging or recapping.
Changing selection clears stale confirmation; challenge withdraws only the view
and offers an explicitly labeled saved-transcription return. Actual browser
checks covered EN/ES language switching, keyboard focus, optional-check Skip,
390px width, original lang=en and original links. Delayed guide response after
Stop/Erase did not repopulate; a new deliberate read succeeded, and HTTP503 left
the original readable. Source/evaluation mutation and scope checks passed.
Independent code review found a language-confirmation regression, now repaired
and verified in both directions. This later increment has **no renewed Claude
review or paid Spanish trial**; it is excluded from the immutable pending
8db5221 approval/payload. The full stretch target remains unmet.

October24 latency/native-UI increment: exact two-commit push65bad7a/6d90b11 is
complete and CI passed at6d90b11. Later work stays local. Parallel retained-source
reads reduce click-to-source/map/completion in a controlled fixed-delay browser
comparison; numeric diagnostics separate UI, text/review, Live and ASR stages.
Closed renderers and progressive source details require no generated HTML/JS or
extra rendering inference. A display-time legal expiry race was found, repaired
and independently closed. Native Chrome comparison exercised actual controls
and one runtime repair; its first map artifact failed, repaired output had only
document links, and its exact-source card worked through language/highlight/
check/Skip/Reset. No native renderer/geometry or new translation was imported.
See [the comparison](GENERATIVE-UI-COMPARISON.md). Actual live voice speed,
heard bilingual quality, full semantic composition and remaining stretch gates
are still open; no public-readiness claim follows.

### October 24, 15:00 UTC — Kansas City main journey and county comparison

Daniel selected Kansas City as the main demo and a second Jackson County ballot
to show real local differences. The implemented first context is the actual
two-page W1-P7 public sample: 25 printed contests, including 8 candidate
elections/15 printed candidate entries, 11 retentions and 6 measures. It is not
a personal ballot. The second context currently uses the JCEB public notice's
Independence bond question, explicitly **not a second individual ballot style**.
The notice cannot assign municipal questions or a candidate contest to a person.
JCEB's individual lookup requires private identifiers; none were entered.

| Workflow | Actual verification | Remaining gate |
| --- | --- | --- |
| KC sample → complete selected roster → official office context | Both sample pages visually checked; pinned compiler reproduces source spans, rejects unconsumed roster text and accounts for instruction/question anchors; public House5 roster exercised in browser | Current certification, complete write-ins and candidate background admission |
| KC → county-local example | Source selector switches to JCEB notice and exact Independence wording; amount, business-plan duration and courthouse name preserved; narrower membership warning visible | A second verified public individual JCEB style; no manufactured combination |
| Proposition A → maps → full original → return | Original includes printed fiscal estimate; question/artifact/page parity checked; same KC source/contest restored on return | Fresh audio latency, public-source rights release and accessible territorial description |
| English → Spanish navigation | Source-context controls and 390px layout exercised; original English retained, translation review notice visible | Human Spanish civic/pronunciation and screen-reader acceptance |
| Stop / Erase / language | Existing owner retained; aborted load gets stopped copy; selections are memory-only and cleared on Erase/language | Human workflow/acoustic/device acceptance |

Fresh direct approval now covers pushes, qualified merge/deploy and the two
bounded API trials within the shared $200 maximum. Publication readiness is
still not established. The current server is loopback-only; an existing safe
deployment target and protected metered inference entry have not been established.
No merge or deployment occurred in this increment. Fresh billing verification is
blocked at an account-selection sign-in approval; neither trial started.

Final verification: code commit `b8f9009` passed both remote offline-contracts
runs [40107057655](https://github.com/daniel-p-green/open-oracle/actions/runs/40107057655)
and [40107062980](https://github.com/daniel-p-green/open-oracle/actions/runs/40107062980).
Actual idle QA found and repaired a warning-layout scroll that renewed activity;
real Chrome then erased at~120.719s and clean entry had no previous contest.
Spanish warning keyboard focus/Continue/reading-focus recovery also passed.
Independent review closed these narrow repairs; full acceptance remains open.

October24 consolidated recap increment: source Add and global My recap are
separate actions; merely browsing stores no recap history. Existing state/abort/
expiry owner retained. Original English source content remains labeled in Spanish;
generated excerpts have per-unit AI/not-quotation/human-pending labels. Candidate
source cards keep every printed name in order with equal background gaps.
The same recap supports exact measure text, judicial questions and source versions.
Private voter lookup pages are dated plain-text references for a resident's own
device; this shared preview opens no private lookup tab or imports its results.

Actual browser proof: two-source KC/JCEB composition, source withdrawal, Spanish
switch/removal, connected-opener focus recovery, explicit Erase and real120s idle
erasure of saved choices. Isolated local503/delay responses exercised withheld
content/removal, Stop/late response suppression, deliberate reopen and Erase
while loading.390px in-app browser with version details expanded had scrollWidth375
and retained full hashes/question qualifiers after a scoped wrapping repair.
Chrome kept its actual1014px viewport despite a390px request; no Chrome-mobile or
physical-device proof is claimed. Opus5.5High critique and closure reviews returned;
independent code review found no remaining substantive issue within this scope.
No new paid API trial, billing sign-in, human audio or deployment occurred.

Recap delivery receipt, October24 16:30UTC: code `004e618e7e535421859ebb9b0ec97b7826b507f1`
is pushed to draft PR6. Both remote offline-contracts runs passed at that exact
SHA: [push](https://github.com/daniel-p-green/open-oracle/actions/runs/40111326672)
and [PR](https://github.com/daniel-p-green/open-oracle/actions/runs/40111329385).
The Library review image is `libfile_9df65636d3f88191afca6247ec64dcb0`
(`openoracle-consolidated-recap-review.jpg`). It shows the two explicitly added
public sources and navigation-only references; no live AI answer is depicted.
Temporary fault server8924 was stopped after QA; providers-off review8923 remains
available locally. Documentation receipts do not change the tested application.
Consolidated recap is implemented/locally verified; AI-planned composition,
live bilingual latency and the other full acceptance gates remain open.

Native-loop acceptance gaps after the corrected test: complete two-turn success;
full input caption timing/finality; Spanish live input/output and civic review;
first safe speech latency; actual interruption-to-silence; consent/privacy and
human device journey; restored browser tooling and renewed Opus5.5High review.
The new primary preview is code-reviewed and provider-off checked, not visually
verified or showcase-ready. Brief answer bound is now120 characters; its effect
on live latency is unmeasured. No checks were removed to improve speed.

Offline investigation/replay increment: actual Chrome1002×757 DOM/screenshots
showed the held trace's measure→paired Kansas City map transition, separate
provisional input turns, Stop legal demotion and Spanish language erasure. No
relevant console errors were observed. The replay banner explicitly excludes
API execution/audio/success claims. Responsive override returned inconsistent
dimensions and was reset; no new390px proof. A later Stop-before-map browser
check was denied by host-access policy and was not retried. Final source-before-
legal and missing-timing repairs were independently inspected and protocol
checked, not newly browser-verified. Actual live correlation, complete input
transcripts, language-hold diagnosis and bilingual acceptance remain open.

Current requested Claude Opus5.5High was visibly available in the existing
OpenOracle chat. The native-source file chooser timed out before setFiles; no
attachment or review prompt was submitted. This is a specific attachment-tool
blocker, not a claim that Claude or all browser tools are unavailable.


Latest adversarial review/fixes: [severity, reproductions and dispositions](CLAUDE-ADVERSARIAL-2026-10-24.md). Completed-job Erase/Stop honesty and session-repeat repairs passed offline contracts and independent inspection. Current browser/human/provider verification remains open; no acceptance row is closed by code inspection alone.

Latest source review Message38 found Spanish word-stem and cleanup-retry defects; local fixes and exact shared-helper/protocol evidence are recorded in the adversarial disposition. Map navigation now has matching bounded speech intent, while substantive map interpretation and actual provider/browser parity remain open.


October25 final bounded native-repair outcome: valid checked text returned at
9.312s, but228received output characters did not match120expected characters;
no accepted waveform,45soperation deadline and confirmed43sLive usage. Exact
spoken wording was not retained, so no invented semantic cause or causal claim
about the language feature. Paid sequence paused;5runs/25attempts/0.32reserved/
0.06827989166666668estimated. Spanish is the only unconsumed purpose, but the
hold/repair conditions do not authorize another text or native-repair run.
An early stable-prefix divergence hold is implemented and protocol-tested
separately; exact matching/independent whole-waveform ASR remain mandatory.
It cannot detect every trailing mismatch early and has no paid verification.
No continuous bilingual/browser/public-readiness result follows.
