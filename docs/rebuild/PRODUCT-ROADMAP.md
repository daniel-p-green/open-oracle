# Integrated civic experience roadmap

User direction recorded October 24, 2026: multilingual AI voice, fact-based
explanations and generative UI, including actual official maps for redistricting.
These are product acceptance goals, not capabilities established by the English
fixed-rate harness. Keep the [primary-source policy](PRIMARY-SOURCE-ARCHITECTURE.md)
and controlled speech path as shared foundations.

## Current completed boundary

The local web harness has exact public sources, abstention, source/currentness
checks, consent fixtures and one completed real Decisions/Responses/Live path.
No mic/speaker, broad candidate corpus, multilingual civic release, map comparison
or Pi acceptance has occurred. Complete each next slice with actual evidence,
small commits and a log entry before expanding paid usage or source volume.

## Next bounded work

1. One candidate primary-evidence bundle: read-only source/identity/rights
   inventory, tiny text extraction/version fixtures, then the agreed Agents API
   job after eligibility/pricing verification. Missing permitted debate transcript
   remains a gap; no unbounded transcription. The application owns publication.
2. Flagship redistricting comparison: verify the exact certified proposition,
   election date, enacted/proposed map versions, operative map and current court
   orders from official sources before implementation. Admission must distinguish
   certification from petition circulation and enactment from present operation.
3. A complete English/Spanish comparison journey: source-backed visual selection,
   checked explanation, matching captions/translation and deliberately enabled
   audio; test uncertainty, interruption, stale evidence and corrections across
   the entire journey. Human civic-language review precedes Spanish release.

## Official-map preflight: identified, not admitted

Read-only official discovery found the Missouri SOS
[2026 referendum circulation page](https://www.sos.mo.gov/petitions/2026refcirculation)
listing HB1 reference `2026-R004`. That page alone does not establish current
ballot certification, an election date, proposition label or legal operation.
Its displayed certification date and referenced session need reconciliation
against final official election records before reliance. The SOS
[map page](https://www.sos.mo.gov/RedistrictingMaps) directs readers to the state
Redistricting Office; its prominently listed 2022 Senate/House maps must not be
mistaken for congressional comparison artifacts. No geometry was admitted by
this discovery. Do not infer an exact district from a neighborhood.

Freshness follow-up, read October 24: the
[September 25 Supreme Court opinion, pages 1–2](https://www.supremecourt.gov/opinions/25pdf/26a388_q86b.pdf)
preserves the 2022 map for the 2026 election. The
[SOS September 10 direction](https://www.sos.mo.gov/default.aspx?PageId=10670)
also instructs local authorities to use 2022 boundaries. Recheck the
[case docket](https://www.supremecourt.gov/docket/docketfiles/html/public/26a388.html)
before release. The ballot's approval/rejection of HB1 must not be described as
redrawing the congressional ballot already used in November 2026.

[Census's current warning](https://www.census.gov/programs-surveys/decennial-census/about/rdo/congressional-districts.html)
says Missouri `cd120` GIS products still contain the superseded plan and await
regeneration, while the national block-equivalency file was corrected October 6.
Do not treat a newer filename as proof of operative boundaries. Date wording on
the Census narrative differs from the dated opinion: bind legal claims to the
court document and data-freshness claims to the specific Census product notice.
Parent research subsequently verified OA's official distribution chain and PDF
pair. This worker downloaded the exact four supplied artifacts, pinned local
hashes and verified eight proposed district IDs (1–8), GeoJSON EPSG:4326 and the
baseline NAD83 degree-based PRJ. See the [research manifest](MAP-SOURCE-MANIFEST.json).
Use the pinned CD118 baseline and proposed GeoJSON; the parent's HB1 shapefile
inspection found conflicting embedded metadata (PRJ 26915 versus XML 3857).
Do not copy stale distributor “not yet signed” prose as legal status. Geometry
topology, reprojection, shared-view rendering and use-specific state-map rights
remain admission checks. Downloads/hashes are not an implemented comparison.

The preflight deliverable is a reviewed manifest for **both** compared versions:
issuer, official URL, document/enactment/effective date, retrieval date, hash,
version, authority/status, litigation uncertainty and exact cited map/page.
For geometry include native CRS/projection, units, transformation/version and
official boundary IDs. For an official image/PDF with unspecified projection,
mark it unknown and show the original artifact; do not infer geometry or compute
area/population statistics from it. Verify reuse and attribution terms.

## Generative UI with deterministic evidence

Let the model select or compose typed components from an admitted bundle:
`MapComparison`, `OfficialMapArtifact`, `MeasureEffects`, `AttributedExcerpt`,
`SourceDisclosure`, `CoverageGap` and `UncertaintyNotice`. Validate component IDs,
scope, evidence/version references and allowed interactions before rendering.
No arbitrary generated HTML/scripts, invented map tiles/boundaries, unsourced
statistics or factual illustrations. Fail closed to the original artifact and
gap notice when typed output is invalid. Never use generated images as evidence.

Show clearly labeled current/operative and proposed/comparison versions with
dates and legal-status qualifications; use side-by-side or stacked views.
Synchronize extent only when compatible georeferencing is established. Keep
stable boundary IDs, labels, focus and selected evidence synchronized with the
checked reading/captions; interrupt audio on selection, language or version
change. A corrected map invalidates derived text, translated copy and audio.
Neutral legends must not imply candidate endorsement or invented political
impact. Explain Yes/No from exact admitted measure text, not visual intuition.

## Bilingual and accessibility acceptance

- Bind every translated claim to the original evidence/locator and reviewed
  translation version. Clearly label original versus translated material; keep
  originals accessible. Review legal conditions, negation, names, numbers and
  uncertainty. Pronunciation checks need language-specific evidence and human
  review; English tests do not establish other-language quality.
- Test a full English and Spanish source → question → official map comparison →
  explanation → captions → approved audio journey, including abstention when
  the requested language or source lacks review. Never silently fall back to
  English civic audio under a Spanish label.
- Keyboard/touch controls, focus order, visible captions, language metadata,
  text/table alternatives, non-color-only map distinctions, zoom and reduced
  motion remain requirements. Confirm with screen-reader/manual review rather
  than DOM assertions alone. Reset/idle must clear selections and queued audio.
- Pi remains a thin display/client. Budget geometry bytes, decode/paint time,
  memory and audio buffer before choosing a renderer; provide static official
  artifact fallback. Measure on target hardware later, without current Pi
  system changes. No automatic autoplay or consent inherited from a fixture.

Release gates: zero wrong ballot-membership assertions, invented map facts,
invalid citations or stale audio in the test corpus; official-version and legal
status review; bilingual civic review; accessible manual journey; measured
latency/resource/cost evidence. These are gates, not achieved statistical claims.
