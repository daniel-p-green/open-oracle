'use strict';
const $ = id => document.getElementById(id);
let inventory = [], category = 'measure', selectedId = null, latest = null;
let epoch = 0, sequence = 0, controller = null, voiceReady = false, voiceActive = false, liveEpoch = 0;
let visitorSession = crypto.randomUUID(), speechTransport = null;

let captureToken = null, answerToken = null, sensorAdapter = null;
const sensorSessions = new Set();
let previousInteractionState = null, voiceClosing = false;
const interaction = new window.OracleInteraction({
  onChange(snapshot) {
    document.body.dataset.interactionState = snapshot.state;
    $('mic').disabled = snapshot.state === 'reset' || voiceClosing || (!voiceActive && !snapshot.voiceReady);
    $('voice-stop').hidden = !voiceActive;
    $('capture-notice').hidden = !snapshot.voiceReady && !voiceActive;
    if (snapshot.state !== previousInteractionState && snapshot.presenceReady && snapshot.voiceReady && !($('input-disclosure').contains(document.activeElement)) && !$('question').value.trim() && ['presence','invitation'].includes(snapshot.state)) { $('input-disclosure').open = false; $('type-summary').hidden = false; $('type-summary').textContent = 'Type instead'; }
    if (snapshot.state === 'review') { $('input-disclosure').open = true; $('type-summary').hidden = true; }
    previousInteractionState = snapshot.state;
    const sensors = snapshot.presenceReady ? (snapshot.waveReady ? 'Presence and wave adapter connected' : 'Presence adapter connected · wave unavailable') : 'Presence and departure unavailable';
    const invitation = snapshot.state === 'invitation' && snapshot.voiceReady ? (snapshot.waveReady ? ' · Wave to begin' : snapshot.wakeReady ? ' · Spoken initiation available through the configured local detector' : '') : '';
    $('interaction-note').textContent = sensors + ' · ' + (snapshot.voiceReady ? 'Voice configured' : voiceActive ? 'Current voice session only' : 'Voice off') + invitation;
  },
  onIntent: token => beginVoice(token),
  onReset: () => resetVisitor()
});
// Operator seam; camera/wake detectors are not installed. Metadata transport is explicit opt-in.
window.OpenOracleInputs = Object.freeze({
  snapshot: () => interaction.snapshot(),
  attachSensorAdapter(options) {
    if (sensorAdapter?.closed) sensorAdapter = null;
    if (sensorAdapter) throw new Error('Detach the current input adapter first.');
    if (interaction.snapshot().state === 'reset') throw new Error('Finish reset before registering inputs.');
    if (sensorSessions.has(options?.sessionId) || sensorSessions.size >= 32) throw new Error('Use a fresh producer session; reload after 32 registrations.');
    const adapter = new window.OracleSensorAdapter(interaction, options);
    sensorSessions.add(options.sessionId); sensorAdapter = adapter;
    return Object.freeze({ accept: event => { const accepted = adapter.accept(event) === true; if (adapter.closed && sensorAdapter === adapter) sensorAdapter = null; return accepted; }, close() { adapter.close(); if (sensorAdapter === adapter) sensorAdapter = null; } });
  },
  reset: () => interaction.reset('accessible_control')
});

function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function orbEvent(type, detail = {}) {
  return window.OpenOracleOrb?.dispatch({ type, sessionId: 'visitor-' + epoch, ...detail });
}

function state(name, text) {
  $('orb').dataset.state = name;
  $('presence-state').textContent = text;
}
const live = new window.OpenOracleLive(event => {
  if (liveEpoch !== epoch) return;
  if (event.type === 'erase_requested') { interaction.reset('spoken_erase'); return; }
  if (event.type === 'allowance_used') { voiceReady = false; interaction.configure({ voiceReady: false }); $('mic-note').textContent = event.text; }
  if (event.type === 'transcript') {
    if (!interaction.valid(captureToken) || interaction.snapshot().state !== 'listening') return;
    selectedId = null; $('question').value = event.text; renderInventory();
    $('spoken-question').textContent = event.text; $('spoken-question').hidden = !event.text;
  } else $('activity').textContent = event.text;
  if (event.type === 'listening') {
    if (!interaction.signal('capture_ready', captureToken)) { live.close(); return; }
    state('listening', 'Listening to your question');
    orbEvent('capture-started', { captureActive: live.stream?.getAudioTracks().some(t => t.enabled && t.readyState === 'live') === true });
  }
  if (event.type === 'unavailable') { voiceReady = false; interaction.configure({ voiceReady: false }); $('mic-note').textContent = event.text; }
  if (event.type === 'connected' || event.type === 'listening') { voiceReady = false; interaction.configure({ voiceReady: false }); $('mic-note').textContent = 'The one-session voice allowance is now used. This question can finish; use typing for later questions.'; }
  if (event.type === 'connecting') { state('thinking', 'Connecting'); orbEvent('connection-started'); }
  if (['buffering','ready','speaking','paused','finished','held'].includes(event.type)) {
    $('speech-status').textContent = event.text;
    $('speak').hidden = false; $('speak').disabled = event.type === 'buffering' || event.type === 'held';
    $('speak').textContent = event.type === 'speaking' ? 'Stop playback' : live.ready ? 'Play answer' : 'Prepare spoken answer';
    if (event.type === 'ready') interaction.signal('speech_ready', answerToken);
    if (event.type === 'buffering') interaction.signal('speech_preparing', answerToken);
    if (event.type === 'speaking') { interaction.signal('playback_started', answerToken); state('speaking', 'Speaking'); orbEvent('playback-started', { requestId: event.request_id, validated: event.validated === true, playing: event.playing === true }); }
    if (['paused','finished','held'].includes(event.type)) { interaction.signal(event.type === 'held' ? 'speech_held' : 'playback_finished', answerToken); state('ready', 'Answer and sources'); orbEvent('playback-stopped', { requestId: event.request_id || latest?.request_id }); }
  }
  if (event.type === 'review') { interaction.signal('transcript_review', captureToken); state('uncertain', 'Review the transcript · voice held'); orbEvent(event.type === 'review' ? 'input-review' : 'output-held'); }
  if (event.type === 'stopped' || event.type === 'error') {
    interaction.signal('capture_failed', captureToken); interaction.signal('speech_held', answerToken);
    voiceActive = false; $('mic').textContent = 'Speak';
    state('ready', 'Text input is ready');
    $('voice-stop').hidden = true; interaction.configure({ voiceReady: Boolean(voiceReady) }); restoreSpeechControls();
    orbEvent(event.type === 'error' ? 'connection-error' : 'capture-stopped');
  }
}, () => latest && !$('answer-region').hidden && $('answer-text').getClientRects().length > 0 ? { request_id: latest.request_id, text: $('answer-text').textContent, language: $('answer-text').lang } : null);
function restoreSpeechControls() {
  if (!latest?.speech) { $('speak').hidden = true; $('speak').disabled = true; return; }
  $('speak').hidden = false; $('speak').disabled = !live.ready && !voiceReady;
  $('speak').textContent = live.ready ? 'Play answer' : 'Prepare spoken answer';
}
function clearAudio() { live.cancel(); interaction.signal('speech_held', answerToken); if (latest) state('ready', 'Answer and sources'); restoreSpeechControls(); }


function renderInventory() {
  const query = $('search').value.toLowerCase();
  $('contests').replaceChildren();
  const rows = inventory.filter(c => c.kind === category &&
    (c.title + ' ' + c.candidates.map(p => p.name).join(' ')).toLowerCase().includes(query));
  if (!rows.length) $('contests').append(element('p', 'No matching contests in this snapshot.', 'muted'));
  for (const contest of rows) {
    const button = element('button', undefined, 'contest' + (selectedId === contest.id ? ' active' : ''));
    button.type = 'button';
    button.setAttribute('aria-pressed', String(selectedId === contest.id));
    button.append(element('strong', contest.title), element('small',
      contest.kind === 'candidate' ? (contest.comparison_topics ? 'Compare stated priorities and property assessments' : `${contest.candidates.length} printed nominee${contest.candidates.length === 1 ? '' : 's'} · position evidence not indexed`) : contest.scope + ' · original wording'));
    button.addEventListener('click', () => {
      selectedId = contest.id;
      $('question').value = contest.comparison_topics ? 'Compare Pollard and Fields priorities' : `Show the official wording for ${contest.title}.`;
      renderInventory();
      ask();
    });
    $('contests').append(button);
  }
}

function currentScope() {
  const location = $('location').value;
  const scope = { election_date: '2026-11-03', authority: $('authority').value };
  if (location === 'Sni Valley Fire Protection District') scope.district = location;
  else if (location) scope.municipality = location;
  return scope;
}

function safeLink(title, url) {
  const anchor = element('a', title);
  const parsed = new URL(url, window.location.origin);
  if (parsed.origin === window.location.origin || parsed.protocol === 'https:') {
    anchor.href = parsed.href;
    anchor.target = '_blank';
    anchor.rel = 'noopener noreferrer';
  }
  return anchor;
}

function renderAnswer(result) {
  latest = result;
  $('spoken-question').hidden = true;
  $('answer-region').hidden = false;
  document.querySelector('.conversation').classList.add('has-answer');
  document.querySelector('.conversation').classList.toggle('has-card', (!!result.card && result.status === 'answered') || !!result.source_fallback);
  $('sources-disclosure').open = false; $('input-disclosure').open = false; $('type-summary').hidden = false;
  $('sources-summary').textContent = `Sources (${result.source_fallback?.sources?.length || result.evidence?.length || 0}) and limits`;
  $('answer-text').lang = 'en';
  $('speech-status').textContent = result.speech ? 'The answer is ready to read or prepare for speech.' : result.review.status === 'not_run' ? 'Text only · independent AI review is off.' : 'Text only · voice requires an accepted answer. AI checks are fallible.';
  $('answer-status').textContent = result.status.replaceAll('_', ' ').toUpperCase();
  $('answer-title').textContent = result.contest?.title || 'A source-based response';
  $('answer-text').textContent = result.answer;
  for (const id of ['choices', 'adaptive-card', 'roster', 'evidence', 'candidate-sources', 'links', 'limitations']) $(id).replaceChildren();
  $('adaptive-card').removeAttribute('tabindex');
  renderCard(result);
  for (const choice of result.choices || []) {
    const button = element('button', choice.title);
    button.type = 'button';
    button.addEventListener('click', () => { selectedId = choice.id; ask(); });
    $('choices').append(button);
  }
  if (result.required_scope?.value) {
    const value = result.required_scope.value;
    const button = element('button', `Answer in the context of ${value}`);
    button.type = 'button';
    button.addEventListener('click', () => {
      $('authority').value = 'JCEB';
      $('location').value = value;
      ask();
    });
    $('choices').append(button);
  }
  if (result.status === 'answered' && result.card?.type !== 'candidate_comparison') {
    for (const candidate of result.contest?.candidates || []) {
      const card = element('div', candidate.name);
      card.append(element('small', `${candidate.party} · as printed in the snapshot inventory`));
      $('roster').append(card);
    }
  }
  for (const evidence of result.source_fallback?.sources || result.evidence || []) {
    const card = element('article', undefined, 'evidence-card');
    card.append(element('div', 'ORIGINAL SOURCE WORDING', 'eyebrow'), element('h3', (evidence.candidate_name ? evidence.candidate_name + ' · ' : '') + evidence.title));
    card.append(element('p', `${evidence.issuer} · ${evidence.source_category} · retrieved ${evidence.retrieved_date}` +
      (evidence.page ? ` · page ${evidence.page}` : '') + (evidence.column ? `, column ${evidence.column}` : ''), 'source-meta'));
    card.append(element('p', `${evidence.version}. ${evidence.extraction}.`, 'source-meta'));
    card.append(element('blockquote', evidence.text, 'quote'));
    card.append(safeLink(evidence.original_label || 'Retained original PDF ↗', evidence.original_route), safeLink('Publisher source ↗', evidence.url));
    $('evidence').append(card);
  }
  for (const person of result.candidate_sources || []) {
    const card = element('article', undefined, 'evidence-card');
    card.append(element('div', 'CANDIDATE-SPECIFIC SOURCE NAVIGATION', 'eyebrow'), element('h3', person.candidate_name));
    card.append(element('p', person.gap, 'source-meta'));
    if (!person.sources.length) card.append(element('p', 'No attributable substantive source was retained for this person in the bounded catalog. This is a research gap.', 'source-meta'));
    for (const source of person.sources) {
      const row = element('div', undefined, 'candidate-source');
      const labels = { candidate_statement_link: 'Candidate-authored answers · publisher link only', third_party_judicial_survey: 'Third-party judicial survey · not an app rating', official_record_gateway: 'Official record gateway · not a completed voting history', independent_reporting_link: 'Independent reporting · publisher link only' };
      const coverage = { full_response_not_retained: 'Full source text is not retained. No position quote is available here.', original_not_retained: 'Original report is unavailable or its version changed.', source_gateway_not_analyzed: 'Records include historical service; current positions are not inferred.', source_specific_nonresponse: 'Research records a nonresponse to this particular questionnaire. This does not establish a position or general absence of sources.', mentioned_not_surveyed: 'Mentioned by the source; not part of this questionnaire. No candidate answer is inferred.', retained_original: 'Retained 2026 survey original. Survey findings belong to the attributed third-party source.' };
      const title = source.coverage === 'source_specific_nonresponse' ? 'Questionnaire source · source-specific nonresponse' : source.coverage === 'mentioned_not_surveyed' ? 'Race guide · candidate mentioned, not surveyed' : labels[source.kind];
      row.append(element('strong', title || 'Source pointer'));
      row.append(element('p', source.source_class + ' · publication: ' + source.publication_date + ' · retrieved ' + source.retrieved_date, 'source-meta'));
      row.append(element('p', coverage[source.coverage] || 'Coverage requires review.', 'source-meta'));
      row.append(element('p', source.document_period, 'source-meta'));
      row.append(safeLink('Publisher source ↗', source.url));
      if (source.original_route) row.append(safeLink('Retained 2026 survey PDF ↗', source.original_route));
      card.append(row);
    }
    $('candidate-sources').append(card);
  }
  for (const link of result.links || []) $('links').append(safeLink(link.title + ' ↗', link.url));
  $('limitations').append(element('strong', result.review.label));
  for (const line of result.limitations || []) $('limitations').append(element('div', line));
  $('trace').textContent = JSON.stringify({ mode: result.mode, elapsed_ms: result.elapsed_ms, stage_ms: result.stage_ms,
    review: result.review.status, steps: result.trace, request_id: result.request_id }, null, 2);
  $('speak').hidden = !voiceReady || !result.speech; $('speak').disabled = !voiceReady || !result.speech; $('speak').textContent = 'Prepare spoken answer';
  state(result.status === 'answered' ? 'ready' : 'uncertain', result.source_fallback ? 'Original wording available · explanation withheld' : result.status === 'answered' ? 'Original evidence available' : 'Context or evidence needed');
  interaction.signal(result.status === 'answered' ? 'answer_accepted' : 'answer_withheld', answerToken);
  live.evidenceContext(result);
}

function renderCard(result) {
  const card = result.card;
  if (result.source_fallback?.type === 'verified_originals') {
    const article = element('article', undefined, 'explanation-card source-fallback');
    article.dataset.viewComponent = 'source_quotes';
    article.append(element('h2', 'Original wording · explanation withheld'), element('p', result.source_fallback.label, 'fine'));
    for (const source of result.source_fallback.sources) {
      article.append(element('h4', source.candidate_name || source.title), element('p', source.source_category, 'source-meta'), element('blockquote', source.text, 'quote'));
      article.append(safeLink('Read the retained original ↗', source.original_route));
    }
    article.append(element('p', result.source_fallback.candidate_statement_limit, 'fine'));
    $('adaptive-card').append(article); return;
  }
  if (card?.type === 'candidate_comparison' && result.status === 'answered') {
    if (card.responses.length !== 2 || !card.responses.every(r => result.evidence.some(e => e.id === r.evidence_id && e.candidate_name === r.candidate_name && e.text === r.quote && e.passage_sha256 === r.passage_sha256))) return;
    const article = element('article', undefined, 'explanation-card');
    article.append(element('p', 'The Beacon · Candidate answers, edited for length', 'source-kind'), element('h3', card.title), element('p', card.method, 'source-meta'));
    const columns = element('div', undefined, 'candidate-comparison');
    for (const response of card.responses) {
      const section = element('section', undefined, 'explanation-facet');
      section.append(element('h4', response.candidate_name), element('p', response.party + ' · District 1 At-Large', 'source-meta'), element('blockquote', response.quote, 'facet-quote'));
      section.append(safeLink('Read the published questionnaire ↗', result.evidence.find(e => e.id === response.evidence_id).url));
      columns.append(section);
    }
    const controls = element('div', undefined, 'choices');
    for (const [label, topic] of [['Compare priorities', 'priorities'], ['Compare property assessments', 'property taxes']]) {
      const button = element('button', label); button.type = 'button';
      button.addEventListener('click', () => { selectedId = card.contest_id; $('question').value = `Compare Pollard and Fields ${topic}`; ask(); }); controls.append(button);
    }
    article.append(columns, controls, element('p', card.limit, 'fine'));
    $('adaptive-card').append(article); return;
  }
  if (!card || result.status !== 'answered' || card.type !== 'measure_explanation') return;
  const source = result.evidence.find(e => e.id === card.evidence_id && e.sha256 === card.source_sha256);
  if (!source || !card.facets.every(f => f.evidence_id === source.id && source.text.slice(f.start, f.end) === f.quote)) return;
  const region = $('adaptive-card'); region.tabIndex = 0; region.setAttribute('role','region'); region.setAttribute('aria-label','Explanation parts');
  const article = element('article', undefined, 'explanation-card');
  article.append(element('p', 'JCEB · Official sample ballot', 'source-kind'), element('h3', card.title));
  article.append(element('p', card.method, 'source-meta'));
  const content = element('div'); content.setAttribute('aria-live','polite');
  const controls = element('div', undefined, 'choices');
  let step = result.view_plan?.initial_part || 0;
  const single = result.view_plan?.component === 'measure_focus' || card.presentation === 'choice_focus';
  article.dataset.viewComponent = single ? 'measure_focus' : 'measure_parts';
  function show() {
    const focusedPart = controls.contains(document.activeElement) ? document.activeElement.dataset.part : null;
    content.replaceChildren(); controls.replaceChildren();
    const facets = [card.facets[step]];
    if (!single) content.append(element('p', `One thing at a time · ${step + 1} of ${card.facets.length}`, 'source-meta'));
    for (const facet of facets) {
      const section = element('section', undefined, 'explanation-facet');
      section.append(element('h4', facet.title));
      if (facet.statement !== result.answer) section.append(element('p', facet.statement));
      if (single) { section.append(element('p', 'Original wording', 'source-meta'), element('blockquote', facet.quote, 'facet-quote')); }
      else { const original = element('details'); original.append(element('summary', 'See the source wording'), element('blockquote', facet.quote, 'facet-quote')); section.append(original); }
      content.append(section);
    }
    if (!single) {
      for (const [label, delta] of [['Previous part', -1], ['Next part', 1]]) {
        const button = element('button', label); button.type = 'button';
        button.dataset.part = String(delta); button.disabled = step + delta < 0 || step + delta >= card.facets.length;
        button.addEventListener('click', () => { clearAudio(); step += delta; show(); }); controls.append(button);
      }
    } else {
      const button = element('button', "I still don’t understand"); button.type = 'button';
      button.addEventListener('click', () => { selectedId = card.contest_id; $('question').value = "I still don't understand"; ask(); });
      controls.append(button);
    }
    if (focusedPart !== null) { const next = controls.querySelector('[data-part=\"' + focusedPart + '\"]'); (next && !next.disabled ? next : region).focus(); }
  }
  article.append(content, controls, element('p', card.limit, 'fine'));
  article.append(safeLink('Read the retained original ↗', source.original_route)); region.append(article); show();
}

async function ask() {
  const question = $('question').value.trim();
  if (window.OpenOracleEraseIntent(question)) { interaction.reset('typed_erase'); return; }
  if (/^(?:please )?(?:explain |show |tell me )?(?:how (?:my|our|your) data is used|how (?:you|this app) use(?:s)? (?:my|our) data|privacy|data use)[?.!]*$/i.test(question)) { showDataUse(); return; }
  if (!selectedId && latest?.card && /^(?:i still don['’]?t understand[.!?]?|i['’]?m still confused[.!?]?|what does (?:yes|no) mean[.!?]?)$/i.test(question)) selectedId = latest.contest.id;
  if (!question) { $('question').focus(); return; }
  const lifecycleToken = interaction.beginThinking();
  if (!lifecycleToken) { $('activity').textContent = 'Reset is still stopping devices. Please wait or choose Start again to retry cleanup.'; return; }
  answerToken = lifecycleToken;
  clearAudio();
  controller?.abort();
  controller = new AbortController();
  const thisController = controller;
  const thisEpoch = epoch, thisSequence = ++sequence;
  const requestId = crypto.randomUUID ? crypto.randomUUID() : `${epoch}-${sequence}-${Date.now()}`;
  latest = null;
  $('speak').disabled = true;
  $('activity').textContent = 'Finding the retained source…';
  state('thinking', 'Finding evidence');
  orbEvent('request-started', { requestId });
  $('answer-region').hidden = true;
  const progress = setTimeout(() => {
    if (epoch === thisEpoch && sequence === thisSequence) $('activity').textContent = 'Still checking evidence. You can start a new question or reset.';
  }, 15000);
  const timeout = setTimeout(() => thisController.abort(), 40000);
  try {
    const body = { question, scope: currentScope(), request_id: requestId };
    if (selectedId) body.contest_id = selectedId;
    const response = await fetch('/api/ask', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Oracle-Session': visitorSession },
      body: JSON.stringify(body), signal: thisController.signal });
    const result = await response.json();
    if (epoch !== thisEpoch || sequence !== thisSequence) return;
    if (!response.ok) throw new Error(result.error || 'Evidence request failed.');
    if (result.request_id !== requestId) throw new Error('Response identity did not match. Please retry.');
    renderAnswer(result);
    orbEvent('answer-released', { requestId, status: result.status });
    $('activity').textContent = 'Source response ready.';
  } catch (error) {
    if (epoch !== thisEpoch || sequence !== thisSequence) return;
    $('activity').textContent = error.name === 'AbortError' ? 'Request stopped. No answer released; please retry.' : error.message;
    interaction.signal('answer_withheld', lifecycleToken);
    state('uncertain', 'No answer released · retry or reset');
    orbEvent('evidence-gap', { requestId });
  } finally {
    clearTimeout(progress); clearTimeout(timeout);
  }
}

$('ask-form').addEventListener('submit', event => { event.preventDefault(); ask(); });
document.querySelectorAll('[data-demo]').forEach(button => button.addEventListener('click', () => {
  selectedId = button.dataset.demo === 'combat' ? 'combat' : 'county-legislator-1st-district-at-large';
  $('question').value = button.dataset.demo === 'combat' ? 'Explain COMBAT' : 'Compare Pollard and Fields priorities';
  renderInventory(); ask();
}));
$('question').addEventListener('input', () => { clearAudio(); selectedId = null; renderInventory(); });
$('search').addEventListener('input', renderInventory);
document.querySelectorAll('[data-kind]').forEach(button => button.addEventListener('click', () => {
  category = button.dataset.kind;
  document.querySelectorAll('[data-kind]').forEach(b => { b.classList.toggle('selected', b === button); b.setAttribute('aria-pressed', String(b === button)); });
  renderInventory();
}));
function resetVisitor() {
  const erasedSession = visitorSession, eraseEpoch = epoch + 1; visitorSession = crypto.randomUUID();
  fetch('/api/erase', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Oracle-Session': erasedSession }, body: '{}', keepalive: true }).then(response => { if (!response.ok) throw Error('Erase not confirmed'); }).catch(() => { if (epoch === eraseEpoch && !$('question').value) $('activity').textContent = 'Local content cleared. Server cancellation could not be confirmed; provider deletion is not promised.'; });
  epoch++; sequence++; controller?.abort(); clearAudio(); voiceClosing = true; $('mic').disabled = true; const resetEpoch = epoch; const closing = live.close(); live.discardVisitor(); voiceActive = false; $('mic').textContent = 'Speak'; state('ready', 'Ready for a question'); selectedId = null; latest = null;
  orbEvent('visitor-reset');
  $('question').value = ''; $('search').value = ''; $('authority').value = 'unknown'; $('location').value = '';
  $('answer-region').hidden = true; $('activity').textContent = 'Visitor content cleared. Voice connection teardown may still be finishing.'; $('speak').disabled = true;
  for (const id of ['choices', 'adaptive-card', 'roster', 'evidence', 'candidate-sources', 'links', 'limitations']) $(id).replaceChildren();
  $('answer-text').textContent = ''; $('trace').textContent = ''; document.querySelector('.conversation').classList.remove('has-answer','has-card'); $('browse').open = false; $('sources-disclosure').open = false; $('input-disclosure').open = true; $('type-summary').hidden = true; renderInventory(); $('question').focus();
  captureToken = null; answerToken = null;
  $('spoken-question').textContent = ''; $('spoken-question').hidden = true;
  closing.catch(() => {}).finally(() => { if (epoch === resetEpoch) { voiceClosing = false; interaction.configure({ voiceReady: Boolean(voiceReady) }); } });
  $('adaptive-card').removeAttribute('tabindex'); $('voice-stop').hidden = true;
  $('speech-status').textContent = ''; $('mic-note').textContent = voiceReady ? 'Microphone off. Start it explicitly to ask a question.' : 'Voice is off or its allowance is used. You can type.';
  return Promise.resolve();
}
$('reset').addEventListener('click', () => interaction.reset('accessible_control'));
$('speak').addEventListener('click', async () => {
  if (!latest?.speech) return;
  try {
    if (live.ready) { await live.play(); return; }
    liveEpoch = epoch; const request = latest.request_id;
    $('speak').disabled = true;
    if (speechTransport === 'websocket') { await live.prepareServer(latest, visitorSession); return; }
    await live.start({ microphone: false });
    if (latest?.request_id !== request) { await live.close(); return; }
    if (!live.evidenceContext(latest)) { await live.close(); throw new Error('Speech requires the same accepted answer and sources.'); }
  } catch (error) { $('speech-status').textContent = error.message; $('speak').disabled = !live.ready; if (live.ready) $('speak').textContent = 'Play answer'; }
});
async function beginVoice(token) {
  if (!interaction.valid(token) || !voiceReady || voiceActive || voiceClosing || live.closePromise) { interaction.signal('capture_failed', token); return; }
  captureToken = token; voiceActive = true; $('voice-stop').hidden = false; liveEpoch = epoch; const thisEpoch = epoch; $('mic').textContent = 'Stop GPT-Live';
  try {
    const health = await fetch('/api/health', { cache: 'no-store' }).then(r => r.json());
    if (!interaction.valid(token)) return;
    if (health.voice_session_available === false) { voiceReady = false; interaction.configure({ voiceReady: false }); throw new Error('Voice session allowance is used. Use text input.'); }
    await live.start();
  }
  catch (error) { if (epoch !== thisEpoch || !interaction.valid(token)) return; interaction.signal('capture_failed', token); voiceActive = false; $('mic').textContent = 'Speak'; $('activity').textContent = error.message; state('uncertain', 'Use text input'); }
}
$('mic').addEventListener('click', async () => {
  if (voiceActive) { await live.close(); return; }
  interaction.intent('accessible_control');
});
$('voice-stop').addEventListener('click', () => { clearAudio(); live.close(); interaction.signal('capture_failed', captureToken); voiceActive = false; $('voice-stop').hidden = true; $('mic').textContent = 'Speak'; $('activity').textContent = 'Microphone stopped.'; interaction.configure({ voiceReady: Boolean(voiceReady) }); });
window.addEventListener('pagehide', () => { live.cancelPlayback(); live.mute(); live.stream?.getTracks().forEach(t => t.stop()); live.send({ type: 'session.close' }); });

Promise.all([fetch('/api/inventory').then(r => r.json()), fetch('/api/health').then(r => r.json())])
  .then(([rows, health]) => {
    inventory = rows;
    speechTransport = health.speech_transport;
    $('operator-notice').textContent = 'Open Oracle · supervised prototype. ' + (health.operator_name ? 'Operator: ' + health.operator_name + '. ' : 'Operator not configured. ') + 'AI explanations can be wrong; check the source.';
    if (health.input_events?.enabled === true) { const bridge = new window.OracleInputBridge(window.OpenOracleInputs); bridge.start(); window.addEventListener('pagehide', () => bridge.stop(), { once: true }); }
    voiceReady = health.voice_session_available !== false && health.voice === 'gpt_live_buffered' && window.isSecureContext && navigator.mediaDevices?.getUserMedia;
    interaction.configure({ voiceReady: Boolean(voiceReady) });
    $('mic').disabled = !voiceReady;
    $('mic-note').textContent = voiceReady ? 'Speak sends your microphone audio to OpenAI for one question. Review it before submitting. Speech plays only after validation and your Play answer click.' : 'Voice is off. You can type your question.';
    $('count').textContent = `${health.counts.contests} printed contests · ${health.counts.candidates} nominees`;
    $('mode').textContent = health.mode === 'live_strands' ? 'Strands · exact evidence' : 'Exact-source mode';
    renderInventory();
    if (!Object.values(health.source_integrity).every(Boolean)) $('activity').textContent = 'A source version changed. Affected evidence is blocked pending reconciliation.';
  }).catch(() => { $('mode').textContent = 'Sources unavailable'; $('activity').textContent = 'Could not load the retained source inventory.'; });

window.addEventListener('keydown', event => { if (event.key === 'Escape' && voiceActive) { clearAudio(); live.close(); } });

$('adaptive-card').addEventListener('keydown', event => { if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return; const button = $('adaptive-card').querySelector('[data-part=\"' + (event.key === 'ArrowRight' ? '1' : '-1') + '\"]'); if (button && !button.disabled) { event.preventDefault(); button.click(); } });

async function showDataUse() {
  let details = $('privacy-draft');
  if (!details) { details = element('details'); details.id = 'privacy-draft'; details.append(element('summary', 'How your data is used')); $('operator-notice').parentElement.append(details); }
  if ($('how-it-works')) $('how-it-works').open = true; details.open = true;
  const summary = details.querySelector('summary'); summary.textContent = 'How your data is used'; summary.focus();
  const thisEpoch = epoch;
  try {
    const faq = await fetch('/api/data-use', { cache: 'no-store' }).then(r => { if (!r.ok) throw Error('Data-use details unavailable'); return r.json(); });
    if (epoch !== thisEpoch) return;
    details.replaceChildren(summary);
    for (const item of faq.items || []) details.append(element('h3', item.title), element('p', item.text));
    for (const source of faq.sources || []) details.append(safeLink(source.title + ' ↗', source.url));
  } catch { if (epoch === thisEpoch) $('activity').textContent = 'Could not load the current data-use facts. No provider-retention guarantee is made.'; }
}
$('example-privacy')?.addEventListener('click', showDataUse);
$('privacy-draft')?.addEventListener('toggle', () => { if ($('privacy-draft').open && $('privacy-draft').querySelector('summary').textContent !== 'How your data is used') showDataUse(); });

$('adaptive-card').addEventListener('keydown', event => { if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return; const button = $('adaptive-card').querySelector('[data-part=\"' + (event.key === 'ArrowRight' ? '1' : '-1') + '\"]'); if (button && !button.disabled) { event.preventDefault(); button.click(); } });


$('reset').textContent = 'Erase this session';
$('reset').setAttribute('aria-label', 'Erase this session');
$('reset').title = 'Stop local capture and playback and clear this session; provider erasure is not promised.';
const dataUseButton = element('button', 'Explain how my data is used', 'quiet'); dataUseButton.type = 'button'; dataUseButton.id = 'data-use'; dataUseButton.addEventListener('click', showDataUse); $('operator-notice').parentElement.append(dataUseButton);
