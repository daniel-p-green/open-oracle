import {answer,validateCorpus,createSession,EXAMPLES,vgcPlan} from './core.mjs';
import {createProviderClient,createHttpTransport} from './live-client.mjs';
import {createConversation,createEvidenceReader,createFixtureIO,RETENTION_NOTICE} from './conversation.mjs';
const $=id=>document.getElementById(id);
const session=createSession();
let corpus,conversation,providerClient,providerAvailable=false,providerUsed=false,locale='en',index=0;
const ui={
 en:{heading:'Understand the question.\nMake your own choice.',intro:'Read what the proposal says, what Yes and No would change, and where each explanation comes from.',ask:'What would you like to understand?',submit:'Explain',reset:'Start over',previous:'Previous question',next:'Next question',status:'Choose a sample question to begin.',sample:'This is a public sample, not your personal ballot.',note:'We have not checked which contests apply to you. Do not enter your address, birth date or private voter records.'},
 es:{heading:'Comprenda la pregunta.\nTome su propia decisión.',intro:'Consulte el texto original en inglés. La explicación cívica en español aún no está verificada.',ask:'¿Qué desea entender?',submit:'Explicar',reset:'Empezar de nuevo',previous:'Pregunta anterior',next:'Pregunta siguiente',status:'La explicación en español está pendiente de revisión.',sample:'Esta es una muestra pública, no su boleta personal.',note:'No hemos comprobado qué contiendas le corresponden. No ingrese su dirección, fecha de nacimiento ni datos privados.'}
};

function clear(message=ui[locale].status){
 providerClient?.stop(); $('provider-audio').textContent='';
 if (conversation) conversation.reset(); else session.reset();
 $('question').value=''; $('claims').replaceChildren(); $('result-status').textContent=message; $('original').open=false; index=0;
}
function localize(){
 const t=ui[locale];
 $('heading').textContent=t.heading;
 $('intro').textContent=t.intro; $('ask-label').textContent=t.ask;
 for(const key of ['submit','reset','previous','next'])$(key).textContent=t[key];
 $('sample-label').textContent=t.sample; $('sample-note').textContent=t.note;
 for(const id of ['heading','intro','ask-label','submit','reset','previous','next','sample-label','sample-note','result-status'])$(id).lang=locale;
 // The original is always English; UI localization does not grant civic translation.
 $('provider-start').disabled=!providerAvailable || providerUsed || locale!=='en';
 $('original-text').lang='en'; $('examples').hidden=locale!=='en'; clear();
}
async function ask(text){
 if(!corpus)return;
 providerClient?.stop();
 conversation?.interrupt();
 const ticket=session.begin(); $('result-status').textContent=locale==='en'?'Checking the retained source…':'Comprobando la fuente…'; $('claims').replaceChildren();
 const result=await answer(text,corpus,locale);
 if(!session.current(ticket))return;
 $('result-status').textContent=result.message;
 for(const claim of result.claims){
   const p=document.createElement('p');p.append(document.createTextNode(claim.text+' '));
   const a=document.createElement('a');a.href='#original';a.textContent='Read source';
   a.addEventListener('click',()=>{$('original').open=true;$('original').focus();});p.append(a);$('claims').append(p);
   const details=document.createElement('details'),summary=document.createElement('summary'),quote=document.createElement('blockquote');
   summary.textContent='Supporting excerpt';quote.textContent=claim.quote;details.append(summary,quote);$('claims').append(details);
 }
}
function choose(delta){index=(index+delta+EXAMPLES.length)%EXAMPLES.length;$('question').value=EXAMPLES[index];ask(EXAMPLES[index]);}
$('ask').addEventListener('submit',e=>{e.preventDefault();ask($('question').value);});
$('reset').addEventListener('click',()=>{clear();$('question').focus();});
$('previous').addEventListener('click',()=>choose(-1));$('next').addEventListener('click',()=>choose(1));
$('language').addEventListener('change',()=>{locale=$('language').value;localize();});
document.addEventListener('keydown',e=>{
 if(e.key==='Escape'){clear();$('question').focus();return;}
 if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;
 if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();choose(e.key==='ArrowRight'?1:-1);}
});
for(const event of ['pointerdown','keydown','input'])document.addEventListener(event,()=>session.touch());
setInterval(()=>{if(session.idle())clear(locale==='en'?'Session cleared after inactivity. Choose a sample question to start again.':'La sesión se borró por inactividad.');},1000);
window.addEventListener('pagehide',()=>{providerClient?.stop();if(conversation)conversation.reset();else session.reset();});
const stages={idle:'Silent fixture ready. This fixture uses no real microphone or cloud service.',consent_required:'Review the cloud data disclosure before simulating consent.',consent_declined:'Consent declined. Capture has not started.',permission_pending:'Simulating the device permission step. No real permission is requested.',permission_denied:'Permission denied. Capture has not started.',listening:'Fixture capture active. The real microphone is off.',checking:'Fixture capture stopped. Checking source coverage and uncertainty.',preparing:'Preparing a silent fixture from the checked answer.',ready:'Checked fixture ready. Select Play fixture to continue; no sound will play.',playing:'Silent playback fixture active. The text below is a preview, not live captions.',complete:'Silent fixture complete. No audio was generated or played.',held:'Answer or audio withheld. No playback is available.',interrupted:'Interrupted. Capture, pending work and queued playback are cleared.'};
function renderConversation(state){
 $('voice-status').textContent=stages[state.stage]??stages.held;
 $('voice-mic').textContent=state.mic==='fixture_active'?'Fixture capture active — real microphone off':'Microphone off';
 $('voice-consent').hidden=state.stage!=='consent_required';
 if(state.stage!=='consent_required'){$('consent-check').checked=false;$('voice-confirm').disabled=true;}
 $('voice-complete').disabled=state.stage!=='listening';$('voice-play').disabled=state.stage!=='ready';
 $('voice-preview').textContent=state.preview;
 $('voice-reading').textContent=state.reading;
 $('voice-hold').textContent=state.stage==='held'?(state.result?.message??'The complete checked transcript or audio binding was unavailable.') : '';
}
const providerStates={queued:'Starting the fixed public question…',routing:'Decisions is routing the public question…',text:'Responses is selecting the admitted wording…',review:'Checking source support…',audio:'Preparing audio privately on the server. No sound will play.',ready:'Source-checked text and transcript-matched audio prepared. Playback remains disabled.',held:'The provider result was withheld. Use the local fixture or start over.',cancelled:'Work cancelled. Local output is cleared.',expired:'Prepared output expired and was discarded.',cancel_requested:'Cancellation requested. An in-flight service call may still be finishing.',stopped:'Provider output cleared. No microphone or speaker is active.',timed_out:'The request timed out. Cancellation was requested; no retry was sent.'};
$('provider-start').addEventListener('click',()=>{
 if(!providerClient || locale!=='en')return;
 conversation?.interrupt();$('claims').replaceChildren();$('provider-audio').textContent='';$('result-status').textContent='Preparing the fixed public example…';
 $('question').value='what is the tax rate?';providerUsed=true;$('provider-start').disabled=true;
 providerClient.start();
});
$('provider-stop').addEventListener('click',()=>{clear();$('question').focus();});
function showProviderResult(result){
 $('result-status').textContent='Prepared wording selected by Responses and checked against the retained source. The model review is uncalibrated.';
 $('claims').replaceChildren();
 const p=document.createElement('p');p.textContent=result.explanation;
 const a=document.createElement('a');a.href='#original';a.textContent='Read original source';a.addEventListener('click',()=>{$('original').open=true;$('original').focus();});
 const quote=document.createElement('blockquote');quote.textContent=result.claims[0].quote;
 $('claims').append(p,a,quote);
 $('provider-audio').textContent=`Prepared audio: ${result.audio.bytes} PCM bytes; complete transcript matched; final duration ${result.audio.seconds}s. Reading: ${result.reading} Audio remains server-side; no acoustic or human-heard validation is claimed.`;
}
$('voice-disclosure').textContent=RETENTION_NOTICE.text;$('voice-policy').href=RETENTION_NOTICE.url;
$('voice-start').addEventListener('click',()=>{providerClient?.stop();conversation?.requestConsent();});
$('consent-check').addEventListener('change',()=>{$('voice-confirm').disabled=!$('consent-check').checked;});
$('voice-confirm').addEventListener('click',()=>conversation?.consent($('consent-check').checked));
$('voice-decline').addEventListener('click',()=>conversation?.consent(false));
$('voice-complete').addEventListener('click',()=>conversation?.completeInput($('voice-question').value,locale));
$('voice-question').addEventListener('change',()=>{providerClient?.stop();conversation?.interrupt();});
$('voice-play').addEventListener('click',()=>conversation?.play());
$('voice-stop').addEventListener('click',()=>{providerClient?.stop();conversation?.interrupt();});
try{
 const response=await fetch('/fixture.json',{cache:'no-store'});if(!response.ok)throw Error();corpus=await response.json();await validateCorpus(corpus);
 const s=corpus.sources[0];$('original-text').textContent=s.text;$('source-meta').textContent=`${s.issuer}, page ${s.page}. Official sample wording.`;$('source-link').href=s.url;$('digest').textContent=s.text_sha256;
 $('coverage-note').textContent=vgcPlan('MO').reason+' No newsroom result was used.';
 for(const q of EXAMPLES){const b=document.createElement('button');b.type='button';b.textContent=q;b.addEventListener('click',()=>{$('question').value=q;index=EXAMPLES.indexOf(q);ask(q);});$('examples').append(b);}
 conversation=createConversation({session,reader:createEvidenceReader(corpus),io:createFixtureIO(),onChange:renderConversation});
 renderConversation(conversation.snapshot());$('voice-start').disabled=false;
 for(const q of EXAMPLES){const option=document.createElement('option');option.value=q;option.textContent=q;$('voice-question').append(option);}
 for(const q of ['Is COMBAT on my ballot?','Who should I vote for?','Who is running for mayor?']){const option=document.createElement('option');option.value=q;option.textContent=q;$('voice-question').append(option);}
 $('submit').disabled=false;session.touch();$('result-status').textContent=ui[locale].status;
 try {
  const response=await fetch('/api/capabilities',{cache:'no-store'});const caps=await response.json();
  if(caps.providers==='enabled' && typeof caps.session_token==='string'){
   providerClient=createProviderClient({session,corpus,transport:createHttpTransport(caps.session_token),onState:(state,reason)=>{$('provider-status').textContent=providerStates[state]??providerStates.held;if(reason && /^[a-z_]{1,48}$/.test(reason))$('provider-status').textContent+=' Reason: '+reason+'.';if(['stopped','held','timed_out','cancelled','expired'].includes(state))$('provider-audio').textContent='';if(['held','timed_out','cancelled','expired'].includes(state)){$('claims').replaceChildren();$('result-status').textContent='No provider answer was released.';}},onResult:showProviderResult});
   providerAvailable=caps.remaining_runs>0;
   $('provider-panel').hidden=false;$('provider-start').disabled=!providerAvailable || locale!=='en';
   $('provider-note').textContent='Real providers enabled for a bounded public example. Typed questions and silent previews remain local fixtures.';
   $('privacy-note').textContent='Only the fixed public sample is sent by the live-example button. Typed questions stay in this tab. Microphone and speaker access are disabled.';
  }
 }catch{ /* Keep the already-working local fixture when provider controls are unavailable. */ }
}catch{corpus=null;$('result-status').textContent='The retained source is unavailable. Explanations are held. Reload to try again.';}
