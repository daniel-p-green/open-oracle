import {useEffect,useRef,useState,type FormEvent} from 'react';
import {createRoot} from 'react-dom/client';
import {CopilotKitContext,CopilotKitCoreReact} from '@copilotkit/react-core/v2/context';
import {z} from 'zod';
import {useAgent,useRenderTool,useRenderToolCall} from '@copilotkit/react-core/v2/headless';
import {HttpAgent} from '@ag-ui/client';
import type {OwnerTicket, Expectation, PublicProjection} from '../release-store';
type ReadingIngress={prepare(ticket:OwnerTicket,context:Expectation,signal?:AbortSignal):Promise<void>;install(raw:unknown,ticket:OwnerTicket):{ok:true;response:PublicProjection}|{ok:false;reason:string};descriptor(raw:unknown,status:string,ticket:OwnerTicket):unknown;invalidate(reason:string,options?:{erase?:boolean}):unknown};
declare global {interface Window {OpenOracleIngress:{createIngress(isCurrent:(ticket:OwnerTicket)=>boolean):ReadingIngress}}}

type Facet={title:string;statement:string;quote:string;evidence_id:string;start:number;end:number};
type Evidence={id:string;text:string;source_category:string;original_route:string;url:string;page:number|string;version:string;candidate_name?:string;topic?:string;question?:string;passage_sha256?:string};
type CandidateAnswer={candidate_name:string;party:string;quote:string;evidence_id:string;passage_sha256:string};
type CandidateSection={topic:string;title:string;responses:CandidateAnswer[]};
type Card={type:'measure_explanation';title:string;presentation:string;facets:Facet[];facet_keys?:string[];limit:string}|{type:'candidate_comparison';title:string;topic:string;responses:CandidateAnswer[];sections?:CandidateSection[];method:string;limit:string};
type CandidateSource={candidate_name:string;gap:string;sources:{kind:string;coverage:string;url:string;original_route?:string;source_class:string;publication_date:string;retrieved_date:string;document_period:string}[]};
type ViewPlan={version:1;request_id:string;component:'measure_parts'|'measure_focus'|'candidate_quotes'|'source_quotes';evidence_ids:string[];facet_keys:('decision'|'rate'|'time'|'purpose'|'fund'|'conditions'|'no'|'investment'|'limit')[];initial_part:number;language:'en'};
type SourceFallback={type:'verified_originals';request_id:string;sources:Evidence[];label:string;candidate_statement_limit:string};
type Response={view_plan:ViewPlan|null;fact_validation:{status:string};source_fallback?:SourceFallback;requested_parts?:string[];comparison_request?:{topics:string[]};request_id:string;status:string;answer:string;mode:string;review:{status:string;execution?:string;label:string};card:Card|null;evidence:Evidence[];limitations:string[];choices:{id:string;title:string}[];links:{title:string;url:string}[];candidate_sources:CandidateSource[];contest?:{id:string;title:string;candidates?:{name:string;party:string}[]}};
type Contest={id:string;title:string;kind:string};
let copilotSession=crypto.randomUUID();
const evidenceAgent=new HttpAgent({url:'/api/ag-ui',agentId:'evidence',threadId:crypto.randomUUID(),headers:{'X-Oracle-Session':copilotSession}});
const agents={evidence:evidenceAgent};
// Local-only direct registration: no runtime/Intelligence account or generated sandbox.
const copilotkit=new CopilotKitCoreReact({agents__unsafe_dev_only:agents,headers:{'X-Oracle-Session':copilotSession}});
const contextValue={copilotkit,showIntelligenceIndicator:false,executingToolCallIds:new Set<string>()};
const safeUrl=(url:string)=>url.startsWith('/api/original/')||url.startsWith('/api/candidate-original/')||url.startsWith('/api/prepared-source/')||/^https:\/\//.test(url)?url:'#';
function Explanation({card,plan,evidence}:{card:Card;plan:ViewPlan;evidence:Evidence[]}){
 const [part,setPart]=useState(plan.initial_part);
 if(card.type==='candidate_comparison')return <article className="explanation-card"><p>The Beacon · attributed candidate answers</p>{(card.sections||[card]).map(shared=><section key={shared.topic}><h2>{shared.title}</h2><div className="candidate-comparison">{shared.responses.map(r=><section key={r.evidence_id}><h3>{r.candidate_name}</h3><p className="source-meta">{r.party} · District 1 At-Large</p><blockquote>{r.quote}</blockquote></section>)}</div></section>)}<p>{card.method}</p><p>{card.limit}</p></article>;
 const single=plan.component==='measure_focus';
 const keys=card.facet_keys||facetKeys;
 const facets=single?plan.facet_keys.map(key=>card.facets[keys.indexOf(key)]):[card.facets[part]];
 return <article className="explanation-card" data-view-component={plan.component} tabIndex={0} onKeyDown={e=>{if(single)return;if(e.key==='ArrowRight'){e.preventDefault();setPart(p=>Math.min(p+1,card.facets.length-1))}if(e.key==='ArrowLeft'){e.preventDefault();setPart(p=>Math.max(p-1,0))}}}>
 <p>Official ballot and proposal evidence</p>{facets.map(facet=><section key={facet.title}><h2>{facet.title}</h2>{(()=>{const source=evidence.find(s=>s.id===facet.evidence_id);if(!source)return null;const points=Array.from(source.text);return <div className="source-reading"><p className="source-meta">Official original · selected clause underlined</p><blockquote className="ballot-wording">{points.slice(0,facet.start).join('')}<span className="selected-source-clause">{points.slice(facet.start,facet.end).join('')}</span>{points.slice(facet.end).join('')}</blockquote></div>})()}<p className="explanation-facet">{facet.statement}</p></section>)}<p>{card.limit}</p>{!single&&<div className="form-actions"><button disabled={part===0} onClick={()=>setPart(p=>p-1)}>Previous</button><span>{part+1} of {card.facets.length}</span><button disabled={part===card.facets.length-1} onClick={()=>setPart(p=>p+1)}>Next</button></div>}</article>
}
const ViewPlanSchema=z.object({version:z.literal(1),request_id:z.string().min(1).max(120),component:z.enum(['measure_parts','measure_focus','candidate_quotes','source_quotes']),evidence_ids:z.array(z.string()).min(1).max(5),facet_keys:z.array(z.enum(['decision','rate','time','purpose','fund','conditions','no','investment','limit'])).max(5),initial_part:z.number().int().min(0).max(4),language:z.literal('en')}).strict();
const facetKeys=['decision','rate','time','purpose','fund'];
function validPlan(raw:unknown,response:Response):raw is ViewPlan{
 const parsed=ViewPlanSchema.safeParse(raw);if(!parsed.success)return false;const plan=parsed.data;
 if(plan.request_id!==response.request_id||JSON.stringify(plan)!==JSON.stringify(response.view_plan))return false;
 const sources=response.source_fallback?.sources||response.evidence;
 if(JSON.stringify(plan.evidence_ids)!==JSON.stringify(sources.map(s=>s.id)))return false;
 if(plan.component==='source_quotes')return plan.facet_keys.length===0&&plan.initial_part===0;
 if(response.status!=='answered'||response.fact_validation.status!=='supported')return false;
 if(plan.component==='candidate_quotes'){
  const card=response.card;
  if(card?.type!=='candidate_comparison'||plan.facet_keys.length!==0||plan.initial_part!==0)return false;
  const sections=card.sections||[card];
  if(sections.length<1||sections.length>2||(card.sections&&(sections.length!==2||JSON.stringify(sections.map(s=>s.topic))!==JSON.stringify(response.comparison_request?.topics)||sections[0].title!==card.title||JSON.stringify(sections[0].responses)!==JSON.stringify(card.responses))))return false;
  if(!sections.every(section=>section.responses.length===2&&new Set(section.responses.map(r=>r.candidate_name)).size===2&&section.responses.every(r=>response.contest?.candidates?.some(c=>c.name===r.candidate_name&&c.party===r.party)&&response.evidence.some(e=>e.id===r.evidence_id&&e.topic===section.topic&&e.question===section.title&&e.candidate_name===r.candidate_name&&e.text===r.quote&&e.passage_sha256===r.passage_sha256))))return false;
  const ids=sections.flatMap(section=>section.responses.map(r=>r.evidence_id));
  return new Set(ids).size===ids.length&&ids.length===response.evidence.length&&response.evidence.every(e=>ids.includes(e.id));
 }
 if(response.card?.type!=='measure_explanation')return false;
 const keys=response.card.facet_keys||facetKeys;
 if(!response.card.facets.every(f=>response.evidence.some(s=>s.id===f.evidence_id&&Array.from(s.text).slice(f.start,f.end).join('')===f.quote)))return false;
 if(JSON.stringify(plan.facet_keys)===JSON.stringify(['rate','time']))return plan.component==='measure_focus'&&plan.initial_part===1&&response.requested_parts?.includes('rate')===true&&response.requested_parts?.includes('duration')===true;
 return plan.component==='measure_parts'?JSON.stringify(plan.facet_keys)===JSON.stringify(keys)&&plan.initial_part===0:plan.facet_keys.length===1&&plan.initial_part===keys.indexOf(plan.facet_keys[0]);
}
function SourceQuotes({response}:{response:Response}){
 const fallback=response.source_fallback,sources=fallback?.sources||response.evidence;
 return <article className="explanation-card" data-view-component="source_quotes"><h2>{fallback?'Original wording · explanation withheld':response.contest?.candidates?.length?'Printed candidates':'Original source wording'}</h2><p>{fallback?.label||'Retained original wording. This is not a personal ballot.'}</p>{sources.map(source=><section key={source.id}><h3>{source.source_category}</h3><blockquote className="quote">{source.text}</blockquote><a href={safeUrl(source.original_route)} target="_blank" rel="noreferrer">Retained original</a></section>)}{fallback&&<p>{fallback.candidate_statement_limit}</p>}</article>
}
function AdaptiveEvidence({response,ingress,ticket}:{response:Response;ingress:ReadingIngress;ticket:OwnerTicket}){
 useRenderTool({name:'renderEvidenceView',parameters:ViewPlanSchema,render:({status,parameters})=>{
  if(status!=='complete'||!ingress.descriptor(parameters,status,ticket)||!validPlan(parameters,response))return null;
  if(parameters.component==='source_quotes')return <SourceQuotes response={response}/>;
  return response.card?<Explanation key={response.request_id} card={response.card} plan={parameters} evidence={response.evidence}/>:null;
 }},[response.request_id,ingress,ticket]);
 const renderCall=useRenderToolCall();const {agent}=useAgent({agentId:'evidence'});
 const id='view-'+response.request_id;
 const calls=agent.messages.flatMap(message=>message.role==='assistant'?message.toolCalls||[]:[]);
 const toolCall=calls.find(call=>call.id===id&&call.function.name==='renderEvidenceView');
 const toolMessage=agent.messages.find(message=>message.role==='tool'&&message.toolCallId===id);
 if(!toolCall||!toolMessage||toolMessage.role!=='tool')return null;
 return renderCall({toolCall,toolMessage});
}
function App(){
 const {agent,isReady}=useAgent({agentId:'evidence'});
 const [question,setQuestion]=useState(''),[authority,setAuthority]=useState('unknown'),[location,setLocation]=useState(''),[inventory,setInventory]=useState<Contest[]>([]),[status,setStatus]=useState('Ready for a question'),[mode,setMode]=useState('Loading sources'),[selected,setSelected]=useState<string|null>(null),[busy,setBusy]=useState(false);
 const expected=useRef<string|null>(null),epoch=useRef(0);
 const transportController=useRef<AbortController|null>(null),ticket=useRef<OwnerTicket|null>(null);
 const ingress=useRef<ReadingIngress|null>(null);
 if(!ingress.current)ingress.current=window.OpenOracleIngress.createIngress(t=>t.epoch===epoch.current&&t.request_id===expected.current&&!transportController.current?.signal.aborted);
 const [released,setReleased]=useState<Response|null>(null);
 const resetFocus=useRef(false);
 const [run,setRun]=useState<string|null>(null);
 const candidate=(agent.state as {response?:Response}).response;
 useEffect(()=>{
  if(!candidate||candidate.request_id!==run||candidate.request_id!==expected.current||!ticket.current)return;
  const checked=ingress.current!.install(candidate,ticket.current);
  if(checked.ok)setReleased(checked.response as unknown as Response);
  else{ingress.current!.invalidate('binding_failed');setReleased(null);setStatus('Evidence binding failed. No answer released.')}
 },[candidate,run]);
 useEffect(()=>{if(resetFocus.current){resetFocus.current=false;document.getElementById('copilot-question')?.focus()}});
 useEffect(()=>{Promise.all([fetch('/api/inventory').then(r=>r.json()),fetch('/api/health').then(r=>r.json())]).then(([rows,h])=>{setInventory(rows);setMode(h.mode==='exact_source'?'Exact-source mode · independent AI review is off':'Live Strands · independent review required')}).catch(()=>setStatus('Sources unavailable. Use the main text fallback.'))},[]);
 async function ask(e?:FormEvent,chosenQuestion=question,contestId=selected){
  e?.preventDefault(); if(!isReady||!chosenQuestion.trim())return;
  const thisEpoch=epoch.current,requestId=crypto.randomUUID();
  transportController.current?.abort();transportController.current=new AbortController();const signal=transportController.current.signal;
  agent.abortRun();expected.current=requestId;ticket.current={request_id:requestId,epoch:thisEpoch};setRun(requestId);setReleased(null);agent.setState({});
  agent.setMessages([{id:crypto.randomUUID(),role:'user',content:chosenQuestion.trim()}]);
  setBusy(true);setStatus('Checking retained evidence…');
  if(!contestId&&released?.card&&/^(?:i still don['’]?t understand[.!?]?|i['’]?m still confused[.!?]?|what does (?:yes|no) mean[.!?]?)$/i.test(chosenQuestion.trim()))contestId=released.contest?.id||null;
  const scope:Record<string,string>={election_date:'2026-11-03'};
  if(authority!=='unknown')scope.authority=authority;
  if(location)scope[location==='Sni Valley Fire Protection District'?'district':'municipality']=location;
  const timer=setTimeout(()=>{if(epoch.current===thisEpoch&&expected.current===requestId){agent.abortRun();transportController.current?.abort();ingress.current!.invalidate('timeout');expected.current=null;setRun(null);setBusy(false);setStatus('Request stopped. No answer released. Use text input to retry.')}},40000);
  try{
   await ingress.current!.prepare(ticket.current!,{scope,language:'en',contest_id:contestId},signal);
   if(epoch.current!==thisEpoch||expected.current!==requestId||signal.aborted)return;
   await copilotkit.runAgent({agent,runId:requestId,forwardedProps:{scope,...(contestId?{contest_id:contestId}:{})}});
   if(epoch.current===thisEpoch&&expected.current===requestId){
    const completed=(agent.state as {response?:Response}).response;
    const checked=completed?.request_id===requestId?ingress.current!.install(completed,ticket.current!):null;
    if(checked?.ok){setReleased(checked.response as unknown as Response);setStatus('Source response ready.')}
    else if(checked){ingress.current!.invalidate('binding_failed');setReleased(null);setStatus('Evidence binding failed. No answer released.')}
    else{expected.current=null;setRun(null);setStatus('Evidence connection failed. No answer released.')}
   }
  }
  catch{if(epoch.current===thisEpoch&&expected.current===requestId){ingress.current!.invalidate('request_failed');expected.current=null;setRun(null);setStatus('Evidence connection failed. No answer released.')}}
  finally{clearTimeout(timer);if(epoch.current===thisEpoch&&(expected.current===requestId||expected.current===null))setBusy(false)}
 }
 function invalidatePending(){transportController.current?.abort();agent.abortRun();ingress.current!.invalidate('input_changed');expected.current=null;setBusy(false)}
 function reset(){
  transportController.current?.abort();ingress.current!.invalidate('erase',{erase:true});ticket.current=null;setReleased(null);
  const erasedSession=copilotSession;
  epoch.current++;const resetEpoch=epoch.current;expected.current=null;agent.abortRun();agent.setState({});agent.setMessages([]);agent.threadId=crypto.randomUUID();setRun(null);setQuestion('');setSelected(null);setAuthority('unknown');setLocation('');setBusy(false);setStatus('Ready for a new visitor.');
  copilotSession=crypto.randomUUID();copilotkit.setHeaders({...copilotkit.headers,'X-Oracle-Session':copilotSession});
  resetFocus.current=true;
  fetch('/api/erase',{method:'POST',headers:{'Content-Type':'application/json','X-Oracle-Session':erasedSession},body:'{}',keepalive:true}).then(r=>{if(!r.ok)throw Error('Erase not confirmed')}).catch(()=>{if(epoch.current===resetEpoch&&expected.current===null)setStatus('Local content cleared. Server cancellation could not be confirmed; provider deletion is not promised.')});
 }
 return <><header className="masthead"><span className="brand">Open Oracle</span><button onClick={reset}>Start again</button></header><main><section className="conversation">
 {!released&&<div className="intro"><h1>What would you like<br/>to understand?</h1><p>Jackson County, Missouri · November 3, 2026</p></div>}
 <p role="status" aria-live="polite">{status}</p>
 {released&&<section aria-label="Answer and evidence"><h2>{released.contest?.title||'Source response'}</h2><p className="fine">{released.review.status==='not_run'?'Text only · retained sources. Independent AI review is off.':'Text only · voice output is held. AI checks are fallible.'}</p><p className="answer-text">{released.answer}</p>{released.view_plan&&<AdaptiveEvidence key={released.request_id} response={released} ingress={ingress.current!} ticket={ticket.current!}/>}
 {!released.view_plan&&!released.card&&released.status==='answered'&&Boolean(released.contest?.candidates?.length)&&<article className="explanation-card"><h2>Printed candidates</h2>{released.contest!.candidates!.map(c=><p key={c.name}><strong>{c.name}</strong> · {c.party}</p>)}<p>Retained official sample. This roster is not evidence of candidate positions.</p></article>}
 {released.choices.map(c=><button key={c.id} onClick={()=>{setSelected(c.id);ask(undefined,question,c.id)}}>{c.title}</button>)}
 <details className="source-disclosure" key={'sources-'+released.request_id}><summary>Sources ({(released.source_fallback?.sources||released.evidence).length+(released.candidate_sources||[]).reduce((n,p)=>n+p.sources.length,0)}) and limits</summary>{(released.source_fallback?.sources||released.evidence).map(e=><article className="evidence-card" key={e.id}><h3>{e.source_category}</h3><p>{e.version} · page {e.page}</p><blockquote className="quote">{e.text}</blockquote><a href={safeUrl(e.original_route)} target="_blank" rel="noreferrer">Original wording</a></article>)}{(released.candidate_sources||[]).map(person=><article className="evidence-card" key={person.candidate_name}><h3>{person.candidate_name}</h3><p>{person.gap}</p>{person.sources.map(source=><section key={source.url}><h4>{source.kind==='third_party_judicial_survey'?'Third-party judicial survey · not an app rating':source.kind==='candidate_statement_link'?'Candidate-authored answers · source pointer':source.kind==='official_record_gateway'?'Official records · not an analyzed voting history':'Attributed reporting · source pointer'}</h4><p>{source.source_class} · {source.publication_date} · retained {source.retrieved_date}</p><p>{source.coverage==='retained_original'?'Retained original; findings belong to the attributed publisher.':source.coverage==='source_specific_nonresponse'?'Nonresponse to this specific questionnaire; no position is inferred.':source.coverage==='mentioned_not_surveyed'?'Mentioned by this source, not surveyed; no answer is inferred.':'Source navigation only; no reviewed position quote is available here.'}</p><a href={safeUrl(source.url)} target="_blank" rel="noreferrer">Publisher source</a>{source.original_route&&<p><a href={safeUrl(source.original_route)} target="_blank" rel="noreferrer">Retained original</a></p>}</section>)}</article>)}{released.links.map(l=><p key={l.url}><a href={safeUrl(l.url)} target="_blank" rel="noreferrer">{l.title}</a></p>)}{released.limitations.map(l=><p key={l}>{l}</p>)}<p>{released.review.label}</p></details></section>}
 <details open key={'input-'+(released?.request_id||'ready')}><summary hidden={!released}>Ask another question</summary><form className="question-card" onSubmit={ask}><label className="sr-only" htmlFor="copilot-question">Your election question</label><textarea id="copilot-question" required maxLength={2000} rows={2} placeholder="Ask about a candidate or ballot question…" value={question} onChange={e=>{invalidatePending();setQuestion(e.target.value);setSelected(null)}}/><button type="submit" className="primary" disabled={!isReady||busy}>Show evidence</button><p className="fine">Text only. Microphone and generated speech are off.</p><details><summary>City or district context</summary><p>This guides source lookup; it does not assign your personal ballot.</p><label>Election authority<select value={authority} onChange={e=>{invalidatePending();setAuthority(e.target.value)}}><option value="unknown">Not sure</option><option value="KCEB">KCEB · Kansas City within Jackson County</option><option value="JCEB">JCEB · Outside Kansas City</option></select></label><label>City or district<select value={location} onChange={e=>{invalidatePending();setLocation(e.target.value)}}><option value="">Not specified</option>{['Kansas City within Jackson County','Blue Springs','Independence',"Lee's Summit",'Sni Valley Fire Protection District'].map(l=><option key={l}>{l}</option>)}</select></label></details></form></details>
 <details><summary>Browse contests</summary><p>Retained inventory; each voter receives only applicable contests.</p>{inventory.map(c=><p key={c.id}><button onClick={()=>{setSelected(c.id);setQuestion('Show original wording');ask(undefined,'Show original wording',c.id)}}>{c.title}</button></p>)}</details>
 <footer>Sources retained October 2026. Samples may change.<br/>No voting recommendations.<details><summary>Delivery details</summary><p>{mode}</p><p>CopilotKit 1.78.0 · AG-UI 1.0.2 · controlled components. Typed adaptive catalog via useRenderTool. Freeform Open Intelligent UI sandbox is not enabled.</p><a href="/">Main text fallback</a></details></footer></section></main></>
}
createRoot(document.getElementById('copilot-root')!).render(<CopilotKitContext.Provider value={contextValue}><App/></CopilotKitContext.Provider>);
