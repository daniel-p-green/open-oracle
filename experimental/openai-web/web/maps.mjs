import {validateMaps} from './map-core.mjs';
const byId=id=>document.getElementById(id), ns='http://www.w3.org/2000/svg';
const text=(tag,value)=>{const e=document.createElement(tag);e.textContent=value;return e;};
let data, selected=null, viewId='statewide';
function draw(){
  const view=data.views.find(v=>v.id===viewId);
  byId('comparison').replaceChildren();byId('table').replaceChildren();
  for(const plan of data.plans){
    const article=document.createElement('article');article.className='plan';
    const head=document.createElement('div');head.className='plan-head';head.append(text('h2',plan.label),text('p',plan.id==='baseline'?'Census TIGER 2023 · CD118 baseline':'State-distributed HB1 geometry · 2025 plan'));article.append(head);
    const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',view.bounds.join(' '));svg.setAttribute('role','img');svg.setAttribute('aria-label',`${plan.label}, ${view.label}. District numbers also appear in the table below.`);svg.setAttribute('preserveAspectRatio','xMidYMid meet');
    // SVG viewport clips identically in both panels. Paths have no executable content.
    for(const f of plan.features){const path=document.createElementNS(ns,'path');path.setAttribute('d',f.path);path.setAttribute('class','district'+(selected===null?'':f.id===selected?' selected':' muted'));const title=document.createElementNS(ns,'title');title.textContent=`District ${f.id}`;path.append(title);svg.append(path);}
    for(const label of view.labels[plan.id]){const t=document.createElementNS(ns,'text');t.setAttribute('x',label.x);t.setAttribute('y',label.y);t.setAttribute('font-size',Math.max(view.bounds[2],view.bounds[3])/30);t.setAttribute('class','district-label');t.textContent=label.id;svg.append(t);}
    article.append(svg);byId('comparison').append(article);
    const tr=document.createElement('tr');tr.append(text('th',plan.label),text('td',view.labels[plan.id].map(l=>l.id).join(', ')));tr.firstChild.setAttribute('scope','row');byId('table').append(tr);
  }
  for(const b of byId('views').querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.view===viewId));
  for(const b of byId('districts').querySelectorAll('button'))b.setAttribute('aria-pressed',String(b.dataset.district===(selected===null?'all':String(selected))));
  byId('selection').textContent=selected===null?'All district numbers are visible where they intersect the selected view.':`District ${selected} is highlighted in both plans where visible. The same number can cover different territory; this is not your district assignment.`;
  byId('status').textContent=`${view.label}. Both panels use the same projection, extent, scale and neutral styling.`;
}
try{
  const [response, registryResponse, pinResponse]=await Promise.all([fetch('/maps.json',{cache:'no-store'}),fetch('/map-manifest.json',{cache:'no-store'}),fetch('/map-review-pin.json',{cache:'no-store'})]);
  if(!response.ok||!registryResponse.ok||!pinResponse.ok)throw Error('not_available');
  const raw=await response.text();if(raw.length>8*1024*1024)throw Error('byte_bound');
  const approved=await pinResponse.json(), bytes=new TextEncoder().encode(raw);
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(b=>b.toString(16).padStart(2,'0')).join('');
  if(hash!==approved.sha256||bytes.length!==approved.bytes)throw Error('unreviewed_derivative');
  data=validateMaps(JSON.parse(raw),await registryResponse.json());
  for(const view of data.views){const b=text('button',view.label);b.type='button';b.dataset.view=view.id;b.addEventListener('click',()=>{viewId=view.id;draw();});byId('views').append(b);}
  for(const id of [null,1,2,3,4,5,6,7,8]){const b=text('button',id===null?'All':String(id));b.type='button';b.dataset.district=id===null?'all':String(id);b.setAttribute('aria-label',id===null?'Show all districts':`Highlight district ${id} in both plans`);b.addEventListener('click',()=>{selected=id;draw();});byId('districts').append(b);}
  byId('projection').textContent='Both plans: EPSG:5070, NAD83 / Conus Albers, metres. No geometry simplification; display coordinates rounded to 0.1 metre. WGS84→NAD83 transformation reports 4m accuracy, not boundary survey precision.';
  for(const source of data.sources){const e=document.createElement('div');e.className='source';const a=document.createElement('a');a.href=source.url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=`${source.name} — original source ↗`;e.append(a,text('p',`Retrieved ${source.retrieved_utc}. ${source.bytes.toLocaleString()} bytes.`),text('code',`SHA256 ${source.sha256}`));byId('sources').append(e);}
  byId('rights').textContent='Local review only. Public distribution and attribution do not establish every reuse right. State-map reuse permissions remain unconfirmed; no public deployment or blanket licensing claim.';
  draw();
}catch{byId('status').textContent='Maps held: a verified local review bundle is unavailable or invalid. No substitute boundaries have been drawn.';byId('comparison').replaceChildren();}
