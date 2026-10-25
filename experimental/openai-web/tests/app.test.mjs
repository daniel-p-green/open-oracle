// Executes the actual app module against a minimal DOM/event fixture, with
// delayed source loading and crypto. This is not browser/accessibility proof.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {webcrypto} from 'node:crypto';
const deferred=()=>{let resolve;const promise=new Promise(r=>{resolve=r;});return {promise,resolve};};
const tick=()=>new Promise(r=>setImmediate(r));
const corpus=JSON.parse(await readFile(new URL('../fixtures/combat.json',import.meta.url),'utf8'));

class Element {
  constructor(){this.listeners={};this.children=[];this.value='';this.textContent='';this.tagName='DIV';}
  addEventListener(type,fn){this.listeners[type]=fn;}
  fire(type){this.listeners[type]?.({target:this,preventDefault(){}});}
  append(...items){this.children.push(...items);}
  replaceChildren(){this.children=[];this.textContent='';}
  focus(){document.activeElement=this;}
}

test('actual app events fence late typed answers after reset and language change',async()=>{
  const nodes=new Map();
  const get=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  get('language').value='en';
  const load=deferred(),fetchStarted=deferred();
  let cryptoGate,started,finished,count=0;
  Object.defineProperty(globalThis,'crypto',{configurable:true,value:{subtle:{async digest(...args){
    if(cryptoGate){started.resolve();await cryptoGate.promise;}
    const result=await webcrypto.subtle.digest(...args);
    if(finished && ++count===2)finished.resolve();
    return result;
  }}}});
  globalThis.document={getElementById:get,addEventListener(){},createElement:()=>new Element(),createTextNode:text=>({textContent:text})};
  globalThis.window={addEventListener(){}};
  globalThis.fetch=async()=>{fetchStarted.resolve();await load.promise;return {ok:true,json:async()=>corpus};};
  globalThis.setInterval=()=>0;
  const importing=import('../web/app.mjs');await fetchStarted.promise;
  get('language').value='es';get('language').fire('change');
  load.resolve();await importing;
  assert.match(get('result-status').textContent,/español/);
  assert.notEqual(get('result-status').textContent,'Choose a sample question to begin.');

  get('language').value='en';get('language').fire('change');
  for(const event of ['reset','language']){
    cryptoGate=deferred();started=deferred();finished=deferred();count=0;
    get('question').value='what is the tax rate?';get('ask').fire('submit');await started.promise;
    if(event==='reset')get('reset').fire('click');
    else{get('language').value='es';get('language').fire('change');}
    const current=get('result-status').textContent;
    cryptoGate.resolve();await finished.promise;await tick();
    assert.equal(get('result-status').textContent,current);assert.equal(get('claims').children.length,0);
  }
});
