/** Current snake_case transport projection, not a versioned server attestation. */
export type ViewPlan = Readonly<{version:1;request_id:string;component:'measure_parts'|'measure_focus'|'candidate_quotes'|'source_quotes';evidence_ids:readonly string[];facet_keys:readonly string[];initial_part:number;language:'en'}>;
export type Json = null | boolean | number | string | readonly Json[] | {readonly [key:string]:Json};
export type OwnerTicket = Readonly<{request_id:string;[key:string]:Json}>;
export interface Evidence {
  readonly id:string;readonly text:string;readonly sha256:string;readonly contest_id:string;readonly election_date:string;
  readonly source_category:string;readonly original_route:string;readonly url:string;readonly title:string;
  readonly issuer:string;readonly retrieved_date:string;readonly version:string;readonly extraction:string;
  readonly status:string;readonly page:number|string|null;readonly column?:number|string|null;
  readonly candidate_name?:string;readonly topic?:string;readonly question?:string;readonly passage_sha256?:string;
}
export interface Facet {readonly title:string;readonly statement:string;readonly quote:string;readonly evidence_id:string;readonly start:number;readonly end:number}
export interface CandidateAnswer {readonly candidate_name:string;readonly party:string;readonly quote:string;readonly evidence_id:string;readonly passage_sha256:string}
export interface CandidateSection {readonly topic:string;readonly title:string;readonly responses:readonly CandidateAnswer[]}
export interface MeasureCard {readonly type:'measure_explanation';readonly id:string;readonly title:string;readonly contest_id:string;readonly election_date:string;readonly evidence_id:string;readonly source_sha256:string;readonly source_url:string;readonly jurisdiction:string;readonly presentation:'overview'|'step_by_step'|'choice_focus';readonly facets:readonly Facet[];readonly facet_keys?:readonly string[];readonly limit:string;readonly method:string}
export interface CandidateCard extends CandidateSection {readonly type:'candidate_comparison';readonly id:string;readonly contest_id:string;readonly method:string;readonly limit:string;readonly sections?:readonly CandidateSection[]}
export type Card = MeasureCard|CandidateCard;
export interface Contest {readonly id:string;readonly title:string;readonly candidates?:readonly {readonly name:string;readonly party:string}[];readonly required_location?:string|null}
export interface SourceFallback {readonly type:'verified_originals';readonly request_id:string;readonly contest_id:string;readonly election_date:string;readonly scope:Readonly<Record<string,string>>;readonly sources:readonly Evidence[];readonly source_bindings:Readonly<Record<string,string>>;readonly label:string;readonly candidate_statement_limit:string}
export interface CandidateSource {readonly candidate_id:string;readonly candidate_name:string;readonly gap:string;readonly sources:readonly {readonly kind:string;readonly coverage:string;readonly url:string;readonly original_route?:string|null;readonly source_class:string;readonly publication_date:string;readonly retrieved_date:string;readonly document_period:string}[]}
export interface Expectation {scope:Readonly<Record<string,string>>;language:'en';contest_id?:string|null;language_revision?:number}
export interface TrustedBindings {
  /** Application-owned, independently loaded/hash-checked original projections.
   * Never build these registries from the result currently being validated. */
  source(id:string):Evidence|undefined;
  contest(id:string):Contest|undefined;
  card(id:string):Card|undefined;
  sourceFingerprint(id:string):string|undefined;
  officialLinks:readonly {readonly title:string;readonly url:string}[];
  candidateSource?(id:string):CandidateSource|undefined;
  /** Synchronous existing finite core display guard, not a cast/AI label. */
  researchDisplay?(response:Json):boolean;
}
export interface PublicProjection {
  readonly request_id:string;
  readonly status:string;
  readonly answer:string;
  readonly mode:'exact_source'|'live_strands'|'reviewed_strands_research';
  readonly language:'en';
  readonly translation_status:'not_requested';
  readonly scope:Readonly<Record<string,string>>;
  readonly review:Readonly<{status:string;label:string;execution?:string}>;
  readonly fact_validation:Readonly<{status:string}>;
  readonly card:Card|null;
  readonly evidence:readonly Evidence[];
  readonly view_plan:ViewPlan|null;
  readonly source_fallback?:SourceFallback;
  readonly requested_parts?:readonly string[];
  readonly comparison_request?:Readonly<{topics:readonly string[];gaps:readonly string[];unclassified:boolean}>;
  readonly contest?:Contest;
  readonly required_scope?:Readonly<{field:'district'|'municipality';value:string}>;
  readonly snapshot_date:string;
  readonly election_date:string;
  readonly limitations:readonly string[];
  readonly choices:readonly {readonly id:string;readonly title:string}[];
  readonly links:readonly {readonly title:string;readonly url:string}[];
  readonly candidate_sources:readonly CandidateSource[];
  /** No playback authority. Original transport belongs to the voice receipt gate. */
  readonly speech:false;
}
export type InstallResult = {ok:true;response:PublicProjection}|{ok:false;reason:string};
export class AcceptedStore {
  constructor(options:{isCurrent:(ticket:OwnerTicket)=>boolean;trust:TrustedBindings});
  begin(ticket:OwnerTicket,context:Expectation):Readonly<{accepted:PublicProjection|null;pending_request_id:string|null}>;
  install(raw:unknown,ticket:OwnerTicket):InstallResult;
  descriptor(raw:unknown,status:string,ticket:OwnerTicket):ViewPlan|null;
  /** Local hold only; does not send or confirm backend cancellation. */
  invalidate(reason:string,options?:{erase?:boolean}):Readonly<{accepted:PublicProjection|null;pending_request_id:string|null}>;
  snapshot():Readonly<{accepted:PublicProjection|null;pending_request_id:string|null}>;
}
export function validateProjection(input:unknown,expectation:Expectation&{request_id:string},trust:TrustedBindings):PublicProjection;
export function sourceSpan(source:{id:string;text:string},span:{evidence_id:string;start:number;end:number;quote:string}):boolean;
export function safeUrl(value:unknown):boolean;
