'use strict';
async function boot() {
  const [catalog,registry,results]=await Promise.all(['locales.json','registry.json','fixture_results.json'].map(path=>fetch(path,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('fixture_unavailable');return r.json();})));
  const $=id=>document.getElementById(id),locale=new OpenOracleLocale.Locale(catalog,registry);
  const core={epoch:0,generation:0,request_id:'fixed-offline-fixture'};
  const cancel=()=>{core.generation++;$('transcript').value='';};
  const binding=new OpenOracleLocale.LanguageBinding(cancel,t=>Object.keys(core).every(k=>t[k]===core[k]));
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');
  let erased=false;
  const idle=new OpenOracleIdleLanguages.IdleLanguages($('idle'),{registry,catalog,preview:true,reducedMotion:reduced.matches});
  $('static').checked=reduced.matches;idle.start();
  const render=()=>{
    const row=results[locale.language];locale.localize(document);
    document.documentElement.lang=locale.language;
    for(const id of ['controls','translated']){$(id).dir=OpenOracleLocale.direction(locale.language);$(id).lang=locale.language;}
    $('primary').textContent=erased?'':row.primary;$('primary').lang=locale.language;$('primary').dir=OpenOracleLocale.direction(locale.language);
    $('original').textContent=erased?'':row.originals[0].text;
    $('english-output').hidden=erased||!$('english-toggle').checked||locale.language==='en';
    $('english').textContent=erased?'':row.english||'';$('english').lang='en';$('english').dir='ltr';
    $('status').textContent=locale.message('status.fixture').text;
  };
  $('language').addEventListener('change',()=>{binding.choose($('language').value,$('english-toggle').checked);locale.choose($('language').value);idle.stop();render();});
  $('english-toggle').addEventListener('change',()=>{binding.choose(locale.language,$('english-toggle').checked);render();});
  $('rotation-pause').addEventListener('click',()=>idle.pause());$('rotation-resume').addEventListener('click',()=>{idle.continue();idle.start();});
  $('static').addEventListener('change',()=>{idle.setStatic($('static').checked);idle.start();});
  reduced.addEventListener('change',()=>{if(reduced.matches){$('static').checked=true;idle.setStatic(true);}});
  document.addEventListener('visibilitychange',()=>document.hidden?idle.pause('hidden'):idle.continue('hidden'));
  $('fixture-start').addEventListener('click',()=>{idle.stop();$('status').textContent=locale.message('reason.voice_unverified').text;});
  $('fixture-stop').addEventListener('click',()=>{cancel();$('status').textContent=locale.message('status.stopped').text;});
  $('fixture-resume').addEventListener('click',()=>{$('status').textContent=locale.message('status.text_only').text;});
  $('fixture-erase').addEventListener('click',()=>{binding.erase();core.epoch++;erased=true;render();$('status').textContent=locale.message('status.erased').text;idle.stop();});
  $('correct').addEventListener('click',()=>{const text=$('transcript').value;if(text){binding.correction(text,locale.language,binding.bind(core));$('transcript').value=text;$('status').textContent=locale.message('status.review').text;}});
  window.addEventListener('pagehide',()=>idle.destroy(),{once:true});render();
  window.languageFixture={registry,locale,binding,idle};
}
boot().catch(error=>{document.getElementById('status').textContent='Offline fixture unavailable.';console.error('Fixed preview setup failure',error.stack);});
