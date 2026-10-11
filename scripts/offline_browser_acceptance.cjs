const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const{chromium}=require('/opt/homebrew/lib/node_modules/promptfoo/node_modules/playwright');
const url=process.argv[2], output=process.argv[3];
if(!/^http:\/\/127\.0\.0\.1:[0-9]+$/.test(url)||!output)throw Error('Use an owned exact-source loopback server and an evidence directory');
fs.mkdirSync(output,{recursive:true});let browser;
(async()=>{
 browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const reports=[];
 for(const route of ['/','/copilot']){
  const page=await browser.newPage({viewport:{width:800,height:480},reducedMotion:'reduce'});const errors=[],external=[];let liveRequests=0;
  page.on('pageerror',e=>errors.push(e.message));await page.addInitScript(()=>{window.captureCalls=0;navigator.mediaDevices.getUserMedia=()=>{window.captureCalls++;throw Error('Capture forbidden in offline readiness')};});
  await page.route('**/*',r=>{const link=r.request().url();if(!link.startsWith(url)){external.push(link);return r.abort()}if(link.includes('/api/live/')){liveRequests++;return r.abort()}return r.continue()});
  await page.goto(url+route);const input=page.locator(route==='/'?'#question':'#copilot-question'),submit=route==='/'?page.locator('#ask-form button[type=submit]'):page.getByRole('button',{name:'Show evidence',exact:true});await input.waitFor();await page.waitForFunction(()=>!document.querySelector('button[type=submit]').disabled);
  const health=await(await page.request.get(url+'/api/health')).json();assert.equal(health.mode,'exact_source');assert.equal(health.voice,'not_connected');assert.ok(Object.values(health.source_integrity).every(Boolean));
  async function ask(question){
   if(!await input.isVisible())await page.getByText('Ask another question',{exact:true}).click();await input.fill(question);
   const responsePromise=page.waitForResponse(r=>r.url().endsWith(route==='/'?'/api/ask':'/api/ag-ui'));
   await input.press('Tab'); // keyboard reaches the next usable control, never a hidden voice action.
   await submit.focus();await page.keyboard.press('Enter');const response=await responsePromise;assert.equal(response.status(),200);
   let result;if(route==='/')result=await response.json();else{const events=(await response.text()).split('\n').filter(x=>x.startsWith('data: ')).map(x=>JSON.parse(x.slice(6)));result=events.find(e=>e.type==='STATE_SNAPSHOT').snapshot.response}
   if(result.card)await page.locator('.explanation-card').waitFor();else {await page.waitForFunction(text=>document.body.textContent.includes(text),result.answer);await page.waitForFunction(()=>!document.querySelector('.explanation-card'));}return result;
  }
  const rate=await ask('What is the COMBAT tax rate?');assert.equal(rate.review.status,'not_run');assert.equal(rate.fact_validation.status,'supported');assert.equal(rate.election_date,'2026-11-03');assert.ok(rate.evidence.length===1);
  if(route==='/'){await page.locator('#full-answer-reading summary').focus();await page.keyboard.press('Enter');await page.locator('#answer-text').waitFor();assert.equal(await page.locator('#answer-text').textContent(),rate.answer);assert.equal(await page.locator('#mic').isDisabled(),true);assert.equal(await page.locator('#speak').isVisible(),false)}
  else assert.match(await page.locator('.explanation-card').textContent(),/printed tax rate is one-quarter/);
  const sourceSummary=page.getByText('Sources (1) and limits',{exact:true});await sourceSummary.focus();await page.keyboard.press('Enter');await page.locator('.source-disclosure .quote').waitFor();assert.equal(await page.locator('.source-disclosure .quote').textContent(),rate.evidence[0].text);
  const original=rate.evidence[0];const pdf=await page.request.get(url+original.original_route);assert.equal(pdf.status(),200);assert.equal(crypto.createHash('sha256').update(await pdf.body()).digest('hex'),original.sha256);
  await sourceSummary.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.explanation-card').count(),1);
  let amendment;
  if(route==='/'){
   await page.getByRole('button',{name:/^(Start again|Erase this session)$/}).click();
   await page.waitForFunction(()=>document.body.dataset.interactionState!=='reset');
   const [response]=await Promise.all([page.waitForResponse(r=>r.url().endsWith('/api/ask')),
    page.getByRole('button',{name:'Understand Amendment 7'}).click()]);amendment=await response.json();
   await page.locator('.explanation-card').waitFor();assert.equal(await page.locator('#authority').inputValue(),'KCEB');
  }else amendment=await ask('Explain Amendment 7');
  assert.equal(amendment.status,'answered');assert.equal(amendment.fact_validation.status,'supported');assert.equal(amendment.evidence.length,5);
  assert.equal(amendment.card.evidence_id,'amendment-7:kceb-sample');assert.equal(amendment.review.status,'not_run');
  assert.match(await page.locator('.explanation-card').textContent(),/YES would create/);
  for(const name of route==='/'?['Next part','Next part']:['Next','Next'])await page.getByRole('button',{name,exact:true}).click();
  assert.match(await page.locator('.explanation-card').textContent(),/does not approve creating the investment fund/);
  const yes=await ask('If I vote Yes, do my taxes go away?');assert.equal(yes.status,'answered');assert.equal(yes.view_plan.initial_part,1);
  if(route==='/'){
   const facet=yes.card.facets[yes.card.facet_keys.indexOf('conditions')],ex=page.locator('.clause-explanation'),parts=[];
   for(let i=0;i<5;i++){assert.match(await ex.locator(':scope>p').first().textContent(),new RegExp(`Reading step ${i+1} of 5`));parts.push(await ex.locator(':scope>p').nth(1).textContent());if(i<4)await ex.getByRole('button',{name:'Next step',exact:true}).click()}
   parts.push(await ex.locator(':scope>p').nth(2).textContent());assert.equal(parts.join(' '),facet.statement);
   const wording=page.locator('.facet-original summary');assert.equal(await wording.textContent(),'Read the source text');await wording.focus();await page.keyboard.press('Enter');assert.ok(await page.locator('.facet-original .ballot-wording').isVisible());assert.equal(await page.locator('.facet-original .ballot-wording').textContent(),yes.evidence.find(e=>e.id===facet.evidence_id).text);await page.keyboard.press('Enter');
   assert.equal(await page.locator('#full-answer-reading').evaluate(e=>e.open),false);await page.locator('#full-answer-reading summary').click();assert.equal(await page.locator('#answer-text').textContent(),yes.answer);assert.ok(await page.locator('#answer-text').isVisible());
  }
  else{const original=page.locator('.explanation-card .ballot-wording');assert.ok(await original.isVisible());assert.equal(await original.textContent(),yes.evidence.find(e=>e.id==='amendment-7:proposal-conditions').text);assert.match(await page.locator('.selected-source-clause').textContent(),/concurrent resolution/)}
  const amendmentSources=page.getByText('Sources (5) and limits',{exact:true});await amendmentSources.click();
  const law=yes.evidence.find(e=>e.id==='amendment-7:proposal-conditions');assert.ok((await page.locator('.source-disclosure').textContent()).includes(law.text));
  assert.match(law.text,/concurrent resolution.*first sixty/);
  const amendmentPdf=await page.request.get(url+law.original_route.split('#')[0]);assert.equal(amendmentPdf.status(),200);assert.equal(crypto.createHash('sha256').update(await amendmentPdf.body()).digest('hex'),law.sha256);
  await amendmentSources.click();await page.locator('.explanation-card').screenshot({path:path.join(output,route==='/'?'amendment7-main-800.png':'amendment7-copilot-800.png')});
  await page.setViewportSize({width:320,height:700});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('.explanation-card').screenshot({path:path.join(output,route==='/'?'amendment7-main-320.png':'amendment7-copilot-320.png')});await page.setViewportSize({width:800,height:480});
  const no=await ask('What does No mean?');assert.equal(no.status,'answered');assert.equal(no.contest.id,'amendment-7');assert.equal(no.view_plan.initial_part,2);assert.match(no.answer,/does not approve creating the investment fund/);
  const cap=await ask('What is the spending limit?');assert.equal(cap.status,'answered');assert.match(cap.answer,/not a new 3% tax/);
  const prediction=await ask('When will Amendment 7 eliminate taxes?');assert.equal(prediction.status,'insufficient_evidence');assert.ok(!prediction.card);assert.equal(await page.locator('.explanation-card').count(),0);
  const comparison=await ask('Compare Pollard and Fields priorities');assert.equal(comparison.evidence.length,2);assert.equal(comparison.card.type,'candidate_comparison');assert.equal(comparison.review.status,'not_run');
  const displayed=await page.locator('.candidate-comparison').textContent();for(const item of comparison.card.responses){assert.ok(displayed.includes(item.candidate_name));assert.ok(displayed.includes(item.quote));assert.ok(comparison.evidence.some(e=>e.id===item.evidence_id&&e.text===item.quote))}
  if(route==='/')assert.equal(await page.locator('#roster').textContent(),'');
  assert.ok(await input.isVisible());
  const contextual=await ask('And property taxes?');assert.equal(contextual.card.topic,'property');
  const natural=await ask('How do Pollard and Fields approaches to property taxes differ?');assert.equal(natural.card.topic,'property');
  const mixed=await ask('Compare Pollard and Fields on property taxes and climate');assert.equal(mixed.card.topic,'property');assert.match(mixed.answer,/climate.*unanswered/);
  const releasedAnswer=route==='/'?page.locator('#answer-text'):page.locator('[aria-label="Answer and evidence"] .answer-text');assert.ok(await releasedAnswer.isVisible());assert.match(await releasedAnswer.textContent(),/climate.*unanswered/);
  const both=await ask('Compare Pollard and Fields priorities and property assessments');assert.equal(both.card.sections.length,2);assert.equal(both.evidence.length,4);assert.equal(await page.locator('.candidate-comparison').count(),2);
  for(const shared of both.card.sections){assert.ok(await page.locator('.explanation-card').getByRole('heading',{name:shared.title,exact:true}).isVisible());for(const response of shared.responses)assert.ok((await page.locator('.candidate-comparison').allTextContents()).some(text=>text.includes(response.quote)))}
  const duration=await ask('What is the COMBAT tax rate and how long would it last?');assert.deepEqual(duration.view_plan.facet_keys,['rate','time']);assert.equal(await page.locator('.explanation-facet').count(),2);assert.match(await page.locator('.explanation-card').textContent(),/ten years/);
  const simpler=await ask("I still don't understand");assert.equal(simpler.contest.id,'combat');assert.equal(simpler.status,'answered');assert.equal(simpler.view_plan.component,'measure_parts');assert.equal(simpler.card.facets.length,5);


  await page.getByRole('button',{name:/^(Start again|Erase this session)$/}).click();assert.equal(await input.inputValue(),'');assert.equal(await page.locator('.explanation-card').count(),0);await page.waitForFunction(()=>['question','copilot-question'].includes(document.activeElement?.id));
  const fresh=await ask('And property taxes?');assert.ok(['clarification_needed','insufficient_evidence'].includes(fresh.status));assert.ok(fresh.request_id);assert.ok(!fresh.card);assert.notEqual(fresh.contest?.id,contextual.contest.id);
  assert.ok(await input.isVisible());
  for(const viewport of[{width:800,height:480},{width:320,height:700}]){await page.setViewportSize(viewport);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const bounds=await submit.boundingBox();assert.ok(bounds.height>=48)}
  await page.setViewportSize({width:800,height:480});
  // Hold an actual completed local answer until Reset, then attempt delayed delivery.
  const api=route==='/'?'/api/ask':'/api/ag-ui';let release,received;const gate=new Promise(r=>release=r),ready=new Promise(r=>received=r);
  await page.route('**'+api,async r=>{try{const response=await r.fetch();received();await gate;await r.fulfill({response})}catch{received()}});
  await input.fill('What is the COMBAT tax rate?');await submit.click();await Promise.race([ready,new Promise((_,j)=>setTimeout(()=>j(Error('Delayed-response setup timeout')),5000))]);
  await page.getByRole('button',{name:/^(Start again|Erase this session)$/}).click();release();await page.waitForTimeout(300);assert.equal(await input.inputValue(),'');assert.equal(await page.locator('.explanation-card').count(),0);if(route==='/')assert.equal(await page.locator('#answer-region').isVisible(),false);
  await page.unroute('**'+api);await page.waitForFunction(()=>['question','copilot-question'].includes(document.activeElement?.id));
  const afterDelayedReset=await ask('What is the COMBAT tax rate and how long would it last?');assert.equal(afterDelayedReset.status,'answered');assert.equal(await page.locator('.explanation-facet').count(),2);
  if(route==='/copilot'){
   const fail=r=>r.abort();await page.route('**/api/ag-ui',fail);
   await input.fill('What is the COMBAT tax rate?');await submit.click();
   await page.getByRole('status').filter({hasText:'Evidence connection failed. No answer released.'}).waitFor();assert.equal(await page.locator('[aria-label="Answer and evidence"]').count(),0);
   await page.waitForFunction(()=>!document.querySelector('button[type=submit]').disabled);
   await page.unroute('**/api/ag-ui',fail);const recovered=await ask('What is the COMBAT tax rate?');assert.equal(recovered.status,'answered');
  }
  const malformed=async r=>{const response=await r.fetch();if(route==='/'){const body=await response.json();body.card.facets[2].start++;await r.fulfill({response,json:body})}else{let body=await response.text();body=body.split('\n').map(line=>{if(!line.startsWith('data: '))return line;const event=JSON.parse(line.slice(6));if(event.type==='STATE_SNAPSHOT'&&event.snapshot.response?.card)event.snapshot.response.card.facets[2].start++;return 'data: '+JSON.stringify(event)}).join('\n');await r.fulfill({response,body})}};
  await page.route('**'+api,malformed);await input.fill('What is COMBAT tax rate and how long would it last?');await submit.click();
  if(route==='/')await page.locator('#activity').filter({hasText:'Evidence binding failed. No answer released.'}).waitFor();else await page.getByRole('status').filter({hasText:'Evidence binding failed. No answer released.'}).waitFor();
  assert.equal(await page.locator('.explanation-card').count(),route==='/'?1:0);if(route==='/')assert.equal(await page.locator('#answer-region').isVisible(),false);
  await page.unroute('**'+api,malformed);const recoveredBinding=await ask('What is COMBAT tax rate and how long would it last?');assert.equal(recoveredBinding.status,'answered');assert.equal(await page.locator('.explanation-facet').count(),2);
  const unspecified=await ask('What do Pollard and Fields propose?');assert.equal(unspecified.status,'insufficient_evidence');assert.ok(!unspecified.card);assert.equal(await page.locator('.candidate-comparison').count(),0);if(route==='/')assert.equal(await page.locator('#roster').textContent(),'');
  assert.equal(await page.evaluate(()=>window.captureCalls),0);assert.equal(liveRequests,0);assert.equal(external.length,0);assert.equal(errors.length,0);
  await page.screenshot({path:path.join(output,route==='/'?'main-reset-800.png':'copilot-reset-800.png')});
  reports.push({route,trusted_ingress_rejects_malformed_combined_span:true,whole_original_selected_span_copilot:route==='/copilot',keyboard_question_and_source_disclosure:true,exact_source_text_preserved:true,pdf_sha256_matches:true,candidate_attribution_preserved:true,natural_property_and_context:true,mixed_gap_explicit:true,both_candidate_topics_visible:true,both_combat_facets_visible:true,reset_blocks_actual_delayed_response:true,reset_focus_and_fresh_response:true,mixed_gap_visible_outside_composer:true,connection_failure_recovery:route==='/copilot',generic_position_intake_held:true,viewports:['800x480','320x700'],targets_at_least_48px:true,reduced_motion:true,secure_context:await page.evaluate(()=>isSecureContext),capture_calls:0,live_requests:0,external_requests:external,page_errors:errors});await page.close();
 }
 const proof={passed:true,execution:'actual_current_localhost_offline',url,voice:'off',paid_calls:0,full_accessibility_audit:false,physical_pi:false,reports};fs.writeFileSync(path.join(output,'browser-current.json'),JSON.stringify(proof,null,2));console.log(JSON.stringify(proof));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>await browser?.close());
