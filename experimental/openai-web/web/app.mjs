import {answer,validateCorpus,createSession,EXAMPLES,vgcPlan} from './core.mjs';
import {createConversation,createEvidenceReader,createFixtureIO,RETENTION_NOTICE} from './conversation.mjs';
const $=id=>document.getElementById(id);
const session=createSession();
let corpus,conversation,locale='en',index=0;
const ui={
 en:{heading:'Understand the question.\nMake your own choice.',intro:'Read what the proposal says, what Yes and No would change, and where each explanation comes from.',ask:'What would you like to understand?',submit:'Explain',reset:'Start over',previous:'Previous question',next:'Next question',status:'Choose a sample question to begin.',sample:'This is a public sample, not your personal ballot.',note:'We have not checked which contests apply to you. Do not enter your address, birth date or private voter records.'},
 es:{heading:'Comprenda la pregunta.\nTome su propia decisión.',intro:'Consulte el texto original en inglés. La explicación cívica en español aún no está verificada.',ask:'¿Qué desea entender?',submit:'Explicar',reset:'Empezar de nuevo',previous:'Pregunta anterior',next:'Pregunta siguiente',status:'La explicación en español está pendiente de revisión.',sample:'Esta es una muestra pública, no su boleta personal.',note:'No hemos comprobado qué contiendas le corresponden. No ingrese su dirección, fecha de nacimiento ni datos privados.'}
};

function clear(message=ui[locale].status){
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
 $('original-text').lang='en'; $('examples').hidden=locale!=='en'; clear();
}
async function ask(text){
 if(!corpus)return;
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
window.addEventListener('pagehide',()=>{if(conversation)conversation.reset();else session.reset();});
const stages={idle:'Silent fixture ready. Real microphone and cloud services are off.',consent_required:'Review the cloud data disclosure before simulating consent.',consent_declined:'Consent declined. Capture has not started.',permission_pending:'Simulating the device permission step. No real permission is requested.',permission_denied:'Permission denied. Capture has not started.',listening:'Fixture capture active. The real microphone is off.',checking:'Fixture capture stopped. Checking source coverage and uncertainty.',preparing:'Preparing a silent fixture from the checked answer.',ready:'Checked fixture ready. Select Play fixture to continue; no sound will play.',playing:'Silent playback fixture active. The text below is a preview, not live captions.',complete:'Silent fixture complete. No audio was generated or played.',held:'Answer or audio withheld. No playback is available.',interrupted:'Interrupted. Capture, pending work and queued playback are cleared.'};
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
$('voice-disclosure').textContent=RETENTION_NOTICE.text;$('voice-policy').href=RETENTION_NOTICE.url;
$('voice-start').addEventListener('click',()=>conversation?.requestConsent());
$('consent-check').addEventListener('change',()=>{$('voice-confirm').disabled=!$('consent-check').checked;});
$('voice-confirm').addEventListener('click',()=>conversation?.consent($('consent-check').checked));
$('voice-decline').addEventListener('click',()=>conversation?.consent(false));
$('voice-complete').addEventListener('click',()=>conversation?.completeInput($('voice-question').value,locale));
$('voice-question').addEventListener('change',()=>conversation?.interrupt());
$('voice-play').addEventListener('click',()=>conversation?.play());
$('voice-stop').addEventListener('click',()=>conversation?.interrupt());
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
}catch{corpus=null;$('result-status').textContent='The retained source is unavailable. Explanations are held. Reload to try again.';}
