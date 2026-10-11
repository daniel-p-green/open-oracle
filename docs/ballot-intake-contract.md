# Isolated ballot PDF/TXT/paste intake contract

This additive slice parses supplied bytes/text and selects an entire detected question block or the full extracted document. It creates **unverified user content**, not an official ballot, accepted evidence, checked explanation, translation or speech. Core owns server endpoints, volatile retention, session/currentness, Strands/source admission, Decisions and playback. No server/client changes are included.

## Implemented API

```python
context = IntakeContext.from_owner(existing_complete_owner_ticket, document_revision)
result = parse_paste(text, context, cancelled=existing_cancel_or_stale_callback)
result = parse_upload(raw_bytes, "pdf" or "txt", context,
                      cancelled=existing_cancel_or_stale_callback)
if result.status == "ready_for_selection":
    selected = select_question(result.document, "q1" or "whole", context,
                               confirmed_complete=True,
                               cancelled=existing_cancel_or_stale_callback)
```

Only trusted application code may supply `Limits`, parser paths, cancellation callback or a retained document object. Endpoints must never deserialize a caller's `IntakeDocument` or accept their verification/review records. Context preserves the complete existing owner ticket as immutable JSON; it does not mint session, epoch, generation, request, language or voice identities. `document_revision` is supplied by the existing owner. These are correlation bindings, not authentication or a second controller.

The cancellation callback must synchronously return an exact Boolean: true for cancellation/stale operation. Adapt an existing event/currentness check rather than passing a throw-only `check_cancel` function directly. A callback failure/non-Boolean holds intake with `owner_check_unavailable`.

The document is immutable and privately retains original bytes, exact decoded/extracted text, raw and text SHA256, complete page spans, conservative question blocks and warnings. The private projection omits raw binary, labels provenance `unverified_user_content`, keeps `source_locale=unknown`, and returns `official_source_receipt=null`/`original_verified=false`. It has no answer, review, fact-validation, card, view-plan, source-fallback or speech authority. Do not pass it to AcceptedStore.

Selection accepts a registered whole block ID, not caller start/end/quote. It rechecks original/text hashes and reconstructs block boundaries to reject shortened/tampered spans. The quote is exactly `document.text[start:end]`. All conditions, exceptions, values and YES/NO content within that block remain; no summary, whitespace cleanup or silent length truncation occurs. A detected heading boundary can be wrong, and extraction can misorder columns. `confirmed_complete=True` records a user's assertion about the supplied full question; it **does not prove official completeness or provenance**. Original preview and whole-document fallback remain necessary. If headings fail, select the full document or supply the full question by paste. A question over the cap must be resupplied complete within limits, never cut to fit.

## Narrow proposed endpoint seam (not implemented)

| Route | Body and metadata | Core response |
|---|---|---|
| `POST /api/intake/paste` | Strict JSON `{owner_ticket, document_revision, text}`; <=512 KiB wire body, then module text limits. | Typed intake outcome; private document handle and projection only if retained. |
| `POST /api/intake/file` | Raw binary body, only `application/pdf` or `text/plain; charset=utf-8`. Core-reviewed bounded context header carries existing owner ticket/document revision; <=5 MiB PDF or 256 KiB TXT. No multipart needed for this slice. | Same typed intake outcome; filenames are optional display-only metadata in core, never passed as paths or authority. |
| `POST /api/intake/select` | Strict JSON `{owner_ticket, document_revision, document_handle, block_id, confirmed_complete}`; <=8 KiB. | Private selected-question record with exact quote/full-text offsets; no released civic answer. |

Core should choose the context header encoding (bounded base64url strict JSON is sufficient) and compare the **entire** decoded ticket against its own current session/operation, never trust a client epoch/request alone. Limit encoded header to 8 KiB and decoded context to 6 KiB; reject duplicate JSON keys, NaN, unknown fields, invalid encodings and ticket growth. Handle cookie/session binding, origin/host checks, CSRF posture and no permissive CORS through existing protections. Reject ambiguous Content-Length, compressed transfer bodies and unsupported content types before allocation. Do not buffer an unbounded chunked body or reuse `/api/ask`'s small body parser for uploads. No arbitrary URL, path, parser option, file password, remote-fetch or cloud-service input exists.

The module's creation context is retained with the document. If selection rotates the current generation, core validates the retained document's session/epoch/revision, calls selection with its **server-retained creation context**, then binds that private selection to the newly current complete owner ticket before commit. Do not trust a client-supplied old ticket, use creation context as answer authority, or force reupload merely because a new generation was started. Cancel/stale callback must check the current selection operation. A later source replacement, document revision, Erase or expiry invalidates the retained handle regardless of hash equality. Core must check currentness again immediately before retaining/displaying any parse or selection result; a check followed by an unguarded commit is a race.

Suggested HTTP outcomes: 200 for `ready_for_selection`/`empty`/`ocr_required`/`partial_extraction` with explanatory state; 413 for byte/page/text/output resource limits; 415 for unsupported file/encoding/content type; 422 for corrupt/active/encrypted PDF or incomplete confirmation; 409 for stale context/selection; 503 for missing parser/resource enforcement/owner check. Cancellation must not commit late content. Keep exact numeric/status mapping core-owned rather than pretending every file failure is missing election evidence.

## Bounds and parser containment

| Bound | Implemented maximum |
|---|---|
| PDF input | 5 MiB |
| TXT/paste UTF-8 input | 256 KiB |
| Extracted/decoded text | 80,000 Unicode code points |
| PDF pages | 30; all pages counted before extraction, never first-N truncation |
| Selection | 20,000 code points |
| Detected headings | 40 plus whole-document option |
| Parser stdout | 16 KiB metadata; <=512 KiB extracted text, streamed and killed on excess |
| Total PDF deadline | 8 seconds across metadata and text stages |
| Child CPU/files/descriptors | 5 CPU seconds per stage, zero core dump/file-size budget, 32 open descriptors |
| Linux memory | 256 MiB DATA plus 1 GiB address-space hard limits; Linux/Pi execution not tested here |
| macOS memory | Kernel RSS observed during bounded polling; kill above 256 MiB. Missing observation fails closed. **This is a sampled limit, not a hard allocation ceiling; brief overshoot is possible.** |

Uses existing Poppler `pdfinfo` and `pdftotext` from deployment-owned absolute paths, launched through the additive worker without a shell or `preexec_fn`. No parser/cloud package is installed. The parent streams stdin/stdout, discards parser stderr and unused metadata, closes handles, kills/reaps unfinished work and removes the private temporary working directory. Credentials/proxy/home/debug environment are not inherited. No visitor bytes are deliberately written by the module; original bytes live in bounded private memory. The parser may use its private temporary directory; it is removed after child termination. Do not claim secure RAM wiping or that cleanup equals remote provider deletion.

This is resource containment, **not a kernel sandbox against a compromised native parser**. Poppler does not execute document JavaScript/actions through these extraction commands, and this slice additionally holds detected JavaScript/forms/encryption; compressed/obfuscated content can defeat superficial feature detection. No embedded content, attachment, action or URI is fetched/executed by this application. Deployment must keep the trusted parser patched and decide whether a stronger OS sandbox is needed before exposing a public upload endpoint. Managed macOS sandbox restrictions on child memory observation can make PDF intake unavailable; TXT/paste remains usable. Do not weaken the guard to obtain a passing extraction.

Core must enforce aggregate limits **before exposing the route**: one active PDF parser, at most four retained documents and <=20 MiB total retained raw bytes, plus existing session capacity/TTL (suggest <=10 minutes), no accumulating old versions. This module has no global registry or persistence. Queue overflow is a fixed busy outcome, not unbounded work or an automatic retry. Reserve local worker/storage capacity separately from provider spend; uploading does not imply permission to send content to a model/OCR service.

## Encoding, offsets and empty/scanned files

- TXT is strict UTF-8 with one optional leading UTF-8 BOM removed by the explicit decoder. Raw bytes/hash retain the BOM. UTF-16 and malformed UTF-8 are rejected. Paste preserves Unicode exactly and rejects lone surrogates.
- No NFC/NFKC, accent, whitespace, newline, punctuation, digit, joiner or bidi-format transformation occurs. Binary C0/C1 controls are rejected except TAB/CR/LF and PDF page breaks. Unicode `Cf` controls remain exact with a warning; render with `textContent` and bidi isolation. Never render upload markup as HTML or automatically link/fetch domain text.
- Poppler emits UTF-8 layout text with Unix line endings. Each full page text is preserved; pages are joined with declared separator `\n\f\n` (UTF-8 bytes `0a 0c 0a`), included in the text hash. This is the exact extraction, **not proof of exact PDF reading order/glyph transcription**. There is no fabricated glyph/time alignment.
- All half-open offsets refer to Unicode code points in the **full** `document.text`, including separator characters, never selected-trimmed text. Pages share that offset space and exclude separator characters. JS UTF-16 indexes require explicit conversion; an emoji counts as one Python code point and two JS code units. Separate noncontiguous spans explicitly; never pretend a combined range was a continuous original quote.
- Empty PDF or authored image-only/scan-shaped PDF yields `ocr_required`; mixed blank/nonblank pages yield `partial_extraction`. Both have **no selectable questions**. A genuinely blank page can produce a conservative false hold. Offer a full-question copy/paste or a text-based PDF/TXT; no paid/local OCR implementation is included. Whitespace-only TXT/paste yields `empty`.

## Provenance, prompt injection and downstream admission

User-supplied file/paste stays unverified regardless of official-looking filename/domain/metadata, user confirmation, hash match or a caller's `original_verified=true`. Hashes bind private bytes, not authorship, official currency or election applicability. Do not export raw/text/selection hashes, user text, filenames, ticket identifiers, parser output or source history to logs/telemetry. Use fixed outcome enums and aggregate counts only. Avoid `asdict(document)` or generic exception/request logging.

All upload text is untrusted data. Exact instructions and markup remain visible as original content but cannot become system instructions, tool choices, source authority, URLs to fetch, parameters or release approval. Before any substantive output, core must validate full-question extraction/completeness, source role/provenance, scope/date/contest, retained source bindings and claim support, execute actual scoped Strands tools, and apply deterministic and Decisions release checks. Missing/conflicting evidence, unsupported question type or service failure stays explicit; silence or a model confidence is not evidence. This module does not register an uploaded source into Corpus.

The frozen language-v1 adapter assumes a **core-accepted English source** and sets `source_locale=en`. Core must reject unknown/non-English intake sources before invoking it, never infer source locale from UI language or completeness confirmation. Intake alone does not support source-language translation. Existing speech comparison rejects all `Cf` controls, including joiners; withhold speech rather than alter the original. Checked target text and speech require their own source/target/release/current-operation gates.

Stop/Erase/source or language replacement must synchronously invalidate the current owner operation before new UI state, set cancellation, discard pending parse/selection/output, reject late results, and drop all retained intake references/handles on Erase. The existing accepted answer may remain labelled with its original scope while a new input is pending; Erase clears it. Do not invent a second locale/voice/controller state machine.

## Supporting documentation and limits

The [Poppler pdftotext manual](https://manpages.debian.org/testing/poppler-utils/pdftotext.1.en.html) documents stdin/stdout, layout/UTF-8 extraction, page breaks and extraction/OCR limitations. The [pdfinfo manual](https://manpages.debian.org/testing/poppler-utils/pdfinfo.1.en.html) documents page/permission/JavaScript/form metadata. [Python resource documentation](https://docs.python.org/3/library/resource.html) describes platform-specific limits; [Apple's proc_taskinfo header](https://github.com/apple-oss-distributions/xnu/blob/main/bsd/sys/proc_info.h) defines the RSS field used by the macOS monitor. Installed CLI versions and actual proof are in the frozen handoff. Header/CLI compatibility is tested locally, not a universal security or parser-version guarantee.

No canonical endpoint, upload UI, Corpus admission, OCR, model transmission, language activation, speech/Pi or full-pipeline acceptance is implemented or claimed by this slice. Core reviews the frozen bytes, adds bounded retention/endpoint identity integration, then runs integrated upload/selection/Stop/Erase/source/release/privacy regressions before enabling it.
