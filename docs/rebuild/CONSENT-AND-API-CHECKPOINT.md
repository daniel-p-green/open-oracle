# Consent, checked playback and API checkpoint — October 24, 2026

The project lead selected **prechecked civic answers before audio output**. The experiment now has a runnable silent consent-to-reading-to-manual-playback flow, with provider-independent interfaces and real failure/cancellation tests. Actual service smoke tests ran separately after explicit testing authorization. The application itself still has no live credential/provider routes.

## Implemented and exercised

The voice preview requires explicit simulated consent after a cloud-data disclosure, then simulated device permission. No reading, capture or playback starts before consent. The active state says “fixture capture active — real microphone off.” Finishing a public fixture question stops capture before source checks. Only a receipt issued by the admitted evidence reader can authorize preparation; a caller's `answered` flag cannot. Complete transcript text, request revision and checked reading must match before manual Play becomes available. Preview text is labeled as a silent fixture, not actual speech/captions.

One shared session revision fences typed input, language/question changes, Stop, reset and idle expiry. Reset is synchronous; it aborts pending waits, disposes current resources, clears queued text and rejects/disposes late permission/capture/audio results. Timeouts and missing/changed transcripts hold without retry. Actual audio bytes, devices and live adapters remain outside this fixture contract.

The disclosure reflects [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data): no default local recording/transcript persistence; potential provider abuse-log retention up to 30 days with legal/safety exceptions; Live recording disabled by default; explicit `store:false` does not imply zero provider retention; ZDR requires eligibility/approval. Stop cannot unsend data. No account retention setting was changed.

## Independent findings and fixes

- **Confirmed source TOCTOU:** mutable caller corpus references could change during asynchronous hashing and release new prose under an old citation. Commit `2719937` snapshots all admission/release inputs synchronously before awaiting crypto and returns frozen source/claim objects. In-flight mutation regressions pass.
- **Confirmed audio-metadata TOCTOU:** adapter-owned transcript metadata could change after checking but before Play. The owner now passes an immutable metadata descriptor and derives preview from its canonical reading, with a currentness recheck after the player callback. A mutation-after-ready regression passes. This is not proof that live audio bytes acoustically match text.
- **Question/queued-reading mismatch:** changing the fixture question now interrupts and clears preparation/playback. Actual browser observation confirmed ready → question change → Play disabled and prepared text cleared.
- **Locale load race:** readiness now uses the selected locale when fixture loading completes. The actual app module is tested against delayed fetch and crypto, including pending typed answer → reset/language change → late completion with no stale UI output. This DOM/event fixture is not screen-reader proof.

Independent review reran 28 Node tests after the integrity fixes; the final owner suite adds the app-event regression for **29 Node tests**, all passing. The **5 actual loopback HTTP tests** pass. Syntax/diff checks pass. Browser actions exercised disclosure, disabled pre-consent controls, simulated capture, complete checked text, manual silent playback, immediate Stop and changed-question invalidation. No actual microphone/speaker call occurred. PR6 reported **no CI checks and no workflow runs** at inspection; local tests are not represented as remote CI.

## Authorized actual service evidence

The user later authorized a testing maximum, with minimal capped runs first. The existing process credential was used server-side without printing or persisting it; explicit organization/project headers matched the account verified in the official Platform. No credential was created, copied from a file, or exposed to browser code. Account balance/identifiers/screenshots and operational receipts remain outside this public repository.

| Test | Actual outcome | Limits |
|---|---|---|
| Read-only model preflight | HTTP 200; `gpt-live-1`, `gpt-6-luna`, `gpt-6.1-sol` listed | Listing alone does not prove inference access. |
| Decisions Playground, prepared public explanation | Support predicate displayed 100%; 641ms server, 352ms network | One request; probability is an uncalibrated estimate. Per-request tokens/charge not exposed by inspected UI. |
| Decisions Playground, ten years changed to twenty | Support predicate displayed 0%; 77ms server, 132ms network | One negative control, not a measured error rate. |
| Responses, `gpt-6-luna` | HTTP 200 completed; 406 input + 34 output tokens, no cache/reasoning tokens; selected `rate` and drafted “The printed COMBAT tax rate is one-quarter of one cent.” | One request, 128 output-token cap, `store:false`, no tools/retries; draft differs from finite baseline and was not released in the app. |
| Decisions API, generated draft | HTTP 200; `factual_support` probability 1.0; 371 input, zero output/cache tokens | One independent support check, not calibrated release approval. |
| GPT-Live, `gpt-live-1`, client delegation | Session started and `session.closed` confirmed `close_requested`; final usage 10.0s; 441,600 output PCM bytes; transcript exactly matched “The printed rate is one-quarter of one cent.”; zero backend calls/errors | One synthetic-zero-input session, 40s outer deadline, 15s close bound, `store:false`; no microphone, playback or saved audio. Nonzero bytes/peak and transcript match do not prove acoustic fidelity or a human-heard journey. |

[Current Standard pricing](https://developers.openai.com/api/docs/pricing) and [Decisions pricing](https://developers.openai.com/api/docs/guides/decisions#pricing-and-availability) price the three directly metered requests at approximately **$0.00843**: $0.0000576 Responses, $0.0000371 Decisions and $0.0083333 Live. These are usage-based estimates, not invoices, and exclude the two unmetered Playground requests. Conservative reservations across all five runs total $0.30. No retry, credit purchase, auto-reload or billing/access change occurred. Paid testing stopped after these runs.

## What the evidence changes

The requested services and model names are real, and this account/project completed bounded calls to all three. Low-cost structured generation can produce a grounded rate draft, but it did not remove the need for application-owned source/currentness contracts or calibrated review. Keep finite explanations as baseline. The synthetic Live transport path works for this fixed sentence; it does not justify enabling arbitrary civic conversation, unreviewed speech, private audio capture or Spanish release.

## Next prerequisite, not a new spend request

Testing budget authorization is already present. Before any human microphone trial, obtain explicit consent for the named device and a short fixed public utterance, disclose that raw audio goes to OpenAI and cannot be reliably redacted before streaming, and keep DOB/address/private voter records out of the trial. First integrate the prechecked buffer/transcript/currentness contract with manual Play using synthetic input, including timeout, mismatch and interruption cases; then prove one supervised Mac microphone → checked answer → matched buffered audio → deliberate human-heard Play journey. No Pi changes or deployment are authorized by this checkpoint.
