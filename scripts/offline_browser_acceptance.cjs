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
  await page.goto(url+route);const input=page.getByRole('textbox',{name:'Your election question'}),submit=page.getByRole('button',{name:'Show evidence',exact:true});await input.waitFor();await page.waitForFunction(()=>!document.querySelector('button[type=submit]').disabled);
  const health=await(await page.request.get(url+'/api/health')).json();assert.equal(health.mode,'exact_source');assert.equal(health.voice,'not_connected');assert.ok(Object.values(health.source_integrity).every(Boolean));
  async function ask(question){
   if(!await input.isVisible())await page.getByText('Ask another question',{exact:true}).click();await input.fill(question);
   const responsePromise=page.waitForResponse(r=>r.url().endsWith(route==='/'?'/api/ask':'/api/ag-ui'));
   await input.press('Tab'); // keyboard reaches the next usable control, never a hidden voice action.
   await submit.focus();await page.keyboard.press('Enter');const response=await responsePromise;assert.equal(response.status(),200);
   let result;if(route==='/')result=await response.json();else{const events=(await response.text()).split('\n').filter(x=>x.startsWith('data: ')).map(x=>JSON.parse(x.slice(6)));result=events.find(e=>e.type==='STATE_SNAPSHOT').snapshot.response}
   await page.locator('.explanation-card').waitFor();return result;
  }
  const rate=await ask('What is the COMBAT tax rate?');assert.equal(rate.review.status,'not_run');assert.equal(rate.fact_validation.status,'supported');assert.equal(rate.election_date,'2026-11-03');assert.ok(rate.evidence.length===1);
  if(route==='/'){await page.locator('#answer-text').waitFor();assert.equal(await page.locator('#answer-text').textContent(),rate.answer);assert.equal(await page.locator('#mic').isDisabled(),true);assert.equal(await page.locator('#speak').isVisible(),false)}
  else assert.match(await page.locator('.explanation-card').textContent(),/printed tax rate is one-quarter/);
  const sourceSummary=page.getByText('Sources (1) and limits',{exact:true});await sourceSummary.focus();await page.keyboard.press('Enter');await page.locator('.source-disclosure .quote').waitFor();assert.equal(await page.locator('.source-disclosure .quote').textContent(),rate.evidence[0].text);
  const original=rate.evidence[0];const pdf=await page.request.get(url+original.original_route);assert.equal(pdf.status(),200);assert.equal(crypto.createHash('sha256').update(await pdf.body()).digest('hex'),original.sha256);
  await sourceSummary.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.explanation-card').count(),1);
  const comparison=await ask('Compare Pollard and Fields priorities');assert.equal(comparison.evidence.length,2);assert.equal(comparison.card.type,'candidate_comparison');assert.equal(comparison.review.status,'not_run');
  const displayed=await page.locator('.candidate-comparison').textContent();for(const item of comparison.card.responses){assert.ok(displayed.includes(item.candidate_name));assert.ok(displayed.includes(item.quote));assert.ok(comparison.evidence.some(e=>e.id===item.evidence_id&&e.text===item.quote))}
  if(route==='/')assert.equal(await page.locator('#roster').textContent(),'');
  await page.getByRole('button',{name:/^(Start again|Erase this session)$/}).click();assert.equal(await input.inputValue(),'');assert.equal(await page.locator('.explanation-card').count(),0);if(route==='/')assert.equal(await page.evaluate(()=>document.activeElement.id),'question');
  for(const viewport of[{width:800,height:480},{width:320,height:700}]){await page.setViewportSize(viewport);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));const bounds=await submit.boundingBox();assert.ok(bounds.height>=48)}
  await page.setViewportSize({width:800,height:480});
  // Hold an actual completed local answer until Reset, then attempt delayed delivery.
  const api=route==='/'?'/api/ask':'/api/ag-ui';let release,received;const gate=new Promise(r=>release=r),ready=new Promise(r=>received=r);
  await page.route('**'+api,async r=>{try{const response=await r.fetch();received();await gate;await r.fulfill({response})}catch{received()}});
  await input.fill('What is the COMBAT tax rate?');await submit.click();await Promise.race([ready,new Promise((_,j)=>setTimeout(()=>j(Error('Delayed-response setup timeout')),5000))]);
  await page.getByRole('button',{name:/^(Start again|Erase this session)$/}).click();release();await page.waitForTimeout(300);assert.equal(await input.inputValue(),'');assert.equal(await page.locator('.explanation-card').count(),0);if(route==='/')assert.equal(await page.locator('#answer-region').isVisible(),false);
  assert.equal(await page.evaluate(()=>window.captureCalls),0);assert.equal(liveRequests,0);assert.equal(external.length,0);assert.equal(errors.length,0);
  await page.screenshot({path:path.join(output,route==='/'?'main-reset-800.png':'copilot-reset-800.png')});
  reports.push({route,keyboard_question_and_source_disclosure:true,exact_source_text_preserved:true,pdf_sha256_matches:true,candidate_attribution_preserved:true,reset_blocks_actual_delayed_response:true,viewports:['800x480','320x700'],targets_at_least_48px:true,reduced_motion:true,secure_context:await page.evaluate(()=>isSecureContext),capture_calls:0,live_requests:0,external_requests:external,page_errors:errors});await page.close();
 }
 const proof={passed:true,execution:'actual_current_localhost_offline',url,voice:'off',paid_calls:0,full_accessibility_audit:false,physical_pi:false,reports};fs.writeFileSync(path.join(output,'browser-current.json'),JSON.stringify(proof,null,2));console.log(JSON.stringify(proof));
})().catch(e=>{console.error(e);process.exitCode=1}).finally(async()=>await browser?.close());
