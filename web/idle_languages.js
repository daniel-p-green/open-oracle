(function(root) {
  'use strict';
  function ready(r,registry,catalog) {
    return Boolean(r&&r.spoken_ready===true&&r.controls==='validated'&&r.explanation==='evaluated_finite_contract'&&r.recognition==='physically_verified'&&r.speech==='physically_verified'&&typeof r.voice==='string'&&r.voice&&r.catalog_validation==='validated'&&Array.isArray(r.verified_surfaces)&&Array.isArray(r.verified_scopes)&&r.verified_surfaces.includes(registry.surface)&&r.verified_scopes.includes(registry.scope)&&typeof catalog?.catalogs?.[r.language]?.[r.invitation_key]==='string');
  }
  function invitations(registry,{preview=false,catalog}={}) {
    if(registry?.version!==1||!Array.isArray(registry.languages)||!catalog) return [];
    return registry.languages.filter(r=>r&&typeof r.label==='string'&&r.label&&['ltr','rtl'].includes(r.direction)&&catalog.catalogs?.[r.language]?.[r.invitation_key]&&(ready(r,registry,catalog)||(preview&&r.controls==='fixture_complete')))
      .map(r=>({language:r.language,label:r.label,direction:r.direction,
        invitationKey:r.invitation_key,status:ready(r,registry,catalog)?'ready':'experimental'}));
  }
  class IdleLanguages {
    constructor(container,{registry,catalog,preview=false,dwellMs=10000,reducedMotion=false,setTimer=root.setTimeout.bind(root),clearTimer=root.clearTimeout.bind(root)}) {
      if(dwellMs<8000||dwellMs>60000) throw Error('invalid_reading_dwell');
      this.container=container; this.rows=invitations(registry,{preview,catalog}); this.catalog=catalog;this.preview=preview;this.registry=registry;
      this.dwellMs=dwellMs; this.static=reducedMotion; this.setTimer=setTimer; this.clearTimer=clearTimer;
      this.index=0; this.timer=null; this.active=false; this.reading=false;this.holds=new Set();this.animationRevision=0;
      this.onFocus=()=>this.pause('focus'); this.onBlur=()=>this.continue('focus');
      this.onEnter=()=>this.pause('pointer');this.onLeave=()=>this.continue('pointer');
      container.addEventListener('focusin',this.onFocus); container.addEventListener('focusout',this.onBlur);
      container.addEventListener('pointerenter',this.onEnter);container.addEventListener('pointerleave',this.onLeave);
      this.render();
    }
    render() {
      this.container.replaceChildren();
      const doc=this.container.ownerDocument;
      if(this.preview) { const banner=doc.createElement('p');banner.lang='en';banner.dir='ltr';banner.textContent=this.catalog.catalogs.en['idle.preview_label'];this.container.append(banner); }
      if(!this.rows.length) { const unavailable=doc.createElement('p');unavailable.lang='en';unavailable.textContent=this.catalog.catalogs.en['reason.voice_unverified']+' '+this.catalog.catalogs.en['status.text_only'];this.container.append(unavailable);return; }
      // All strings belong to catalog. No HTML, flags, audio or capture APIs.
      for(const r of this.static?this.rows:this.rows.slice(this.index,this.index+1)) {
        const row=this.container.ownerDocument.createElement('div'); row.lang=r.language; row.dir=r.direction; row.className='idle-language';
        const invitation=this.container.ownerDocument.createElement('p'); invitation.textContent=this.catalog.catalogs[r.language]?.[r.invitationKey]||r.label;
        const status=this.container.ownerDocument.createElement('p'); status.className='language-capability';
        status.textContent=this.catalog.catalogs[r.language]?.[r.status==='ready'?'idle.ready':'idle.experimental']||r.status;
        row.append(invitation,status); this.container.append(row);
      }
      const list=doc.createElement('ul');list.className='idle-language-list';
      for(const r of this.rows) {const item=doc.createElement('li');const name=doc.createElement('bdi');name.lang=r.language;name.dir=r.direction;name.textContent=r.label;item.append(name);list.append(item);}
      this.container.append(list);
      // Deliberate Start button lives outside rotating region. No live announcements.
    }
    start() { this.active=true; this.schedule(); }
    schedule() { if(this.active&&!this.static&&!this.reading&&this.rows.length>1&&this.timer===null) {const revision=this.animationRevision;this.timer=this.setTimer(()=>{if(!this.active||revision!==this.animationRevision||this.reading||this.static)return;this.timer=null;this.index=(this.index+1)%this.rows.length;this.render();this.schedule();},this.dwellMs);} }
    pause(reason='manual') { this.animationRevision++;this.holds.add(reason);this.reading=true; if(this.timer!==null) this.clearTimer(this.timer); this.timer=null; }
    continue(reason='manual') { this.holds.delete(reason);this.reading=this.holds.size>0; this.schedule(); }
    stop() { this.animationRevision++;this.active=false; if(this.timer!==null) this.clearTimer(this.timer);this.timer=null; }
    setStatic(value) { this.stop();this.static=Boolean(value);this.render(); }
    refresh(registry) { const active=this.active;this.stop();this.registry=registry;this.rows=invitations(registry,{preview:this.preview,catalog:this.catalog});this.index=0;this.render();if(active)this.start(); }
    destroy() { this.stop();this.container.removeEventListener('focusin',this.onFocus);this.container.removeEventListener('focusout',this.onBlur);this.container.removeEventListener('pointerenter',this.onEnter);this.container.removeEventListener('pointerleave',this.onLeave); }
  }
  const api={invitations,IdleLanguages,ready};
  if(typeof module!=='undefined') module.exports=api; else root.OpenOracleIdleLanguages=api;
})(typeof window==='undefined'?globalThis:window);
