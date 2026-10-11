/* Private intake transport and native interaction. No theme, civic release or media. */
(() => {
  'use strict';
  const uuid = () => crypto.randomUUID();
  const element = (tag, text, props = {}) => Object.assign(document.createElement(tag), props, text === null ? {} : {textContent: text});
  function createOwner() {
    let epoch = 0, sequence = 0, session = uuid(), active = null, serverWork = false;
    const invalidate = () => { active?.controller.abort(); active = null; sequence++; };
    return Object.freeze({
      get session() { return session; },
      invalidate,
      next() {
        invalidate();
        const controller = new AbortController();
        const ticket = Object.freeze({request_id: uuid(), epoch, sequence});
        const step = {ticket, session, controller}; active = step;
        return Object.freeze({ticket, session, signal: controller.signal,
          current: () => active === step && !controller.signal.aborted && step.session === session});
      },
      markServerWork() { serverWork = true; },
      async erase() {
        const old = session, needed = serverWork;
        invalidate(); epoch++; session = uuid(); serverWork = false;
        if (!needed) return true;
        try {
          const response = await fetch('/api/erase', {method: 'POST', headers: {'Content-Type': 'application/json', 'X-Oracle-Session': old}, body: '{}', keepalive: true});
          return response.ok;
        } catch { return false; }
      }
    });
  }
  function mount(form, owner) {
    if (!form || form.dataset.intakeMounted) return;
    form.dataset.intakeMounted = 'true';
    const wording = form.querySelector('#ballot-wording'), file = form.querySelector('#ballot-file');
    const status = form.querySelector('#evaluator-status'), submit = form.querySelector('#read-ballot');
    const clear = form.querySelector('#clear-wording'), cancel = form.querySelector('#cancel-intake'), count = form.querySelector('#wording-count'), limit = form.querySelector('#wording-limit');
    let doc = null, documentId = null, revision = 0, busy = false, enabled = false, pageGone = false, inputRevision = 0;
    const panel = element('section', null, {id: 'intake-selection', hidden: true});
    const heading = element('h2', 'Choose complete wording');
    const admission = element('p', 'Supplied wording · source language unknown · source unverified. No AI explanation, translation or speech is authorized by this preview.');
    const blockLabel = element('label', 'Select a complete block', {htmlFor: 'intake-block'});
    const blocks = element('select', null, {id: 'intake-block'});
    const review = element('details', null, {id: 'intake-extracted'});
    review.append(element('summary', 'Review extracted wording'));
    const original = element('blockquote', '', {className: 'quote', id: 'intake-original'});review.append(original);
    const warnings = element('p', '', {id: 'intake-warnings'});
    const complete = element('input', null, {type: 'checkbox', id: 'intake-complete'});
    const completeLabel = element('label', ' I checked that this selection contains the complete question and its conditions.', {htmlFor: complete.id});
    const completeLine = element('p', null);completeLine.append(complete, completeLabel);
    const english = element('input', null, {type: 'checkbox', id: 'intake-english'});
    const englishLabel = element('label', ' Use an English formula estimate. The source language has not been verified.', {htmlFor: english.id});
    const englishLine = element('p', null);englishLine.append(english, englishLabel);
    const calculate = element('button', 'Select wording and check readability', {type: 'button', id: 'intake-calculate', disabled: true});
    const output = element('section', null, {id: 'intake-result', hidden: true});
    panel.append(heading, admission, blockLabel, blocks, review, warnings, completeLine, englishLine, calculate, output);
    form.append(panel);
    status.setAttribute('role', 'status');status.setAttribute('aria-live', 'polite');
    const tell = text => {status.textContent = text;};
    const humanReason = reason => ({
      no_pdf_text_ocr_unavailable: 'This PDF has no extracted text. OCR is unavailable; paste a complete question instead.',
      incomplete_pdf_text: 'Some PDF pages have no text. Review the original and paste the complete question; selection is held.',
      empty_text: 'No wording was found. Supply a complete question.',
      preview_already_pending: 'Discard or erase the previous preview before reading another.',
      complete_question_confirmation_required: 'Review the complete wording and confirm it includes all conditions.',
      owner_changed: 'The input changed. This result was discarded.',
    }[reason] || reason?.replaceAll('_', ' ') || 'Private preview unavailable. No answer or source accepted.');
    function updateCount() {
      const n = Array.from(wording.value).length;
      count.textContent = `${n.toLocaleString()} / 80,000 characters`;
      const tooLong = n > 80000 || new TextEncoder().encode(wording.value).length > 256 * 1024;
      limit.hidden = !tooLong;wording.setAttribute('aria-invalid', String(tooLong));
      submit.disabled = !enabled || busy || tooLong;
      cancel.hidden = !busy;
      calculate.disabled = busy || !doc || doc.status !== 'ready_for_selection' || !complete.checked;
    }
    function clearReading() { doc = null; documentId = null; revision = 0; panel.hidden = true; output.hidden = true; output.replaceChildren(); original.textContent = ''; blocks.replaceChildren(); complete.checked = false; english.checked = false; }
    async function sourceChanged() {
      const change = ++inputRevision;
      owner.invalidate();busy = false;clearReading();updateCount();
      const confirmed = await owner.erase();
      if (change === inputRevision && !pageGone) tell(confirmed ? 'Previous preview cleared. Read the new wording when ready.' : 'Local preview cleared; server Erase could not be confirmed. No provider deletion is promised.');
    }
    async function request(path, body, step, binary = false, contentType = '') {
      owner.markServerWork();
      const headers = {'X-Oracle-Session': step.session, 'Content-Type': binary ? contentType : 'application/json'};
      if (binary) headers['X-Oracle-Intake'] = JSON.stringify({owner_ticket: step.ticket, expected_revision: revision});
      const response = await fetch(path, {method: 'POST', headers, body: binary ? body : JSON.stringify(body), signal: step.signal});
      const result = await response.json();
      if (!step.current() || pageGone) throw new DOMException('Discarded', 'AbortError');
      if (!response.ok) throw Error(humanReason(result.error));
      return result;
    }
    function bind(result, step) {
      const got = result.binding?.owner_ticket || result.owner_ticket || result.document?.owner_ticket;
      if (got && (got.request_id !== step.ticket.request_id || got.epoch !== step.ticket.epoch || got.sequence !== step.ticket.sequence || Object.keys(got).length !== 3)) throw Error('Private result belongs to another request; discarded.');
    }
    async function read(event) {
      event.preventDefault();
      if (!enabled || busy) return;
      if (file.files.length && wording.value.trim()) { tell('Choose a file or pasted wording, then read it.');return; }
      if (!file.files.length && !wording.value.trim()) { tell('Upload PDF/TXT or paste a complete question.');wording.focus();return; }
      busy = true;panel.hidden = true;output.hidden = true;updateCount();tell('Reading supplied wording locally…');
      const input = inputRevision, step = owner.next();
      try {
        let prepared;
        if (file.files.length) {
          const chosen = file.files[0];
          const pdf = chosen.type === 'application/pdf' || /\.pdf$/i.test(chosen.name);
          if (!pdf && !/\.txt$/i.test(chosen.name) && chosen.type !== 'text/plain') throw Error('Only PDF or UTF-8 TXT files are accepted.');
          if (chosen.size > (pdf ? 5*1024*1024 : 256*1024)) throw Error('File exceeds the PDF 5 MiB or TXT 256 KiB limit. Keep the complete wording.');
          const raw = await chosen.arrayBuffer();if (!step.current()) return;
          prepared = await request('/api/intake/upload', raw, step, true, pdf ? 'application/pdf' : 'text/plain');
        } else prepared = await request('/api/intake/prepare', {text: wording.value, owner_ticket: step.ticket, expected_revision: revision}, step);
        bind(prepared, step);
        if (!step.current()) return;
        // Synchronously invalidate existing local work before the fresh commit ticket.
        const commit = owner.next();
        const accepted = await request('/api/intake/commit', {prepared_id: prepared.prepared_id, owner_ticket: commit.ticket, expected_revision: revision}, commit);
        bind(accepted, commit);if (!commit.current()) return;
        doc = accepted.document;documentId = accepted.document_id;revision = accepted.document_revision;
        original.textContent = doc.text;blocks.replaceChildren();complete.checked = false;english.checked = false;
        for (const block of doc.questions) blocks.append(element('option', block.block_id === 'whole' ? 'Whole document · not a per-question score' : `Detected block ${block.block_id.slice(1)} · review its full wording`, {value: block.block_id}));
        warnings.textContent = doc.warnings.map(humanReason).join('. ');
        panel.hidden = false;
        tell(doc.status === 'ready_for_selection' ? 'Wording extracted. Source and language remain unverified. Choose and review a complete block.' : humanReason(prepared.reason));
        busy = false;updateCount();if (doc.status === 'ready_for_selection') blocks.focus();
      } catch (error) { if (error.name !== 'AbortError' && input === inputRevision && !pageGone) tell(error.message || 'Private preview unavailable.'); }
      finally { if (input === inputRevision && !pageGone) {busy = false;updateCount();} }
    }
    async function select() {
      if (!doc || busy || !complete.checked) return;
      const step = owner.next(), input = inputRevision, source = doc, ident = documentId;
      busy = true;output.hidden = true;updateCount();tell('Checking the selected wording and formula…');
      try {
        const result = await request('/api/intake/select', {document_id: ident, expected_revision: revision, block_id: blocks.value, confirmed_complete: true,
          method_language_assumption: english.checked ? 'en' : null, owner_ticket: step.ticket}, step);
        bind(result, step);
        const binding = result.binding;
        if (binding.document_id !== ident || binding.document_revision !== revision || binding.block_id !== blocks.value || result.source_locale !== 'unknown' || result.provenance !== 'unverified_user_content'
            || Array.from(source.text).slice(binding.start, binding.end).join('') !== result.quote || result.speech !== false || result.translation !== 'blocked') throw Error('Private selection failed its original-wording binding.');
        if (!step.current()) return;
        const diagnostic = result.readability;output.replaceChildren();
        output.append(element('h3', diagnostic.label), element('p', diagnostic.qualifier, {id: 'intake-assumption'}));
        if (diagnostic.scope === 'whole_document') output.append(element('p', 'Whole-document diagnostic, not a per-question score.'));
        if (diagnostic.status === 'calculated_under_assumption') {
          const scores = diagnostic.report?.scores;
          if (!scores || !Object.values(scores).every(Number.isFinite) || diagnostic.report.raw_text_sha256 !== binding.quote_sha256) throw Error('Formula result unavailable; no valid score.');
          const list = element('dl', null, {id: 'intake-scores'});
          for (const [key, value] of Object.entries(scores)) list.append(element('dt', key === 'flesch_reading_ease' ? 'Flesch Reading Ease estimate' : key === 'flesch_kincaid_grade_level' ? 'Flesch–Kincaid grade-level formula estimate' : key), element('dd', String(value)));
          output.append(list);
        } else output.append(element('p', diagnostic.status === 'unsupported' ? 'No score: this formula was not selected or does not support the wording. No language detection, accent stripping or translation was applied.' : diagnostic.status === 'empty' ? 'No words to calculate. Scores are undefined, not zero.' : 'The formula is unavailable; no score was produced.'));
        output.append(element('p', 'Decisions clarity review: not run. This diagnostic is separate from source verification and AI explanation.'));
        const exact = element('details', null);exact.append(element('summary', 'Selected complete wording'), element('blockquote', result.quote, {className: 'quote', id: 'intake-selected-quote'}));output.append(exact);
        if (diagnostic.report) {
          const method = element('details', null);method.append(element('summary', 'Formula, counts and limitations'));
          method.append(element('p', diagnostic.report.method?.variables || ''));
          if (diagnostic.report.counts) method.append(element('p', `${diagnostic.report.counts.words} words; ${diagnostic.report.counts.sentences} sentences; ${diagnostic.report.counts.syllables} syllables.`));
          for (const warning of [...diagnostic.report.warnings, ...diagnostic.report.limitations]) method.append(element('p', warning));output.append(method);
        }
        output.hidden = false;tell(diagnostic.status === 'calculated_under_assumption' ? 'English formula estimate ready. Source language remains unknown and source remains unverified.' : 'Selection saved privately. No readable score or AI answer has been authorized.');
      } catch (error) { if (error.name !== 'AbortError' && step.current() && !pageGone) tell(error.message || 'Private calculation unavailable.'); }
      finally { if (input === inputRevision && !pageGone) {busy = false;updateCount();} }
    }
    form.addEventListener('submit', read);
    wording.addEventListener('input', () => {sourceChanged();updateCount();});
    file.addEventListener('change', sourceChanged);
    for (const control of [blocks, complete, english]) control.addEventListener('change', () => {owner.invalidate();output.hidden = true;output.replaceChildren();updateCount();});
    calculate.addEventListener('click', select);
    cancel.addEventListener('click', async () => {
      const change = ++inputRevision;owner.invalidate();busy = false;clearReading();updateCount();
      const erased = await owner.erase();
      if (change === inputRevision && !pageGone) tell(erased ? 'Preview cancelled and cleared. Your input stays here for a deliberate new Read ballot.' : 'Preview cancelled locally; server cancellation could not be confirmed. No provider deletion is promised.');
    });
    clear.addEventListener('click', async () => {
      wording.value = '';file.value = '';const change = ++inputRevision;owner.invalidate();busy = false;clearReading();updateCount();wording.focus();
      const erased = await owner.erase();if (change === inputRevision && !pageGone) tell(erased ? 'Session erased locally. Provider deletion is not promised.' : 'Local content cleared. Server Erase could not be confirmed; provider deletion is not promised.');
    });
    window.addEventListener('pagehide', () => {pageGone = true;owner.invalidate();clearReading();wording.value = '';file.value = '';owner.erase();});
    fetch('/api/health').then(r => r.json()).then(health => {if (pageGone) return;enabled = health.intake?.enabled === true;updateCount();tell(enabled ? 'Private local PDF/TXT or paste preview is ready. Source, language and meaning remain unverified.' : 'Private intake is off on this server. The retained-source demo remains available.');}).catch(() => {if (!pageGone) tell('Could not connect to private intake. No wording sent.');});
    updateCount();
  }
  window.OpenOracleIntake = Object.freeze({createOwner, mount});
})();
