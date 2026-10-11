'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {Locale,LanguageBinding,LanguageSession,direction}=require('../web/locale.js');
const {invitations,IdleLanguages}=require('../web/idle_languages.js');
const catalog=JSON.parse(fs.readFileSync(path.join(__dirname,'../web/locales.json'))),registry=JSON.parse(fs.readFileSync(path.join(__dirname,'../web/registry.json')));

class Element {
 constructor(doc){this.ownerDocument=doc;this.children=[];this.listeners=new Map();this.attrs={};this.textContent='';this.dataset={};}
 append(...els){this.children.push(...els);}replaceChildren(){this.children=[];}
 addEventListener(k,fn){this.listeners.set(k,fn);}removeEventListener(k){this.listeners.delete(k);}setAttribute(k,v){this.attrs[k]=v;}
}
function fixture(options={}) {
 const doc={createElement(){return new Element(doc);}},container=new Element(doc),timers=new Map();let next=0;
 const idle=new IdleLanguages(container,{registry,catalog,preview:true,setTimer:(fn,ms)=>{const id=++next;timers.set(id,{fn,ms});return id;},clearTimer:id=>timers.delete(id),...options});
 return {container,idle,timers};
}

test('six locales have complete text, explicit fallback and Arabic direction',()=>{
 for(const row of registry.languages){const locale=new Locale(catalog,registry,row.language);assert.equal(locale.message('control.stop').language,row.language);assert.equal(locale.message('status.fixture').direction,row.direction);}
 const fallback=new Locale(catalog,registry,'fr');assert.equal(fallback.language,'en');assert.equal(fallback.fallback,true);
 assert.equal(direction('ar-Latn'),'ltr');assert.equal(direction('en-Arab'),'rtl');
 assert.equal(new Locale(catalog,registry,'ar-Latn').fallback,true);assert.equal(new Locale(catalog,registry,'zh-Hant').fallback,true);assert.equal(new Locale(catalog,registry,'zh-Hans-CN').language,'zh-Hans');
});
test('translations render as text and only allow safe localized attributes',()=>{
 const e=new Element(null),locale=new Locale(catalog,registry,'ar');locale.render(e,'control.stop');assert.equal(e.dir,'rtl');assert.equal(e.lang,'ar');assert.equal(e.textContent,catalog.catalogs.ar['control.stop']);
 assert.throws(()=>locale.render(e,'control.stop','onclick'),/unsafe/);assert.throws(()=>locale.message('not.a.key'),/missing_locale/);
});
test('spoken invitations fail closed while all-six preview is explicitly experimental',()=>{
 assert.equal(invitations(registry,{catalog}).length,0);const preview=invitations(registry,{catalog,preview:true});assert.equal(preview.length,6);assert.ok(preview.every(r=>r.status==='experimental'));assert.equal(preview.find(r=>r.language==='ar').direction,'rtl');
 const poisoned=structuredClone(registry);poisoned.languages[0].spoken_ready=true;assert.equal(invitations(poisoned,{catalog}).length,0);
 assert.equal(invitations(registry,{preview:true}).length,0);
});
test('ready invitation requires every field, current scope/surface and native catalog',()=>{
 const r=structuredClone(registry),row=r.languages[0];r.scope='scope-1';r.surface='web';Object.assign(row,{spoken_ready:true,controls:'validated',explanation:'evaluated_finite_contract',recognition:'physically_verified',speech:'physically_verified',catalog_validation:'validated',verified_scopes:['scope-1'],verified_surfaces:['web']});
 assert.equal(invitations(r,{catalog}).length,1);
 for(const field of ['spoken_ready','controls','explanation','recognition','speech','voice','catalog_validation','verified_scopes','verified_surfaces']){const altered=structuredClone(r);delete altered.languages[0][field];assert.equal(invitations(altered,{catalog}).length,0,field);}
 const missing=structuredClone(catalog);delete missing.catalogs.en['idle.invitation'];assert.equal(invitations(r,{catalog:missing}).length,0);
});
test('idle dwell is at least 8 seconds, timers pause for reading and clean on unmount',()=>{
 assert.throws(()=>fixture({dwellMs:7999}),/invalid_reading/);const {idle,timers,container}=fixture();idle.start();assert.equal(timers.size,1);assert.ok([...timers.values()][0].ms>=8000);
 idle.pause('manual');idle.pause('focus');idle.continue('focus');assert.equal(timers.size,0);idle.continue('manual');assert.equal(timers.size,1);
 idle.stop();assert.equal(timers.size,0);idle.start();idle.destroy();assert.equal(timers.size,0);assert.equal(container.listeners.size,0);
});
test('reduced motion is static with all six native invitations and no timers',()=>{
 const {idle,timers,container}=fixture({reducedMotion:true});idle.start();assert.equal(timers.size,0);assert.equal(container.children.filter(e=>e.className==='idle-language').length,6);assert.equal(container.attrs['aria-live'],undefined);
});
test('current registry refresh removes obsolete ready invitations without leaving timers',()=>{
 const {idle,timers}=fixture();idle.start();assert.equal(timers.size,1);idle.preview=false;idle.refresh(registry);assert.equal(idle.rows.length,0);assert.equal(timers.size,0);
});
test('already queued old rotation callback cannot change display after Stop or Erase',()=>{
 const {idle,timers,container}=fixture();idle.start();const late=[...timers.values()][0].fn;idle.stop();const before=container.children;late();assert.equal(idle.index,0);assert.equal(container.children,before);assert.equal(timers.size,0);
});
test('malformed registry entries cannot advertise spoken readiness',()=>{
 const r=structuredClone(registry);r.languages=[null,{spoken_ready:true},{...r.languages[0],spoken_ready:true,verified_surfaces:{includes:true}}];assert.equal(invitations(r,{catalog}).length,0);
});
test('core identity and language revision invalidate stale text/media before locale changes',()=>{
 const core={epoch:1,generation:1,turn_id:'t',transcript_id:'tr',request_id:'r'};let cancelled=0;
 const binding=new LanguageBinding(()=>{cancelled++;core.generation++;},ticket=>JSON.stringify(ticket)===JSON.stringify(core));
 const old=binding.bind(core);assert.ok(binding.accepts(old));binding.choose('ar');assert.equal(cancelled,1);assert.equal(core.epoch,1);assert.ok(!binding.accepts(old));
 const current=binding.bind(core);assert.ok(binding.correction('السؤال عن الضريبة','ar',current));assert.ok(!binding.accepts(current));assert.equal(binding.language,'ar');binding.erase();assert.equal(binding.correctedTranscript,null);
});
test('failed synchronous cancellation cannot mutate chosen language',()=>{
 const binding=new LanguageBinding(()=>{throw Error('cancellation failed');},()=>true);assert.throws(()=>binding.choose('es'));assert.equal(binding.language,'en');assert.equal(binding.revision,0);
 const declined=new LanguageBinding(()=>false,()=>true);assert.throws(()=>declined.choose('es'),/cancellation_failed/);assert.equal(declined.language,'en');assert.equal(declined.revision,0);
});
test('isolated session preserves stop-resume distinction and clears erased transcript',()=>{
 const session=new LanguageSession(()=>{},'en','s1');session.resume();const old=session.token('r1');session.suggest(['es','en'],old);assert.equal(session.language,'en');assert.ok(session.recognition.mixed);session.choose('es');assert.ok(!session.accepts(old));assert.ok(session.stopped);session.resume();const current=session.token('r2');session.correctTranscript('La pregunta','es',current);session.stop();assert.ok(session.transcript);session.resume();session.erase('s2');assert.equal(session.transcript,null);assert.equal(session.sessionId,'s2');
});
