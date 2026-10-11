/* Shared nonvisual ingress. Application owns transport, sources and lifecycle.
 * No controller, identity minting, provider, DOM, speech or frontend tool. */
(function(root) {
  'use strict';
  const FACT_KEYS = ['decision','rate','time','purpose','fund'];
  const COMPONENTS = ['measure_parts','measure_focus','candidate_quotes','source_quotes'];
  const ROOT_FIELDS = new Set(('request_id status answer mode review fact_validation card evidence view_plan source_fallback requested_parts comparison_request scope snapshot_date election_date language translation_status claims choices links candidate_sources limitations contest required_scope public_display display_contract speech readability elapsed_ms stage_ms operational_receipt trace integration_error').split(' '));
  const MODES = ['exact_source','live_strands','reviewed_strands_research'];
  const STATUSES = ['answered','unavailable','clarification','clarification_needed','insufficient_evidence','conflict','neutrality_boundary','official_links'];
  class ContractError extends Error {}
  const fail = code => { throw new ContractError(code); };
  function json(value, depth=0) {
    if (depth>24) fail('projection_depth');
    if (value===null || typeof value==='string' || typeof value==='boolean') return value;
    if (typeof value==='number' && Number.isFinite(value)) return value;
    if (Array.isArray(value)) { if(value.length>256) fail('projection_size'); return value.map(v=>json(v,depth+1)); }
    if (!value || typeof value!=='object' || ![Object.prototype,null].includes(Object.getPrototypeOf(value))) fail('plain_json_required');
    const descriptors=Object.getOwnPropertyDescriptors(value), out={};
    for(const key of Reflect.ownKeys(descriptors)) {
      if(typeof key!=='string'||['__proto__','constructor','prototype'].includes(key)||!('value' in descriptors[key])) fail('plain_json_required');
      out[key]=json(descriptors[key].value,depth+1);
    }
    return out;
  }
  function canonical(value) {
    if(Array.isArray(value)) return '['+value.map(canonical).join(',')+']';
    if(value&&typeof value==='object') return '{'+Object.keys(value).sort().map(k=>JSON.stringify(k)+':'+canonical(value[k])).join(',')+'}';
    return JSON.stringify(value);
  }
  const equal=(a,b)=>canonical(a)===canonical(b);
  function freeze(value) { if(value&&typeof value==='object') { Object.values(value).forEach(freeze); Object.freeze(value); } return value; }
  function object(value, code) { if(!value||typeof value!=='object'||Array.isArray(value)) fail(code); return value; }
  function text(value,code,max=60000) { if(typeof value!=='string'||!value.length||value.length>max) fail(code); return value; }
  function array(value,code,max=64) { if(!Array.isArray(value)||value.length>max) fail(code); return value; }
  function keys(value,allowed,code) { object(value,code); if(Object.keys(value).some(k=>!allowed.includes(k))) fail(code); }
  function synchronous(fn,...args) { const result=fn(...args); if(result&&typeof result.then==='function') fail('synchronous_owner_required'); return result; }
  function current(owner,ticket) { return synchronous(owner,ticket)===true; }
  function safeUrl(value) {
    if(typeof value!=='string'||/[\x00-\x20\\]/.test(value)) return false;
    if(/^\/api\/(original|candidate-original|prepared-source)\/[A-Za-z0-9][A-Za-z0-9._-]*(?:#page=\d+)?$/.test(value)) return true;
    try { const u=new URL(value); return u.protocol==='https:'&&!u.username&&!u.password&&u.hostname!==''; } catch { return false; }
  }
  function sourceSpan(source,span) {
    if(!source||!span||span.evidence_id!==source.id||!Number.isInteger(span.start)||!Number.isInteger(span.end)||span.start<0||span.end<=span.start) return false;
    const points=Array.from(source.text);
    return span.end<=points.length&&points.slice(span.start,span.end).join('')===span.quote;
  }
  function bindSource(source,trust) {
    object(source,'invalid_evidence'); text(source.id,'invalid_evidence_id',120);
    const retained=synchronous(trust.source,source.id);
    if(!retained||!equal(source,retained)) fail('source_binding_failed');
    if(source.status!=='current_snapshot'||!safeUrl(source.url)||!safeUrl(source.original_route)) fail('source_metadata_failed');
    text(source.text,'missing_original'); text(source.sha256,'missing_source_hash',64);
  }
  function validateCard(r,trust) {
    const card=r.card; if(card===null) return;
    object(card,'invalid_card'); const reference=synchronous(trust.card,text(card.id,'invalid_card_id',120));
    if(!reference||reference.type!==card.type) fail('unregistered_card');
    if(card.contest_id!==r.contest?.id) fail('card_contest_binding');
    if(card.type==='measure_explanation') {
      const {facets,presentation,facet_keys,...metadata}=card;
      const {facets:expected,presentation:_p,facet_keys:_k,...expectedMetadata}=reference;
      if(!equal(metadata,expectedMetadata)||!['overview','step_by_step','choice_focus'].includes(presentation)) fail('card_metadata_binding');
      const supportedKeys=reference.facet_keys||FACT_KEYS, selected=facet_keys||FACT_KEYS;
      if(!Array.isArray(selected)||!selected.length||new Set(selected).size!==selected.length||selected.some(k=>!supportedKeys.includes(k))) fail('card_facet_keys');
      if(!Array.isArray(facets)||facets.length!==selected.length) fail('card_facet_count');
      const primary=r.evidence.find(e=>e.id===card.evidence_id);
      if(!primary||primary.sha256!==card.source_sha256||primary.url!==card.source_url||primary.election_date!==card.election_date) fail('card_source_binding');
      // Validate ALL facets before plan selection, including combined rate/time.
      facets.forEach((f,i)=>{
        if(!equal(f,expected[supportedKeys.indexOf(selected[i])])||!sourceSpan(r.evidence.find(s=>s.id===f.evidence_id),f)) fail('facet_span_binding');
      });
    } else if(card.type==='candidate_comparison') {
      const {sections,...base}=card;
      if(!equal(base,reference)) fail('candidate_card_binding');
      const selected=sections||[base];
      if(selected.length<1||selected.length>2) fail('candidate_sections');
      if(sections&&(!equal(selected.map(s=>s.topic),r.comparison_request?.topics)||selected[0].title!==card.title||!equal(selected[0].responses,card.responses))) fail('candidate_coverage');
      const ids=[];
      for(const section of selected) {
        const known=section.topic===base.topic?reference:synchronous(trust.card,'atlarge-1-'+section.topic+'-v1');
        if(!known||!equal(section,{topic:known.topic,title:known.title,responses:known.responses})&&sections) fail('candidate_section_binding');
        if(section.responses.length!==2||new Set(section.responses.map(v=>v.candidate_name)).size!==2) fail('candidate_pair');
        for(const v of section.responses) {
          const source=r.evidence.find(e=>e.id===v.evidence_id);
          if(!r.contest.candidates?.some(c=>c.name===v.candidate_name&&c.party===v.party)||!source||source.topic!==section.topic||source.question!==section.title||source.candidate_name!==v.candidate_name||source.text!==v.quote||source.passage_sha256!==v.passage_sha256) fail('candidate_source_binding');
          ids.push(v.evidence_id);
        }
      }
      if(new Set(ids).size!==ids.length||ids.length!==r.evidence.length||r.evidence.some(e=>!ids.includes(e.id))) fail('candidate_coverage');
    } else fail('unregistered_card');
  }
  function validatePlan(plan,r) {
    keys(plan,['version','request_id','component','evidence_ids','facet_keys','initial_part','language'],'view_plan_fields');
    if(plan.version!==1||plan.request_id!==r.request_id||plan.language!=='en'||!COMPONENTS.includes(plan.component)||!Number.isInteger(plan.initial_part)||plan.initial_part<0||plan.initial_part>4) fail('view_plan_identity');
    const sources=r.source_fallback?.sources||r.evidence;
    if(!sources.length||sources.length>(r.contest?.id==='amendment-7'?5:4)||!equal(plan.evidence_ids,sources.map(e=>e.id))) fail('view_plan_sources');
    array(plan.facet_keys,'view_plan_facets',5);
    if(plan.component==='source_quotes') { if(r.card||plan.facet_keys.length||plan.initial_part!==0) fail('source_quotes_plan'); return; }
    if(r.status!=='answered'||r.fact_validation.status!=='supported'||!r.card) fail('unreleased_card_plan');
    if(plan.component==='candidate_quotes') { if(r.card.type!=='candidate_comparison'||plan.facet_keys.length||plan.initial_part!==0) fail('candidate_plan'); return; }
    if(r.card.type!=='measure_explanation') fail('measure_plan');
    const cardKeys=r.card.facet_keys||FACT_KEYS;
    if(plan.component==='measure_parts') { if(!equal(plan.facet_keys,cardKeys)||plan.initial_part!==0) fail('measure_parts_plan'); }
    else if(equal(plan.facet_keys,['rate','time'])) {
      if(!cardKeys.includes('rate')||!cardKeys.includes('time')||plan.initial_part!==1||!r.requested_parts?.includes('rate')||!r.requested_parts?.includes('duration')) fail('combined_plan');
    } else if(plan.facet_keys.length!==1||!cardKeys.includes(plan.facet_keys[0])||plan.initial_part!==cardKeys.indexOf(plan.facet_keys[0])) fail('measure_focus_plan');
  }
  function validateProjection(input,expectation,trust) {
    const r=json(input);
    if(canonical(r).length>750000) fail('projection_size');
    object(r,'response_required');
    if(Object.keys(r).some(k=>!ROOT_FIELDS.has(k))) fail('unknown_transport_field');
    if(r.request_id!==expectation.request_id) fail('request_mismatch');
    text(r.answer,'answer_required');
    if(!MODES.includes(r.mode)||!STATUSES.includes(r.status)) fail('unsupported_mode_or_status');
    if(r.language!=='en'||r.translation_status!=='not_requested'||expectation.language!=='en') fail('unreleased_language');
    if(!equal(r.scope,expectation.scope)) fail('scope_mismatch');
    if(typeof r.election_date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(r.election_date)||typeof r.snapshot_date!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(r.snapshot_date)) fail('source_dates_required');
    object(r.review,'review_required'); text(r.review.label,'review_label_required',2000);
    if(!['not_run','accepted','rejected','unavailable'].includes(r.review.status)) fail('review_status');
    object(r.fact_validation,'fact_validation_required');
    if(!['supported','not_applicable','unsupported','contradictory'].includes(r.fact_validation.status)) fail('fact_validation_status');
    array(r.evidence,'evidence_required',r.contest?.id==='amendment-7'?5:4); array(r.claims,'claims_required',32);
    array(r.choices,'choices_required'); array(r.links,'links_required'); array(r.candidate_sources,'candidate_sources_required');
    array(r.limitations,'limitations_required').forEach(v=>text(v,'invalid_limitation',6000));
    if(r.card===undefined||r.view_plan===undefined) fail('card_plan_required');
    const reviewed=r.review.status==='accepted'&&r.review.execution==='real_api';
    if(r.mode==='exact_source'&&r.review.status==='accepted'&&!reviewed) fail('authored_review_not_live');
    if(r.mode==='live_strands'&&!reviewed&&r.status!=='unavailable') fail('review_required_for_live');
    if(r.status==='answered'&&(!['not_run','accepted'].includes(r.review.status)||r.fact_validation.status!=='supported')) fail('factual_release_gate');
    if(r.evidence.length&&new Set(r.evidence.map(s=>s.id)).size!==r.evidence.length) fail('duplicate_evidence');
    r.evidence.forEach(s=>bindSource(s,trust));
    if(r.evidence.some(s=>s.election_date!==r.election_date||s.snapshot_date!==r.snapshot_date)) fail('source_version_binding');
    if(r.contest) {
      const retained=synchronous(trust.contest,r.contest.id);
      if(!retained||!equal(retained,r.contest)||expectation.contest_id&&r.contest.id!==expectation.contest_id) fail('contest_binding');
      if(r.evidence.some(s=>s.contest_id!==r.contest.id||s.election_date!==r.election_date)) fail('evidence_scope_binding');
    } else if(r.evidence.length&&r.mode!=='reviewed_strands_research') fail('contest_required');
    if(r.status==='answered'&&r.election_date!==expectation.scope.election_date) fail('election_mismatch');
    if(!['not_run','accepted'].includes(r.review.status)&&(r.card||r.evidence.length||r.claims.length||r.candidate_sources.length)) fail('withheld_content');
    if(r.mode==='reviewed_strands_research') {
      if(!reviewed||r.display_contract!=='source_bound_research_browser_v1'||r.public_display!==true||r.fact_validation.status!=='supported'||r.card||r.view_plan||r.source_fallback||r.speech||typeof trust.researchDisplay!=='function'||synchronous(trust.researchDisplay,r)!==true) fail('research_display_gate');
    } else {
      r.claims.forEach(c=>{
        const source=r.evidence.find(e=>e.id===c.evidence_id);
        if(!source||typeof c.quote!=='string'||(c.start===undefined?c.quote!==source.text:!sourceSpan(source,c))) fail('claim_span_binding');
      });
      validateCard(r,trust);
    }
    if(r.source_fallback) {
      const f=r.source_fallback;
      keys(f,['type','request_id','contest_id','election_date','scope','sources','source_bindings','label','candidate_statement_limit'],'fallback_fields');
      if(f.type!=='verified_originals'||f.request_id!==r.request_id||f.contest_id!==r.contest?.id||f.election_date!==r.election_date||!equal(f.scope,r.scope)||r.status!=='unavailable'||r.card||r.evidence.length||r.claims.length) fail('fallback_binding');
      array(f.sources,'fallback_sources',4); if(!f.sources.length||new Set(f.sources.map(s=>s.id)).size!==f.sources.length) fail('fallback_sources');
      f.sources.forEach(s=>{bindSource(s,trust);if(s.contest_id!==f.contest_id||s.election_date!==r.election_date||s.snapshot_date!==r.snapshot_date||f.source_bindings?.[s.id]!==synchronous(trust.sourceFingerprint,s.id)) fail('fallback_source_binding');});
      if(!equal(Object.keys(f.source_bindings).sort(),f.sources.map(s=>s.id).sort())) fail('fallback_source_binding');
      text(f.label,'fallback_label');text(f.candidate_statement_limit,'fallback_limit');
    }
    r.choices.forEach(c=>{ keys(c,['id','title'],'choice_fields'); const known=synchronous(trust.contest,c.id); if(!known||c.title!==known.title) fail('choice_binding'); });
    r.links.forEach(link=>{keys(link,['title','url'],'link_fields'); if(!safeUrl(link.url)||!trust.officialLinks.some(v=>equal(v,link))&&!r.evidence.some(s=>s.original_route===link.url)) fail('link_binding');});
    r.candidate_sources.forEach(c=>{if(typeof trust.candidateSource!=='function'||!equal(c,synchronous(trust.candidateSource,c.candidate_id))) fail('candidate_catalog_binding');});
    if(r.required_scope) {keys(r.required_scope,['field','value'],'required_scope_fields');if(!['district','municipality'].includes(r.required_scope.field)||r.required_scope.value!==r.contest?.required_location) fail('required_scope_binding');}
    if(r.requested_parts) { array(r.requested_parts,'requested_parts',3); if(new Set(r.requested_parts).size!==r.requested_parts.length||r.requested_parts.some(k=>!['rate','duration','prediction'].includes(k))) fail('requested_parts'); }
    if(r.comparison_request) {
      const c=r.comparison_request;
      keys(c,['topics','gaps','unclassified'],'comparison_fields');array(c.topics,'comparison_topics',2);array(c.gaps,'comparison_gaps');
      if(!c.topics.length||new Set(c.topics).size!==c.topics.length||c.topics.some(k=>!['issues','property'].includes(k))||new Set(c.gaps).size!==c.gaps.length||c.gaps.some(k=>!['climate','crime','abortion','immigration','records and experience','stadiums and sports','sales taxes','endorsements','other_requested_topic'].includes(k))||typeof c.unclassified!=='boolean') fail('comparison_fields');
      if(r.card?.type==='candidate_comparison'&&!equal(c.topics,(r.card.sections||[r.card]).map(s=>s.topic))) fail('candidate_coverage');
    }
    if(r.view_plan!==null) validatePlan(r.view_plan,r);
    if(r.card&&r.view_plan===null) fail('card_plan_required');
    const output={};
    for(const k of ['request_id','status','answer','mode','card','evidence','view_plan','source_fallback','requested_parts','comparison_request','scope','snapshot_date','election_date','language','translation_status','choices','links','candidate_sources','contest','required_scope']) if(k in r) output[k]=r[k];
    // Operational/provider/claim/reviewer diagnostics are never renderer certainty.
    output.review={status:r.review.status,label:r.review.label,...(r.review.execution?{execution:r.review.execution}:{})};
    output.fact_validation={status:r.fact_validation.status}; output.limitations=r.limitations;
    // Voice owner consumes the original transport through its separate receipt gate.
    output.speech=false;
    return freeze(output);
  }
  class AcceptedStore {
    constructor({isCurrent,trust}) { if(typeof isCurrent!=='function'||!trust||['source','contest','card','sourceFingerprint'].some(k=>typeof trust[k]!=='function')||!Array.isArray(trust.officialLinks)) fail('application_bindings_required'); this.owner=isCurrent;this.trust=trust;this.pending=null;this.accepted=null; }
    begin(ticket,context) {
      const t=freeze(json(ticket)), e=freeze(json({...context,request_id:t.request_id}));
      text(t.request_id,'request_identity_required',120);object(e.scope,'scope_required');
      if(!current(this.owner,t)) fail('stale_owner_ticket');
      if(this.pending&&equal(t,this.pending.ticket)) {
        if(!equal(e,this.pending.expectation)) fail('reused_request_context');
        return this.snapshot();
      }
      this.pending={ticket:t,expectation:e,installed:null}; return this.snapshot();
    }
    install(raw,ticket) {
      try {
        const pending=this.pending,t=json(ticket);
        if(!pending||!equal(t,pending.ticket)||!current(this.owner,pending.ticket)) fail('stale_result');
        const response=validateProjection(raw,pending.expectation,this.trust);
        // Recheck after resolvers: synchronous callbacks can invalidate the owner.
        if(this.pending!==pending||!current(this.owner,pending.ticket)) fail('stale_result');
        if(pending.installed&&!equal(response,pending.installed)) fail('conflicting_result_replay');
        if(!pending.installed) { pending.installed=response;this.accepted=response; }
        return {ok:true,response:this.accepted};
      } catch(error) { return {ok:false,reason:error instanceof ContractError?error.message:'binding_or_owner_failure'}; }
    }
    descriptor(raw,status,ticket) {
      try {
        const pending=this.pending,plan=json(raw),t=json(ticket);
        if(status!=='complete'||!pending?.installed||!equal(t,pending.ticket)||!current(this.owner,pending.ticket)||!equal(plan,pending.installed.view_plan)) return null;
        validatePlan(plan,pending.installed);
        return this.pending===pending?pending.installed.view_plan:null;
      } catch { return null; }
    }
    invalidate(reason,{erase=false}={}) { text(reason,'invalidation_reason',120);this.pending=null;if(erase)this.accepted=null;return this.snapshot(); }
    snapshot() { return Object.freeze({accepted:this.accepted,pending_request_id:this.pending?.ticket.request_id||null}); }
  }
  const api=Object.freeze({AcceptedStore,validateProjection,sourceSpan,safeUrl});
  if(typeof module!=='undefined'&&module.exports) module.exports=api; else root.OpenOracleReleaseStore=api;
})(typeof window==='undefined'?globalThis:window);
