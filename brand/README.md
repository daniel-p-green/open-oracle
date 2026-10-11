# Open Oracle brand kit

Status: selected concept 03 VOTE mark; production exports prepared 2026-10-11. Typography, color hierarchy, and the optional responsive favicon are provisional owner decisions. No application integration or publication occurred.

## Start here

- `logos/open-oracle-vote.svg`: original selected navy master, copied byte-for-byte.
- `previews/open-oracle-brand-contact-sheet.png`: actual rendered overview.
- `previews/index.html`: offline browsable SVG gallery.
- `lockups/horizontal/` and `lockups/stacked/`: mark plus outlined Open Oracle wordmark; each has sans and serif alternatives.
- `wordmarks/`: outlined standalone names.
- `social/open-oracle-og-light.png` and `open-oracle-og-dark.png`: 1200 × 630 social previews.
- `favicons/`: full selected mark at 16/24/32/48, multi-size ICO, 180 Apple touch icon and 192/512 web icons.
- `asset-manifest.json` and `validation.json`: dimensions, hashes and validation evidence.

## Palette and backgrounds

Navy #000c1f is the restrained primary recommendation. Reference control blue #002664 and cool background #f1f5fb come from the project's measured America.gov direction. White is #ffffff. Red #b31942 is a proposed electoral accent, not an extracted America.gov brand token; it is not the product error red. Palette hierarchy requires owner selection.

Original navy and red/blue SVGs have transparent exteriors and interiors. Use them on white or a similarly pale background. Blue/white and red/white/blue marks have an explicit white blossom interior and transparent exterior. Use white reversed marks and wordmarks on navy. Do not assume the navy/red transparent versions will work on a dark or mid-tone surface. Do not stretch, rotate, recolor individual letters, add effects or thicken the outline.

On white, measured contrast: navy 19.58:1, blue 14.37:1, proposed red 6.70:1. White on navy is 19.58:1. These are color contrast measurements, not proof of tiny-word legibility.

## Typography

Sans alternative: Libre Franklin, weight 500, tracking −.01em. Serif alternative: Libre Baskerville, weight 400, tracking −.02em. HarfBuzz shapes the text, including font kerning; FontTools creates path outlines. The font software remains unmodified, distributed in `fonts/` with corresponding SIL Open Font License notices in `licenses/`.

These are licensed provisional fallbacks. They do not claim to match Helvetica Now or Rhymes, the commercial reference typefaces in root DESIGN.md. No reference font binaries were downloaded or embedded. Wordmark/lockup SVGs contain paths and work without font installation. The Open Oracle wordmark remains an owner choice; retain both alternatives until chosen.

## Size and clear space

For the complete VOTE icon, 48px and above is the recommended working size. At 24px the word is small; at 16px the contour survives but the word should not be relied on. Wordmarks: keep the visible letter height at least 16px; horizontal lockups need enough room for the icon to remain at least 48px. Do not use a small full lockup as a favicon.

Reserve at least 1/8 of the icon canvas width as clear space outside its canvas (64 units for the 512-unit icon), or one capital O height around a standalone wordmark. The exports include some internal padding; maintain the additional external clearance in layouts. Background texture and photographs need a solid quiet surface behind the mark.

`favicons/favicon.svg`, the standard PNGs/ICO, Apple touch icon and web icons preserve the full selected VOTE artwork. They expose its tiny-size limitation honestly. `optional-responsive-v-*` is a separately named, provisional adaptation: the same outer contour with the existing V glyph enlarged. It reduces the word to one letter and is therefore not a replacement for the selected logo. Owner selection is required before using it. No favicon was wired into the app.

## Meaning and production limits

The badge immediately signals voting. The name and the descriptor “Understand your ballot” explain the comprehension purpose; “VOTE” alone may otherwise suggest participation or turnout. Navy feels more neutral; red/blue feels more electoral. The blossom is visually close to the supplied Codex contour, so it contributes familiarity more than a unique Open Oracle signature. The kit claims no official affiliation.

Selected image-generation artwork was traced with Potrace 1.16 and exported as SVG paths. This kit retains that trace geometry, including subtle facets in curved contours and the O counter. It does not claim a newly hand-refined geometric master. Production curve cleanup and owner sign-off remain appropriate before permanent integration. The original rejected explorations were left untouched.

All SVGs are self-contained XML with viewBox and outlined paths, no raster images, scripts, external links, font embedding or live text. PNGs are vector rasterizations by librsvg; logos, wordmarks and lockups have transparent exteriors. Social previews and touch/web icons have intentionally opaque backgrounds. Logo PNGs: 512/2048; wordmarks and lockups: 1200/2400px wide. The ZIP is built outside this directory so it never includes itself.

## Provenance and sources

Logo source: selected panel 03, `vote-refinements-iteration-22/open-oracle-vote-refinements-2x2.png`; image generation exploration followed by existing Potrace vector conversion. These assets are not attributed to Claude Opus. Earlier rejected Opus explorations are separate archives.

Font sources and licenses: https://github.com/google/fonts/tree/main/ofl/librefranklin and https://github.com/google/fonts/tree/main/ofl/librebaskerville ; exact downloaded URLs/hashes are retained in `licenses/font-sources.json`. Their OFL licenses allow document use and redistribution subject to the retained font notices. No Noun Project geometry or sample-stock illustrations are included in these exports.
