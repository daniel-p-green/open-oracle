# Open Oracle — measured America.gov design reference

Status: Daniel chose **America.gov as the CSS reference**, superseding the earlier visual proposals. This document records its measured styles and the deliberate Open Oracle adaptations. It does not select an earlier concept or establish government affiliation. Updated 2026-10-11. Core owns integration and git; frontend work remains isolated until reviewed.

## Evidence and scope

Reference: [America.gov](https://america.gov/). Fresh isolated Chrome returned HTTP 200; the text-fetch tool returned 403. Measurements cover 1280×720, 1440×1000, 1920×1080 and 390×844. The rendered page, screenshots, computed-style JSON and original stylesheets are retained under the design task's `design-discovery/america-reference/`. Source stylesheets: [base-html.CLkSFh1-.css](https://america.gov/_astro/base-html.CLkSFh1-.css) and [pages.BdnjhxEj.css](https://america.gov/_astro/pages.BdnjhxEj.css). Asset names are a point-in-time observation, not a stable dependency.

**Observed** means browser-computed values or an explicit stylesheet declaration. **Proposed** means an Open Oracle adaptation. Values below are observations unless marked proposed. No seal, flag lockup, government banner, slogan, photography, or privacy promise is transferred. Open Oracle identifies itself as an independent community prototype.

## Four principles for Open Oracle

1. **One calm focal point.** A large serif invitation, one question composer, and one contextual card. Use the existing official orb only as truthful status feedback; icon exploration belongs to the separate icon task.
2. **Read the original first.** Keep the entire retained original sentence readable. Underline one exact clause; put its faithful, short explanation underneath. Dimming is an optional exploration with readable contrast; blur is not approved.
3. **Reveal detail when requested.** Keep source attribution visible; expand sources, uncertainty and delivery details progressively. A material limit that changes interpretation stays with the answer.
4. **Show actual capability.** Voice, translations and synchronized captions appear only when their acceptance and timing contracts are satisfied. Static accepted text remains usable without audio, animation, microphone or WebGL.

## Color — exact reference values

| Role | Reference token | Value |
|---|---|---|
| Main ink | blue-900 / text-primary | `#000c1f` |
| Hover navy | blue-800 | `#00163b` |
| Primary control | blue-700 | `#002664` |
| Strong blue | blue-600 | `#004ac3` |
| Links | blue-500 / link | `#0066c5` |
| Cool light background | blue-50 | `#f1f5fb` |
| Main surface | white / background-primary | `#fff` |
| Neutral background | grey-50 | `#f7f7f7` |
| Neutral border | grey-200 | `#e3e4e6` |
| Error | red-600 | `#d80007` |
| Focus ring | black-100 | `#0c0c0c` |

Secondary text is `color-mix(in srgb, #000c1f 65%, transparent)`; tertiary text is 45%, disabled is 15%. Background-secondary is blue-700 at 10%; background-tertiary, neutral surface and footer are blue-700 at 5%. Borders use ink at 85%, 45%, 10% and 5%. Keep alpha values as alpha, rather than a solid swatch that only works on white.

**Proposed accessibility exception:** meaningful reading text uses primary or 65% ink over the actual surface. Do not use the reference's 45% or 15% ink for essential text. Give interactive field boundaries a separately verified 3:1 boundary; the reference's 5% decorative outline is insufficient as the only identifying affordance. Underlines and labels convey selected clause and errors as well as color.

## Typography — exact families, sources and reuse status

| Role | Observed family | Size / line / weight / tracking |
|---|---|---|
| Body | `"Helvetica Now Text", Arial, Helvetica, sans-serif` | 16px / 24px / 400; `ss01` off, `ss07` on, `ss08` off |
| Serif display | `"Rhymes Text", "Rhymes Fallback", "Times New Roman", Times, serif` | desktop hero 96px / 96px / 400 / −.06em |
| Mobile hero | same serif stack | `clamp(36px,12vw,48px)` / 1 / 400 / −.05em; 46.8px at 390px |
| Large desktop hero | same serif stack | at ≥1440px: `clamp(96px,5.71429vw + 13.7143px,144px)` |
| Intro subhead | `"Helvetica Now Display", Arial, Helvetica, sans-serif` | 24px / 36px / 400 / −.01em |
| Feature heading sampled | Helvetica Now Display | 40px / 42px / 500 / −.02em |
| Main desktop prompt | Helvetica Now Display | 21px / 31.5px / 400 / −.01em |
| Mobile prompt | Helvetica Now Text | 16px / 24px / 400 / −.03em |
| Primary control | Helvetica Now Text | 16px / 16px / 500 / −.03em |
| Small reference body/label | Helvetica Now Text | 12px; **proposed Open Oracle floor 16px** |

The reference also declares heading-l `clamp(3rem,2.3rem + 3.01vw,5rem)`, heading-s `clamp(1.125rem,.99rem + .56vw,1.5rem)`, heading-xs `clamp(1rem,.96rem + .19vw,1.125rem)`, and home-prompt/FAQ 21px. Do not confuse these with the final cascading hero rule above.

Exact observed font asset paths, relative to `https://america.gov`:

```text
/_astro/helvetica-now-text-400.DgICZbSh.woff2
/_astro/helvetica-now-text-500.2BZWIaro.woff2
/_astro/helvetica-now-display-400.CWJqSIYL.woff2
/_astro/helvetica-now-display-500.CYcMHrwX.woff2
/_astro/rhymes-text-regular.DRsO9i-l.woff2
```

The page loaded these families/weights. Each `@font-face` uses normal style and `font-display:swap`. Rhymes enables `liga`/`clig` and disables `dlig`/`hlig`. Its fallback declares local Times New Roman/Times with `size-adjust:112.68%`, `ascent-override:95.67%`, `descent-override:23.96%`, `line-gap-override:0%`.

**Verified rights limitation:** these are commercial fonts, not public-domain assets merely because America.gov serves them. [Monotype's Helvetica Now page](https://www.monotype.com/fonts/helvetica-now) offers webfont licensing. [Maxitype's Rhymes page](https://maxitype.com/typeface/rhymes/) identifies the foundry; its [published EULA](https://maxitype.com/wp-content/uploads/2023/01/MX_EULA_1.7.pdf), §§5.8–5.11, requires an appropriate web license and acquired webfont files. No Open Oracle license was supplied or purchased in this task. Do not download, embed or hotlink these reference binaries. The isolated preview uses the literal family stacks and the measured Rhymes local fallback, so glyphs are **fallback-rendered, not an exact font match**. Licensed self-hosted WOFF2 files are the remaining prerequisite for exact typography; keep font loading in one replaceable module.

## Spacing, shape and surfaces

Reference spacing scale: 4, 8, 12, 16, 24, 48, 96px. Site-section spacing: 9rem (144px), large 18rem (288px). Gutter: 16px. Page-inset token: 1.75rem (28px). Site container: 87rem (1392px). Mobile breakpoint: 768px.

Radius tokens: 4, 8, 12, 16, 24, 32, 40, 48px and full 9999px. Radius is selected by component, not applied uniformly.

| Component | Observed desktop | Observed mobile |
|---|---|---|
| Header | 56px horizontal inset, 24px padding, 12px gap; measured 1168×92 at 1280 | 12px inset/padding rule below 768px |
| Hero outer surface | 48px radius, x32 and width1216 at1280; 144px vertical /32px horizontal padding | 40px radius, full viewport width; 160px top /40px bottom padding |
| Main composer | 655×96 at 1280; radius 48px; padding 23px 23px 23px 40px | 358×119 at 390; radius 32px; measured same padding |
| Main textarea | transparent, border/radius 0; padding 8px 0 | same; smaller body type |
| Menu/text control | radius 40px, 44px tall, 20px inline padding, 2px bottom padding, 8px gap | same declared control style |
| Circular icon controls | 48×48, full radius | 40×40, full radius |
| Small composer elsewhere | radius 40px; padding 22px 24px 22px 32px | radius 32px |

Main composer outline: declared 1px ink at 5% when resting; timed focus samples show 2px `#0c0c0c` on desktop, large and mobile. One desktop idle snapshot caught an outline transition, so its intermediate oklab value is not used as the resting token. Main desktop composer has no effective shadow; mobile has `0 4px 16px rgba(1,14,36,.08)`. Elevation-1 token: `0 10px 40px 0 #010e2414`. Use these understated shadows only when they separate a floating surface.

Reference roadmap cards declare 40px radius, 20px padding, 16px gap and a 1px ink-5% outline. Where supported, they use `corner-shape:superellipse(1.3)` with radius scale 1.194. This is specific to roadmap cards; do not silently apply it to all controls or claim all reference corners are squircles.

**Proposed Open Oracle adaptation:** one reading card uses 40px desktop / 32px mobile corners. Essential controls have at least 48×48 CSS-pixel targets, instead of the reference's 40px mobile and 44px menu targets. Original wording uses body/sans-display at 24–32px and 1.45 line-height; explanatory text beneath uses 20–24px and 1.5. These reading sizes and card contents are proposed, not extracted America.gov styles.

## States and accessibility

Reference primary control: navy `#002664`, white label; hover rule `#00163b`; active navy/white. Ghost controls: transparent ink, hover blue-700 at 5%; disabled controls use ink at 15%. Transition: 200ms `cubic-bezier(.22,1,.36,1)` for color, background, border, shadow, scale and opacity. Keyboard focus rule: `box-shadow:0 0 0 2px #fff,0 0 0 4px #0c0c0c`; outline none on the control. Reduced motion removes transitions. Hover/focus snapshots taken immediately after activation are not proof of their settled CSS values; declarations and additional timed samples are distinguished in the evidence.

**Proposed:** retain this focus treatment on buttons and links; use a clear 2px ink outline on the composer. Honor reduced motion and provide the existing static orb fallback. No automatic audio, capture or playback. Support 320px reflow and 200% text resizing without horizontal reading scroll, clipping or hidden actions. Keep native labels, summaries, button semantics, logical heading order, keyboard operation and a polite status region; announce accepted changes once, not each audio sample. Verify contrast on composited surfaces rather than token values alone. Do not dim non-selected wording below normal-text contrast or blur it.

## Concrete Open Oracle screen states

| State | Visible content and controls |
|---|---|
| Ready | Text wordmark, independent community identity, large serif invitation, local election context, single composer; truthful voice availability, erase action, browse disclosure. No fake listening animation. |
| Listening | Existing microphone owner confirms active capture before label changes. Visible Stop and typed alternative remain available. One current transcript; draft is labelled. |
| Checking | Short status in the same surface. Preserve question. Allow cancel/erase; no simulated caption timing. |
| Source ready | Complete original sentence remains readable, one verified exact clause underlined, explanation beneath; source kind and text-only status visible. Previous/next clause controls change only the selected facet. Sources and limits expand below. |
| Withheld | Show genuine source fallback, if supplied, and concise reason the explanation is withheld. Never restyle this as accepted speech or invent a translation. |
| Speaking | Requires current accepted server receipt, matching request/text/source bindings and actual audio `playing`. Static accepted text remains visible. Stop/erase use existing owner. |
| Bilingual, conditional | Only after accepted verified language data exists: spoken language primary, English secondary, with controls to hide either. Label retained official original separately from generated translation. Current English-only payload does not activate this state. |
| Erasing/reset | Stop local capture and playback, cancel pending work, clear ephemeral session, return focus to composer. Do not promise provider deletion. |

## Implementation boundaries and acceptance

Preserve the current server release gates, request/visitor IDs, evidence hashes, speech receipt cancellation, and DOM accepted-answer binding. No translation or word timing is generated by presentation code. Keep `#answer-text` as the exact current accepted text with its request ID and language; do not visually or programmatically substitute a facet statement for that speech binding.

Use five reusable seams from `design-discovery/component-review/component-contracts.ts`: released-answer adapter, speech-session owner, draft/accepted transcript adapter, exact ballot focus view, and source/session controls. Bound generative cards to the approved catalog and validated data; [CopilotKit's requested Open Intelligent UI reference](https://www.copilotkit.ai/blog/introducing-open-intelligent-ui) informs the contextual component approach, not permission to bypass evidence review or accept freeform generated UI.

ElevenLabs TranscriptViewer requires aligned accepted text/audio and owns an audio element. Do not mount a second player beside OpenOracleLive. Current speech acceptance and word synchronization remain unverified. VoiceButton's recording state mounts LiveWaveform, which independently calls `getUserMedia`; adapt it to the existing stream/levels before use. ConversationBar starts an ElevenLabs provider session and is not a drop-in replacement for the current transport. Use retained MIT-licensed official sources only through documented adaptations.

For source spans, preserve the server's exact Unicode offsets. Python code-point indices require explicit conversion before JavaScript UTF-16 slicing when non-BMP text occurs; test emoji, combining characters and line breaks. Render original text via text nodes and a selected underline, never `innerHTML` from model data.

Frontend deliverable: isolated app preview and patch against its captured current baseline; no active UI edits, automatic merge or publication. Browser proof must cover Pi 1280×720 and a larger display, 320px reflow, 200% text, focus, readable contrast, unchanged accepted display and retained original hash. Label fixture/offline checks honestly. The separate icon task owns original SVG concepts; this preview retains a text wordmark.

## Model provenance

Earlier paired design reviews used the existing authenticated Claude Code Max setup with actual `claude-opus-5-5` model-use receipts and CLI `--effort high`, retained in `design-discovery/opus-use-evidence.json`. No new broad discovery or provider call was made for this CSS extraction. Sol6.1 HIGH was requested for this thread; runtime model/effort metadata is not independently exposed to the extraction tools, so that configuration is not asserted as verified evidence.
