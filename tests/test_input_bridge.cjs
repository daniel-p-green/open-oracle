const assert=require('node:assert/strict');const{OracleInputBridge}=require('../web/input-bridge.js');
(async()=>{let states=[],adapters=[],resolve;const inputs={snapshot:()=>({state:'idle'}),attachSensorAdapter:opts=>{const adapter={closed:0,events:[],accept(e){this.events.push(e)},close(){this.closed++}};adapters.push(adapter);return adapter}};
 const sample=(extra={})=>({schema:'open-oracle-input/v1',available:true,cursor:1,session_id:'fixture-session',producer_monotonic_ms:0,capabilities:{presence:true,wave:true},events:[{type:'start_requested'}],...extra});
 let body=sample();const bridge=new OracleInputBridge(inputs,{fetcher:async()=>({ok:true,json:async()=>body}),delay:999999});bridge.abort=new AbortController();await bridge.poll(0);clearTimeout(bridge.timer);assert.equal(adapters.length,1);assert.equal(adapters[0].events.length,0,'Initial retained intent is never replayed');
 body=sample({cursor:2,events:[{type:'presence_detected'}]});await bridge.poll(0);clearTimeout(bridge.timer);assert.equal(adapters[0].events.length,1);
 body=sample({cursor:3,discontinuity:true});await bridge.poll(0);clearTimeout(bridge.timer);assert.equal(adapters[0].closed,1);assert.equal(bridge.adapter,null);
 const slow=new OracleInputBridge(inputs,{fetcher:()=>new Promise(r=>resolve=r),delay:999999});slow.start();slow.stop();resolve({ok:true,json:async()=>sample()});await Promise.resolve();await Promise.resolve();assert.equal(adapters.length,1,'A late response after stop never attaches');assert.equal(slow.adapter,null);
 bridge.stop();console.log('Input bridge: bootstrap replay, stream discontinuity and delayed-stop guards passed; no sensors or network.');
})().catch(e=>{console.error(e);process.exitCode=1});
