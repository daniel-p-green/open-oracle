const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const{chromium}=require('/opt/homebrew/lib/node_modules/promptfoo/node_modules/playwright');
const url=process.argv[2], out=process.argv[3];if(!/^http:\/\/127\.0\.0\.1:\d+$/.test(url)||!out)throw Error('owned loopback required');fs.mkdirSync(out,{recursive:true});
const TEXT='Question 1\nShall the county continue a tax of 0.25 cent for ten years? The money must remain in a separate trust fund.\nQuestion 2\nShall a second program continue?';
(async()=>{const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const page=await browser.newPage({viewport:{width:1280,height:800},reducedMotion:'reduce'}), errors=[],unexpected=[];let capture=0, paid=0, checks=0;
 await page.addInitScript(()=>{window.captureCalls=0;navigator.mediaDevices.getUserMedia=()=>{window.captureCalls++;throw Error('capture forbidden')}});page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',r=>{const u=r.request().url();if(!u.startsWith(url)){unexpected.push(u);return r.abort()}if(/\/api\/(live|ask|ag-ui)/.test(u)){paid++;return r.abort()}return r.continue()});
 const expect=async(condition,message)=>{assert.ok(condition,message);checks++};
 async function ready(){await page.goto(url+'/website');await page.locator('#read-ballot').waitFor();await page.waitForFunction(()=>!document.getElementById('read-ballot').disabled);}
 async function erase(){await page.locator('#clear-wording').click();await page.waitForFunction(()=>document.getElementById('evaluator-status').textContent.startsWith('Session erased locally'));assert.equal(await page.locator('#intake-result').isVisible(),false);assert.equal(await page.locator('#ballot-wording').inputValue(),'');}
 async function read(text){await page.locator('#ballot-wording').fill(text);await page.locator('#read-ballot').click();await page.locator('#intake-selection').waitFor();await page.waitForFunction(()=>!document.getElementById('read-ballot').disabled);}
 async function calculate(block='q1',english=true){await page.locator('#intake-block').selectOption(block);await page.locator('#intake-complete').check();await page.locator('#intake-english').setChecked(english);await page.locator('#intake-calculate').click();await page.locator('#intake-result').waitFor();}
 try {
  await ready();const health=await(await page.request.get(url+'/api/health')).json();assert.equal(health.intake.enabled,true);assert.equal(health.provider,null);assert.equal(health.voice,'not_connected');checks++;
  await read(TEXT);await expect(!(await page.locator('#intake-english').isChecked()),'English not preselected');await expect(await page.locator('#intake-calculate').isDisabled(),'completeness required');
  await calculate();await expect(await page.locator('#intake-assumption').innerText()=== 'You selected English; source language not verified. This formula does not test comprehension, accuracy or legal meaning.','qualifier');
  await expect(await page.locator('#intake-scores').locator('dd').count()===2,'two formula numbers');await expect(await page.locator('#intake-selected-quote').textContent()===TEXT.slice(0,TEXT.indexOf('Question 2')),'complete condition original');await expect((await page.locator('#intake-result').textContent()).includes('Decisions clarity review: not run'),'clarity separate');
  await page.screenshot({path:path.join(out,'paste-qualified.png')});
  await calculate('whole');await expect((await page.locator('#intake-result').textContent()).includes('Whole-document diagnostic, not a per-question score.'),'whole diagnostic labelled');
  await calculate('q1',false);await expect(await page.locator('#intake-scores').count()===0,'no silent formula');
  await erase();await expect(await page.locator('#ballot-wording').evaluate(e=>document.activeElement===e),'Erase focus');
  await read('Question 1\nShall the café remain?');await calculate();await expect(await page.locator('#intake-scores').count()===0,'accented unsupported not stripped');await expect((await page.locator('#intake-selected-quote').textContent()).includes('café'),'original accent preserved');
  await erase();
  await page.locator('#ballot-file').setInputFiles({name:'wording.txt',mimeType:'text/plain',buffer:Buffer.concat([Buffer.from([0xef,0xbb,0xbf]),Buffer.from(TEXT)])});
  await page.locator('#read-ballot').click();await page.locator('#intake-selection').waitFor();await calculate();await expect(await page.locator('#intake-selected-quote').textContent()===TEXT.slice(0,TEXT.indexOf('Question 2')),'BOM TXT original');await erase();
  const pdf=await page.request.get(url+'/api/original/kceb-sample');assert.equal(pdf.status(),200);await page.locator('#ballot-file').setInputFiles({name:'public-ballot.pdf',mimeType:'application/pdf',buffer:await pdf.body()});await page.locator('#read-ballot').click();await page.locator('#intake-selection').waitFor();await expect((await page.locator('#evaluator-status').textContent()).includes('unverified'),'PDF no provenance promotion');await page.screenshot({path:path.join(out,'pdf-private.png')});await erase();
  await page.locator('#ballot-wording').fill(TEXT);let unlock;const held=new Promise(r=>unlock=r);let reached;const delivered=new Promise(r=>reached=r);let commitAfterCancel=0;
  const observer=request=>{if(request.url().endsWith('/api/intake/commit'))commitAfterCancel++};page.on('request',observer);
  await page.route(url+'/api/intake/prepare',async route=>{const response=await route.fetch();reached();await held;try{await route.fulfill({response})}catch{}});
  await page.locator('#read-ballot').click();await delivered;await page.locator('#cancel-intake').click();await page.waitForFunction(()=>document.getElementById('evaluator-status').textContent.startsWith('Preview cancelled'));
  unlock();await page.unroute(url+'/api/intake/prepare');await page.waitForTimeout(100);page.off('request',observer);
  await expect(commitAfterCancel===0,'cancel before unknown preview id prevents commit');await expect(!(await page.locator('#intake-selection').isVisible()),'late preview hidden');
  await page.locator('#read-ballot').click();await page.locator('#intake-selection').waitFor();await calculate();await expect(await page.locator('#intake-scores').count()===1,'fresh recovery after cancel');
  let unlockSelect;const heldSelect=new Promise(r=>unlockSelect=r);let reachedSelect;const arrivedSelect=new Promise(r=>reachedSelect=r);
  await page.route(url+'/api/intake/select',async route=>{const response=await route.fetch();reachedSelect();await heldSelect;try{await route.fulfill({response})}catch{}});
  await page.locator('#intake-calculate').click();await arrivedSelect;await erase();unlockSelect();await page.unroute(url+'/api/intake/select');await page.waitForTimeout(100);
  await expect(!(await page.locator('#intake-result').isVisible()),'late calculated result rejected after Erase');
  for (const width of [320,768,1280]) {await page.setViewportSize({width,height:700});await expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no horizontal overflow '+width);}
  capture=await page.evaluate(()=>window.captureCalls);await expect(capture===0&&paid===0&&unexpected.length===0&&errors.length===0,'no media/providers/errors');
  const report={passed:true,checks,url:url+'/website',execution:'actual_headless_browser_real_intake_http',source:'unverified_user_content',source_locale:'unknown',formula:'explicit_english_assumption',clarity:'not_run',strands_uploaded_answer:'not_implemented',capture_calls:capture,provider_route_requests:paid,external_requests:unexpected.length,page_errors:errors,viewports:[320,768,1280],no_private_content_or_ids_in_report:true};fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
 }finally{await browser.close()}
})().catch(error=>{console.error(error.stack);process.exitCode=1});
