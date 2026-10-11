(function(root) {
  'use strict';
  function tag(value) {
    if (typeof value !== 'string' || !/^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,4}$/.test(value)) throw Error('invalid_language');
    return value.split('-').map((p,i)=>i===0?p.toLowerCase():p.length===4&&/^[a-z]+$/i.test(p)?p[0].toUpperCase()+p.slice(1).toLowerCase():p.length===2&&/^[a-z]+$/i.test(p)?p.toUpperCase():p.toLowerCase()).join('-');
  }
  function direction(language) {
    const parts=tag(language).split('-'), script=parts.slice(1).find(p=>p.length===4&&/^[a-z]+$/i.test(p));
    return script ? ['Arab','Hebr','Thaa','Nkoo','Adlm','Syrc'].includes(script)?'rtl':'ltr' : ['ar','fa','he','ur','ps','sd','yi'].includes(parts[0])?'rtl':'ltr';
  }
  class Locale {
    constructor(catalog,registry,language='en') { this.catalog=catalog.catalogs; this.registry=registry; this.choose(language); }
    choose(language) {
      this.requested=tag(language);
      const parts=this.requested.split('-'),script=parts.slice(1).find(p=>p.length===4&&/^[a-z]+$/i.test(p));
      this.capability=this.registry.languages.find(r=>r.language===this.requested)||this.registry.languages.find(r=>r.language===parts[0]+(script?'-'+script:''))||this.registry.languages.find(r=>r.language===parts[0]&&(!script||r.script===script));
      this.language=this.capability?.language||'en';
      this.fallback=!this.capability||!this.catalog[this.language];
      if (!this.catalog[this.language]) this.language='en';
    }
    message(key) {
      const text=this.catalog[this.language]?.[key];
      if (typeof text!=='string'||!text) throw Error('missing_locale_key:'+key);
      return {text,language:this.language,direction:direction(this.language),fallback:this.fallback};
    }
    render(element,key,attribute=null) {
      const m=this.message(key);
      // Fixed allowlist: translations never become markup, CSS or handlers.
      if(attribute!==null&&!['placeholder','aria-label','title'].includes(attribute)) throw Error('unsafe_locale_attribute');
      if(attribute) element.setAttribute(attribute,m.text); else element.textContent=m.text;
      element.lang=m.language; element.dir=m.direction;
      return m;
    }
    localize(container) {
      for (const e of container.querySelectorAll('[data-l10n]')) this.render(e,e.dataset.l10n);
      for (const e of container.querySelectorAll('[data-l10n-placeholder]')) this.render(e,e.dataset.l10nPlaceholder,'placeholder');
      for (const e of container.querySelectorAll('[data-l10n-label]')) this.render(e,e.dataset.l10nLabel,'aria-label');
    }
    refusal(reason) {
      return this.message(Object.hasOwn(this.catalog[this.language],'reason.'+reason)?'reason.'+reason:'reason.invalid_translation_envelope');
    }
  }
  class LanguageSession {
    constructor(cancelPending,language='en',sessionId='language-session') {
      if(typeof cancelPending!=='function') throw Error('cancellation_required');
      this.cancelPending=cancelPending; this.sessionId=sessionId; this.epoch=0; this.revision=0;
      this.language=tag(language); this.optionalEnglish=false; this.stopped=true; this.pending=null; this.recognition=null; this.transcript=null;
    }
    invalidate() {
      const result=this.cancelPending();
      if(result===false) throw Error('cancellation_failed');
      if(result&&typeof result.then==='function') throw Error('synchronous_cancellation_required');
      this.epoch++; this.pending=null;
    }
    token(requestId) {
      if(this.stopped||typeof requestId!=='string'||!requestId||requestId.length>120) throw Error('session_stopped_or_invalid_request');
      this.pending={session_id:this.sessionId,epoch:this.epoch,language_revision:this.revision,request_id:requestId,language:this.language};
      return {...this.pending};
    }
    accepts(token) { return !this.stopped&&this.pending!==null&&token&&Object.keys(token).length===5&&Object.keys(this.pending).every(k=>token[k]===this.pending[k]); }
    choose(language,optionalEnglish=false) {
      const next=tag(language); if(typeof optionalEnglish!=='boolean') throw Error('invalid_english_preference');
      if(next!==this.language||optionalEnglish!==this.optionalEnglish) {
        this.invalidate(); this.revision++; this.language=next; this.optionalEnglish=optionalEnglish;
        this.recognition=null; this.transcript=null; this.stopped=true;
      }
    }
    suggest(languages,token) {
      if(!this.accepts(token)) return false;
      const tags=[...new Set(languages.map(tag))];
      if(!tags.length||tags.length>8) throw Error('invalid_recognition');
      this.recognition={languages:tags,mixed:tags.length>1,requires_choice:true}; return true;
    }
    correctTranscript(text,language,token) {
      if(!this.accepts(token)) return false;
      if(typeof text!=='string'||!text.length||text.length>2000) throw Error('invalid_transcript');
      const next=tag(language); this.invalidate(); this.stopped=true;
      this.transcript={text,language:next,corrected:true}; return true;
    }
    stop() { this.invalidate(); this.stopped=true; this.recognition=null; }
    resume() { if(this.stopped) { this.invalidate(); this.stopped=false; } }
    erase(newSessionId) { if(typeof newSessionId!=='string'||!newSessionId||newSessionId===this.sessionId) throw Error('new_session_required'); this.invalidate(); this.sessionId=newSessionId; this.stopped=true; this.recognition=null; this.transcript=null; }
  }
  class LanguageBinding {
    constructor(cancelCurrent,isCurrent,language='en') { this.cancelCurrent=cancelCurrent;this.isCurrent=isCurrent;this.language=tag(language);this.revision=0;this.optionalEnglish=false;this.recognition=null;this.correctedTranscript=null; }
    cancel(reason) { const r=this.cancelCurrent(reason);if(r===false)throw Error('cancellation_failed');if(r&&typeof r.then==='function') throw Error('synchronous_cancellation_required');this.revision++; }
    choose(language,optionalEnglish=false) { const chosen=tag(language);if(typeof optionalEnglish!=='boolean')throw Error('invalid_english_preference');if(chosen!==this.language||optionalEnglish!==this.optionalEnglish){this.cancel('language_revision');this.language=chosen;this.optionalEnglish=optionalEnglish;this.recognition=null;this.correctedTranscript=null;} }
    bind(ticket) { if(!ticket||!this.isCurrent(ticket)||Object.hasOwn(ticket,'language')||Object.hasOwn(ticket,'language_revision'))throw Error('stale_or_duplicate_language_binding');return {...ticket,language:this.language,language_revision:this.revision}; }
    accepts(ticket) { if(!ticket||ticket.language!==this.language||ticket.language_revision!==this.revision)return false;const {language,language_revision,...base}=ticket;return Boolean(this.isCurrent(base)); }
    correction(text,language,ticket) { if(!this.accepts(ticket))return false;if(typeof text!=='string'||!text.length||text.length>2000)throw Error('invalid_transcript');const next=tag(language);this.cancel('recognition_revision');this.correctedTranscript={text,language:next,corrected:true};this.recognition=null;return true; }
    erase() { this.cancel('erase_language_state');this.recognition=null;this.correctedTranscript=null; }
  }
  const api={tag,direction,Locale,LanguageSession,LanguageBinding};
  if(typeof module!=='undefined') module.exports=api; else root.OpenOracleLocale=api;
})(typeof window==='undefined'?globalThis:window);
