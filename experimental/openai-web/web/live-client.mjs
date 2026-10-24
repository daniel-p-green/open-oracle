import {immutableCopy,validateCorpus} from './core.mjs';

const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const READING_SUFFIX=' This is a retained public sample, not your personal ballot.';
export async function validateIntegratedResult(value, corpus) {
  [value,corpus]=immutableCopy([value,corpus]);
  await validateCorpus(corpus);
  const claim={id:'rate',...corpus.claims.rate},audio=value?.audio;
  if(value?.explanation!==claim.text || !same(value.claims,[claim]) || !same(value.source,corpus.sources[0]) || !same(value.scope,corpus.scope)
      || value.reading!==claim.text+READING_SUFFIX || value.review!=='completed_uncalibrated' || value.playback_enabled!==false
      || audio?.prepared!==true || audio.transcript_match!==true || audio.finalized!==true
      || !Number.isInteger(audio.bytes) || audio.bytes<24000 || audio.bytes>2097152 || audio.bytes%2
      || typeof audio.sha256!=='string' || !/^[a-f0-9]{64}$/.test(audio.sha256)
      || !Number.isFinite(audio.seconds) || audio.seconds<=0 || audio.seconds>40)throw Error('unbound_provider_result');
  return value;
}

export function createHttpTransport(token) {
  async function json(path,options={}) {
    const response=await fetch(path,{...options,cache:'no-store',headers:{'Content-Type':'application/json','X-Session-Token':token}});
    const text=await response.text();
    if(!response.ok || text.length>16384)throw Error('provider_route_unavailable');
    return JSON.parse(text);
  }
  return {
    start:(request,signal)=>json('/api/provider/start',{method:'POST',body:JSON.stringify({request_id:request,question_id:'rate'}),signal}),
    poll:(request,signal)=>json('/api/provider/job/'+request,{signal}),
    cancel:request=>json('/api/provider/cancel',{method:'POST',body:JSON.stringify({request_id:request}),signal:AbortSignal.timeout(3000),keepalive:true}),
  };
}

export function createProviderClient({session,corpus,transport,onState=()=>{},onResult=()=>{},pollMs=500,deadlineMs=110000}) {
  let request,abort,activeCancel,expiryTimer;
  function stop() {
    session.reset();abort?.abort();clearTimeout(expiryTimer);
    activeCancel?.();
    request=undefined;
    onState('stopped');
  }
  async function pause(signal) {
    await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>{signal.removeEventListener('abort',cancel);resolve();},pollMs);
      function cancel(){clearTimeout(timer);reject(Error('cancelled'));}
      signal.addEventListener('abort',cancel,{once:true});
      if(signal.aborted)cancel();
    });
  }
  return {
    stop,
    async start() {
      stop();
      const ticket=session.begin(),id=crypto.randomUUID().replaceAll('-','');
      const ownAbort=new AbortController();abort=ownAbort;request=id;
      let cancellationSent=false;
      function cancelOnce(){if(!cancellationSent){cancellationSent=true;void transport.cancel(id).catch(()=>{});}}
      activeCancel=cancelOnce;
      const timer=setTimeout(()=>ownAbort.abort(),deadlineMs);
      onState('queued');
      try {
        let state=await transport.start(id,ownAbort.signal);
        while(session.current(ticket) && !ownAbort.signal.aborted) {
          if(state.request_id!==id)throw Error('wrong_request');
          if(state.state==='ready') {
            if(!Number.isFinite(state.expires_in_seconds) || state.expires_in_seconds<=0 || state.expires_in_seconds>120)throw Error('expired_result');
            const result=await validateIntegratedResult(state.result,corpus);
            if(!session.current(ticket) || ownAbort.signal.aborted)return;
            onState('ready');
            if(session.current(ticket) && !ownAbort.signal.aborted){
              onResult(result);
              expiryTimer=setTimeout(()=>{if(session.current(ticket)){stop();onState('expired');}},state.expires_in_seconds*1000);
              expiryTimer.unref?.();
            }
            return;
          }
          if(['held','cancelled','expired','cancel_requested'].includes(state.state)) {onState(state.state,state.reason);return;}
          if(!['queued','routing','text','review','audio'].includes(state.state))throw Error('invalid_state');
          onState(state.state);await pause(ownAbort.signal);
          state=await transport.poll(id,ownAbort.signal);
        }
      } catch {
        if(session.current(ticket))onState(ownAbort.signal.aborted?'timed_out':'held');
        cancelOnce();
      } finally { clearTimeout(timer);if(!session.current(ticket) || ownAbort.signal.aborted)cancelOnce(); }
    },
  };
}
