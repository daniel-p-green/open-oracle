// Application-owned finite evidence path. No network/model calls or visitor storage.
export const CAPABILITIES = Object.freeze({mode:'fixture', generation:'not_run', review:'not_run', voice:'disabled', personalBallot:'not_loaded'});
export const VGC = Object.freeze({endpoint:'https://voterguidecommons.org/mcp', states:['WI','MI','GA','CA','HI'], enabled:false});
export const IDLE_MS = 120_000;
const CORPUS_SHA256 = '656b82b4fccceb1979165a96c788729e9cb528530502cb4d724e4ce7126a6663';

const queries = new Map([
  ['what do yes and no change?', ['yes','no','rate','duration','purpose','fund']],
  ['what does yes mean?', ['yes','rate','duration','purpose','fund']],
  ['what does no mean?', ['no']],
  ['what is the tax rate?', ['rate']],
  ['how long would it last?', ['duration']],
  ['what is combat?', ['purpose','fund']],
]);
export const EXAMPLES = [...queries.keys()];
const norm = text => text.trim().toLowerCase().replace(/\s+/g,' ');
const hash = async text => [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(text)))].map(x=>x.toString(16).padStart(2,'0')).join('');
const same = (a,b) => JSON.stringify(a) === JSON.stringify(b);
export function immutableCopy(value) {
  const copy = structuredClone(value);
  function freeze(item) {
    if (item && typeof item === 'object') {
      for (const child of Object.values(item)) freeze(child);
      Object.freeze(item);
    }
    return item;
  }
  return freeze(copy);
}

export function vgcPlan(state) {
  if (!VGC.states.includes(state)) return {status:'no_coverage', calls:0, reason:'No Voter Guide Commons coverage for this state.'};
  return {status:'disabled', calls:0, reason:'Optional newsroom adapter is not connected. Official membership is required separately.'};
}

export async function validateCorpus(corpus) {
  corpus = immutableCopy(corpus);
  if (await hash(JSON.stringify(corpus)) !== CORPUS_SHA256) throw Error('unadmitted_corpus');
  if (corpus?.schema !== 'openoracle-fixture/v1' || corpus.mode !== 'public_sample_fixture' || !Array.isArray(corpus.sources) || corpus.sources.length !== 1) throw Error('invalid_corpus');
  const s=corpus.sources[0];
  if (s.role !== 'official_sample' || s.membership_authority !== false || s.election_date !== corpus.scope.election_date || s.jurisdiction !== corpus.scope.jurisdiction || await hash(s.text) !== s.text_sha256) throw Error('source_integrity');
  if (s.url !== 'https://jcebmo.org/wp-content/uploads/11.03.26-Notice-of-Election-Sample-Ballot-Poster.pdf') throw Error('source_url');
  for (const c of Object.values(corpus.claims)) {
    if(c.source_id !== s.id || !Number.isInteger(c.start) || !Number.isInteger(c.end) || c.start < 0 || c.end <= c.start || c.end > s.text.length || s.text.slice(c.start,c.end) !== c.quote) throw Error('citation_binding');
  }
  return true;
}

// Drafts can select admitted claim IDs only. Text and links come from the registry.
// Future freeform Responses output needs a separate semantic release gate.
export async function release(draft, corpus, expectedScope, expectedClaims) {
  // Snapshot all caller-owned references before the first asynchronous check.
  [draft, corpus, expectedScope, expectedClaims] = immutableCopy([draft, corpus, expectedScope, expectedClaims]);
  await validateCorpus(corpus);
  if (!same(expectedScope,corpus.scope)) throw Error('scope_mismatch');
  if (!draft || Object.keys(draft).sort().join(',') !== 'claim_ids' || !Array.isArray(draft.claim_ids) || !same(draft.claim_ids,expectedClaims) || draft.claim_ids.some(id=>!Object.hasOwn(corpus.claims,id))) throw Error('unadmitted_draft');
  return immutableCopy(draft.claim_ids.map(id=>({id,...corpus.claims[id]})));
}

const hold = (status,message) => ({status,message,claims:[],sources:[],capabilities:CAPABILITIES});

export async function answer(question, corpus, locale='en') {
  if (typeof question !== 'string' || !question.trim() || question.length > 500) return hold('unsupported','Choose a sample question, or ask about the exact wording shown here.');
  const q=norm(question);
  if (/^(help|what can you help me with\??|how does this work\??)$/.test(q)) return hold('help','I can explain this public sample question and show its source. I cannot identify your personal ballot or recommend a vote.');
  if (/\b(should i vote|who should i|recommend|best candidate|persuade|convince)\b/.test(q)) return hold('advice_refused','I can explain wording and show sources. I cannot recommend a vote or try to change your views.');
  if (/\b(my ballot|on my ballot|eligible|my address|born|date of birth|dob)\b/.test(q)) return hold('membership_unknown','Your personal ballot has not been loaded. This public sample cannot establish what is on your ballot. Do not enter your address or date of birth.');
  const ids=queries.get(q);
  if (!ids) return hold('unsupported','This slice has no supported answer to that question. Try a sample question. Missing evidence stays unanswered.');
  if (locale !== 'en') return hold('translation_held','La explicación en español aún no está verificada. Puede leer el texto oficial original en inglés.');
  try {
    corpus = immutableCopy(corpus);
    const claims=await release({claim_ids:ids},corpus,corpus.scope,ids);
    return immutableCopy({status:'answered',message:'Prepared explanation from a retained public sample.',claims,sources:corpus.sources,capabilities:CAPABILITIES});
  } catch {
    return hold('source_held','The retained source could not be verified. No explanation is released.');
  }
}

// Shared ownership fence for input, reset, language changes and delayed results.
export function createSession() {
  let revision=0, latestActivity=0;
  return {
    begin(now=Date.now()) { latestActivity=now; return ++revision; },
    current(ticket) { return revision===ticket; },
    reset(now=Date.now()) { latestActivity=now; ++revision; },
    touch(now=Date.now()) { latestActivity=now; },
    idle(now=Date.now()) { return now-latestActivity>=IDLE_MS; },
  };
}
