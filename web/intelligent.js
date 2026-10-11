'use strict';
// Structured views of a released answer. Everything here is drawn from the same /api/ask result
// that app.js already rendered (its top-level `latest`), so no view can show a fact the text
// answer path did not release. Labels below describe response types and source coverage only.
(() => {
  const $ = id => document.getElementById(id);
  const make = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined) node.textContent = text;
    if (className) node.className = className;
    return node;
  };
  const KINDS = {
    answered: ['Source wording found', 'Exact retained wording, shown beside the source it came from.'],
    clarification: ['One more detail needed', 'Nothing was guessed. Choose or confirm below to continue.'],
    neutrality_boundary: ['Outside what this guide does', 'It explains wording and shows sources. It does not recommend how to vote.'],
    official_links: ['Sent to the official source', 'Voting logistics change, so the election authority is the place to check.'],
    insufficient_evidence: ['Coverage gap', 'No retained source answers this. The gap is shown rather than filled in.'],
    conflict: ['Source changed', 'The retained document no longer matches the inspected version, so its wording is withheld.'],
    unavailable: ['No answer released', 'A check did not pass. The contest inventory is still available.'],
  };
  const COVERAGE = {
    full_response_not_retained: 'Linked · answers not retained here',
    original_not_retained: 'Original unavailable',
    source_gateway_not_analyzed: 'Record gateway · not analyzed',
    source_specific_nonresponse: 'No response to this questionnaire',
    mentioned_not_surveyed: 'Mentioned · not surveyed',
    retained_original: 'Original retained',
  };

  function banner(result) {
    const [title, meaning] = KINDS[result.status] || ['Response', 'See the details below.'];
    const node = make('div', undefined, 'response-kind');
    node.dataset.status = result.status;
    node.append(make('strong', title), make('span', meaning));
    return node;
  }

  // Highlights, inside the original wording, the exact spans the explanation card quotes.
  function linkPassages(result) {
    const card = result.card;
    if (!card || result.status !== 'answered' || card.type !== 'measure_explanation') return;
    const index = result.evidence.findIndex(e => e.id === card.evidence_id && e.sha256 === card.source_sha256);
    const source = result.evidence[index];
    const quote = $('evidence').querySelectorAll('.evidence-card .quote')[index];
    if (!source || !quote || quote.textContent !== source.text) return;
    const facets = card.facets.map((facet, order) => ({ ...facet, order })).sort((a, b) => a.start - b.start);
    let cursor = 0;
    for (const facet of facets) {
      if (facet.evidence_id !== source.id || facet.start < cursor || source.text.slice(facet.start, facet.end) !== facet.quote) return;
      cursor = facet.end;
    }
    quote.replaceChildren();
    cursor = 0;
    for (const facet of facets) {
      quote.append(source.text.slice(cursor, facet.start));
      const mark = make('mark', facet.quote, 'passage');
      mark.id = `passage-${facet.order}`;
      mark.tabIndex = -1;
      mark.title = facet.title;
      quote.append(mark);
      cursor = facet.end;
    }
    quote.append(source.text.slice(cursor));
    quote.before(make('p', 'Highlighted passages are the exact words each part of the explanation quotes.', 'source-meta passage-legend'));
    decorateFacets();
  }

  function decorateFacets() {
    const card = typeof latest !== 'undefined' && latest?.card;
    if (!card || !document.querySelector('mark.passage')) return;
    for (const section of $('adaptive-card').querySelectorAll('.explanation-facet')) {
      if (section.querySelector('.passage-link')) continue;
      const text = section.querySelector('.facet-quote')?.textContent;
      const order = card.facets.findIndex(facet => facet.quote === text);
      if (order < 0) continue;
      const button = make('button', 'Find this in the original wording ↓', 'passage-link');
      button.type = 'button';
      button.addEventListener('click', () => {
        const mark = $(`passage-${order}`);
        if (!mark) return;
        document.querySelectorAll('mark.passage.current').forEach(node => node.classList.remove('current'));
        mark.classList.add('current');
        const calm = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        mark.scrollIntoView({ block: 'center', behavior: calm ? 'auto' : 'smooth' });
        mark.focus({ preventScroll: true });
      });
      section.append(button);
    }
  }

  // One column per person, one row per source. An empty cell is stated as a gap, never left blank.
  function comparison(result) {
    const people = result.candidate_sources || [];
    if (people.length < 2) return null;
    const sources = new Map();
    for (const person of people) for (const source of person.sources) if (!sources.has(source.source_id)) sources.set(source.source_id, source);
    const wrap = make('section', undefined, 'comparison');
    wrap.append(make('div', 'SOURCE COVERAGE · SIDE BY SIDE', 'eyebrow'));
    wrap.append(make('p', 'This compares which sources exist for each person, not their positions. A gap means nothing was retained. It is not a position and not a judgment.', 'source-meta'));
    const scroller = make('div', undefined, 'comparison-scroll');
    scroller.tabIndex = 0;
    scroller.setAttribute('role', 'region');
    scroller.setAttribute('aria-label', 'Source coverage by candidate');
    const table = make('table');
    const head = table.createTHead().insertRow();
    head.append(make('th', 'Source'));
    for (const person of people) { const th = make('th', person.candidate_name); th.scope = 'col'; head.append(th); }
    const body = table.createTBody();
    const row = (label, detail, cell) => {
      const tr = body.insertRow();
      const th = make('th', label); th.scope = 'row';
      if (detail) th.append(make('small', detail));
      tr.append(th);
      for (const person of people) {
        const [text, gap] = cell(person);
        tr.append(make('td', text, gap ? 'gap' : ''));
      }
    };
    for (const [id, source] of sources) {
      row(source.source_class, `Publication: ${source.publication_date}`, person => {
        const own = person.sources.find(s => s.source_id === id);
        return own ? [COVERAGE[own.coverage] || 'Coverage needs review', false] : ['Coverage gap · no pointer retained', true];
      });
    }
    if (!sources.size) row('Any attributable source', '', () => ['Coverage gap · none retained', true]);
    row('Position answers retained in this app', '', person =>
      person.position_evidence === 'not_retained' ? ['Coverage gap · not retained', true] : ['See this person’s sources below', false]);
    scroller.append(table);
    wrap.append(scroller);
    return wrap;
  }

  function followups(result) {
    const contest = result.contest;
    if (!contest || result.card?.type === 'candidate_comparison' || !['answered', 'insufficient_evidence'].includes(result.status)) return null;
    const options = [];
    const hasSources = (result.candidate_sources || []).length > 0;
    if (contest.kind === 'candidate' && result.status === 'answered') options.push(['What sources exist for these candidates?', `What sources exist for the candidates for ${contest.title}?`]);
    if (contest.kind === 'retention' && result.status === 'answered') options.push(['What sources exist about this judge?', `What sources exist for ${contest.title}?`]);
    if (contest.kind !== 'measure' && hasSources) options.push(['Show the printed wording', `Show the official wording for ${contest.title}.`]);
    if (!options.length) return null;
    const wrap = make('div', undefined, 'followups');
    wrap.append(make('div', 'NEXT, IF USEFUL', 'eyebrow'));
    const list = make('div', undefined, 'choices');
    for (const [label, question] of options) {
      const button = make('button', label);
      button.type = 'button';
      button.addEventListener('click', () => { $('question').value = question; $('ask-form').requestSubmit(); });
      list.append(button);
    }
    wrap.append(list);
    return wrap;
  }

  function enhance() {
    document.querySelectorAll('.response-kind, .comparison, .followups, .passage-legend').forEach(node => node.remove());
    const region = $('answer-region');
    const result = typeof latest !== 'undefined' ? latest : null;
    if (!result) { delete region.dataset.status; return; }
    region.dataset.status = result.status;
    $('answer-text').before(banner(result));
    linkPassages(result);
    const table = comparison(result);
    if (table) $('candidate-sources').before(table);
    const next = followups(result);
    if (next) $('choices').after(next);
  }

  // app.js writes #trace last when it renders a result and clears it on reset.
  new MutationObserver(enhance).observe($('trace'), { childList: true, characterData: true, subtree: true });
  new MutationObserver(decorateFacets).observe($('adaptive-card'), { childList: true, subtree: true });
})();
