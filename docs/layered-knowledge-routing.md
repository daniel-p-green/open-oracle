# Layered knowledge and question routing

Open Oracle needs a small hierarchy of reusable knowledge, not a flat collection
of documents searched for every question. This is the core implementation direction;
it makes no claim about another product's internals or measured latency.

| Layer | Question | Existing foundation | Boundary |
|---|---|---|---|
| Product and local actions | How does this work? Stop, Erase, change language | Local UI/session contracts, dated product FAQ | No legal/political answer or paid model required for local controls. |
| Applicable ballot and finite facts | What does the ballot say? Rate, duration, candidate's attributed response | Scoped Corpus, registered fact/card catalog, exact original spans | Election/board/contest/version must match. Candidate statement is not verified fact. |
| Official explanation and related proposal | What changes? What does Yes/No approve? Which conditions apply? | Official fair language plus separately role-labelled proposal clauses | Keep current law, proposed law, fiscal notes and official explanation distinct. Read complete material conditions. |
| Bounded evidence completion | Which necessary fact is missing from the ballot? | Private same-agent completion and scoped retrieval modules | At most the approved expansion; absent/conflicting evidence yields a precise gap. Draft cannot approve itself. |

User-facing navigation describes tasks—Read the question, See what changes,
Check the source, Explain this term. Storage/vector/provider names stay internal.
The landing's supplied PDF/TXT/paste is a separate unverified-input lane. Extraction
or a hash does not promote an upload to official evidence or an accepted answer.

## Per-question route

1. Keep the original request intact; split multipart requests without dropping parts.
2. Bind current visitor generation, document/language revision, election, jurisdiction
   and contest. Ask for missing scope rather than guessing personal eligibility.
3. Route local actions to existing owner controls. Resolve each factual part's
   source role and minimum complete evidence pack before any model request.
4. Reuse pinned local source metadata and exact source/span IDs. Semantic ranking
   locates candidates; it does not establish support or override scope/version.
5. Use substantive Strands tools for scoped search/acquire/read and structured claims.
   Expand only a necessary missing fact within the existing request budget.
6. Rebind all claims, numbers, units, conditions and attribution before and after
   applicable Decisions review. Review estimates remain fallible and uncalibrated.
7. Publish an immutable accepted projection or explicit insufficient/conflicting/
   unsupported/service-failure outcome. Separable supported parts require a complete
   mixed projection that passes release; never hide the unanswered parts.
8. Speech uses its separate current accepted receipt and closed transcript/audio
   fence. A retrieved answer or successful text review does not authorize playback.

## Implemented versus next optimization

The retained finite facts/catalog, source-role metadata, same-agent private completion,
strict accepted ingress and bounded provider requests exist. Amendment 7 currently
requires all five sources for every explanation; it is not yet an optimized selective
layer planner. Optional Decisions triage remains off. The next routing change should
be tested against locked multipart/scope/source-role cases before activation.

Cache only source/version-scoped records and registered finite content. A cached
answer must never bypass current source rehash, request/language identity or required
review. Do not cache visitor content or infer readiness from cache presence. Measure
route latency and calls by role before claiming the hierarchy is faster.
