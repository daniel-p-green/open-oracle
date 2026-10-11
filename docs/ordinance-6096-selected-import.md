# Ordinance 6096 selected-passage ingestion

Eight manually inspected passages are now loaded as a distinct `combat-6096-selected-v1` source. It is an **adopted proposal**, with **partial verified reading-copy** quality, not current law or proof of voter approval. The previous `combat-6096` OCR source stays unverified. The original retained PDF is unchanged and remains outside Git.

The checked-in selected reading copy is an explicitly normalized manual transcription: visual line breaks are joined and repeated spaces normalized. Unicode offsets identify that reading copy, not PDF glyph positions. Each directly constructed chunk has a pinned page, section, passage hash and approximate reviewer locator in `data/6096-selected-index.json`; editorial headings are excluded from chunks. `selected_passage_binding` supplies inspection provenance; it does not approve public release.

Pins:

- Original PDF, 466739 bytes/five pages: `5fa4474560da047207bfd7c7033de0d0a1febb20d6e92cc6447982ca71a1afde`
- Selected reading: `229da53b66722072ed5f980c09ef91125b573fb1a18c333d2ed14961163f83a5`
- Selected index: `13b7602bf7d7d6553465732f343156ba5900480521900f1633baf5c21de32d39`
- External reviewed packet: `ad8c7fe44fd934217615cd7c931f824e005f104657900b359e0fb47f67e316b2`

The loader fails on changed original, reading or index bytes and constructs only the eight pinned spans. The index binds packet provenance; the full external packet is not a runtime dependency or Git artifact. The actual retained five-page original and approved image checks support this bounded import; no fresh HTTP-original equivalence is claimed.

Selected coverage includes the prior-authorization and expiry recitals, Section 1 submission scope/rate/duration/purposes, Section 2 administration/election-cost exception, Section 3 full submitted question including trust fund, Section 4 voter-approval condition and collection dates, Section 5 notification directive, and the separate immediate-effectiveness sentence. Legislative adoption/ordinance effectiveness and conditional tax collection remain distinct. A notification directive is not proof of completion.

Registry legal-reference retrieval and exact reading-copy citations are available. Ballot-fact/current-law/prediction eligibility and generic legal public release remain excluded; the existing finite COMBAT answer contract is unchanged. No Chapter 93 dated web-reader content, withdrawn Ordinance 6120 or unverified additional OCR is promoted. No vector ingestion, cloud storage, provider calls or arbitrary legal interpretation was performed.

Fifteen dedicated local tests cover pins, all eight spans, exceptions/conditions/trust fund, attribution, changes to bytes/offsets/pages/schema/scope/roles, old OCR rejection and legal release refusal. Integrated source counts become 5 sources and 107 chunks. The synthetic semantic test explicitly approves all verified/native sources and therefore builds 91 authored vector records; this is a fixture, not real AWS ingestion. Missing-index tests remain constrained to the unchanged unverified OCR source. Whole-suite validation and exact-source browser preservation are recorded in the core checkpoint.
