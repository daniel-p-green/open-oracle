"""Bounded Bedrock embeddings, exact local vectors, optional S3 Vectors ranker.

No default credentials, provisioning, arbitrary file ingestion, cloud writes or
Strands tools that let the model choose an index/scope. Only explicitly approved
public strings can reach Bedrock. Returned text is always read from Registry.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import fsum, isfinite, sqrt
from pathlib import Path
from threading import Lock
from types import MappingProxyType
from typing import Callable
import json

from .research_corpus import Chunk, Registry
from .semantic_errors import SemanticUnavailable

MODEL_ID = 'amazon.titan-embed-text-v2:0'
ADAPTER_CODE_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                      allow_nan=False).encode('utf-8')


def fingerprint(value) -> str:
    return sha256(canonical(value)).hexdigest()


@dataclass(frozen=True)
class EmbeddingConfig:
    dimensions: int = 256
    model_id: str = MODEL_ID
    normalize: bool = True

    def __post_init__(self):
        if self.model_id != MODEL_ID or type(self.dimensions) is not int or self.dimensions not in {256,512,1024} or self.normalize is not True:
            raise ValueError('Expected pinned normalized Titan V2 configuration')

    @property
    def revision(self):
        return f'bedrock:{self.model_id}:float:{self.dimensions}:normalized:v1'


def unit_vector(value, dimensions: int) -> tuple[float, ...]:
    if not isinstance(value, (list, tuple)) or len(value) != dimensions:
        raise ValueError('Embedding dimension mismatch')
    if any(type(x) not in (int,float) or not isfinite(x) for x in value):
        raise ValueError('Embedding must contain finite numbers')
    length = sqrt(fsum(float(x)**2 for x in value))
    if not isfinite(length) or length <= 0:
        raise ValueError('Embedding must be nonzero')
    return tuple(float(x)/length for x in value)


def binding(registry: Registry, chunk: Chunk) -> dict:
    source = registry.sources[chunk.source_id]
    return {'chunk_id':chunk.id, 'source_id':source.id,
            'original_sha256':source.original_sha256,
            'extraction_sha256':source.extraction_sha256, 'chunk_sha256':chunk.sha256,
            'start':chunk.start, 'end':chunk.end, 'contest_id':chunk.contest_id,
            'applicability':chunk.applicability, 'location':chunk.location,
            'authority':source.authority, 'state':source.state, 'county':source.county,
            'election_date':source.election_date, 'role':source.role,
            'effective_from':source.effective_from, 'retrieved_date':source.retrieved_date}


def public_manifest(registry: Registry, approved_sources: dict[str,str],
                    config: EmbeddingConfig) -> dict:
    """Application supplies exact public-source versions; no path scanning.

    Hash approval is explicit human-reviewed public provenance, not a classifier
    that guesses privacy from a government-looking URL or filename.
    """
    if not approved_sources or set(approved_sources) - set(registry.sources):
        raise ValueError('Explicit known public source approvals required')
    for ident, expected in approved_sources.items():
        source = registry.sources[ident]
        if expected != source.original_sha256 or source.quality not in {'verified_reading_copy','native_html'}:
            raise ValueError('Public source version or extraction not approved')
        registry.acquire(ident)
    records = [binding(registry,c) for c in sorted(registry.chunks.values(),key=lambda c:c.id)
               if c.source_id in approved_sources]
    if not records: raise ValueError('Empty approved public corpus')
    return {'schema':'open-oracle-public-vector-v1', 'encoder_revision':config.revision,
            'dimensions':config.dimensions, 'records':records}


class PublicTextPolicy:
    """Exact public strings only. Freeform visitor queries fall back locally.

    Never treat a model-created query as public by default. The application may
    explicitly approve scripted public demo queries; this object stores no visitor
    content and never records or exports text passed to its predicate.
    """
    def __init__(self, registry: Registry, manifest: dict, public_queries=()):
        hashes = set()
        for record in manifest['records']:
            chunk = registry.chunks[record['chunk_id']]
            if binding(registry,chunk) != record: raise ValueError('Manifest binding changed')
            hashes.add(sha256(chunk.text.encode()).hexdigest())
        queries = tuple(public_queries)
        if any(not isinstance(q,str) or not q.strip() or len(q)>240 for q in queries):
            raise ValueError('Invalid approved public demo query')
        self._hashes = frozenset(hashes | {sha256(q.encode()).hexdigest() for q in queries})

    def __call__(self, text: str) -> bool:
        return sha256(text.encode()).hexdigest() in self._hashes


class TitanEmbedder:
    """One explicit client, exact text approval, no retries, bounded attempted work.

    A caller's before_call checks its shared spend ledger/cancellation. This class
    limits attempts and UTF-8 bytes conservatively; it does not claim an invoice
    cap or token count. Failed calls consume attempted-work budget.
    """
    def __init__(self, client, *, config: EmbeddingConfig, approve_text: Callable[[str],bool],
                 max_calls: int, max_input_bytes: int, before_call=lambda: None):
        if type(max_calls) is not int or not 1<=max_calls<=200 or type(max_input_bytes) is not int or not 1<=max_input_bytes<=1000000:
            raise ValueError('Explicit bounded embedding budget required')
        self.client, self.config, self.approve_text = client, config, approve_text
        self.max_calls, self.max_input_bytes, self.before_call = max_calls,max_input_bytes,before_call
        self.calls, self.input_bytes, self.input_tokens = 0,0,0
        self._lock=Lock()
        self.revision=config.revision

    def embed(self, text: str) -> tuple[float,...]:
        if not isinstance(text,str) or not text.strip() or len(text.encode())>8000:
            raise ValueError('Embedding input exceeds bounded public span')
        if not self.approve_text(text): raise SemanticUnavailable('input_not_approved')
        self.before_call()
        with self._lock:
            size=len(text.encode())
            if self.calls>=self.max_calls or self.input_bytes+size>self.max_input_bytes:
                raise SemanticUnavailable('call_budget')
            self.calls+=1; self.input_bytes+=size
        try:
            result=self.client.invoke_model(modelId=self.config.model_id,
                contentType='application/json', accept='application/json',
                body=canonical({'inputText':text,'dimensions':self.config.dimensions,
                                'normalize':True,'embeddingTypes':['float']}))
            body=result['body']
            try: raw=body.read(100000)
            finally: body.close()
        except Exception as exc:
            # Never serialize provider exception text or response contents.
            from botocore.exceptions import BotoCoreError, ClientError
            if isinstance(exc,(BotoCoreError,ClientError,OSError,TimeoutError)):
                raise SemanticUnavailable('provider_unavailable') from None
            raise
        try: data=json.loads(raw)
        except (ValueError,TypeError): raise ValueError('Malformed embedding response') from None
        tokens=data.get('inputTextTokenCount')
        if type(tokens) is not int or not 0<tokens<=8192:
            raise ValueError('Invalid embedding token count')
        vector=unit_vector(data.get('embedding'),self.config.dimensions)
        with self._lock: self.input_tokens+=tokens
        return vector


def workshop_clients(*, profile: str, region: str):
    """Construct existing-profile clients only, without an API request."""
    if profile!='open-oracle-event' or region!='us-east-1':
        raise ValueError('Expected authorized workshop profile/region')
    import boto3
    from botocore.config import Config
    session=boto3.Session(profile_name=profile,region_name=region)
    settings=Config(retries={'total_max_attempts':1},connect_timeout=3,read_timeout=5)
    return (session.client('bedrock-runtime',config=settings),
            session.client('s3vectors',config=settings))


def ingest_local(registry: Registry, manifest: dict, encoder) -> dict:
    """Reproducible ID/order/config/span bindings; vectors remain provider outputs.

    Build atomically in memory; caller writes only on success. No re-chunking,
    generated summaries or arbitrary directories/files enter ingestion.
    """
    if manifest['encoder_revision']!=encoder.revision: raise ValueError('Encoder revision mismatch')
    vectors={}
    for record in manifest['records']:
        chunk=registry.chunks[record['chunk_id']]
        registry.read(chunk.id)
        if binding(registry,chunk)!=record: raise ValueError('Ingestion span binding changed')
        vectors[chunk.id]=list(unit_vector(encoder.embed(chunk.text),manifest['dimensions']))
    # Revalidate originals after provider work, before publishing any artifact.
    for ident in {r['source_id'] for r in manifest['records']}: registry.acquire(ident)
    artifact={'manifest':manifest,'manifest_sha256':fingerprint(manifest),'vectors':vectors}
    return {**artifact,'artifact_sha256':fingerprint(artifact)}


@dataclass(frozen=True)
class PublicSearchHint:
    """Application-owned public query hint, never source evidence or visitor text."""
    contest_id: str
    purpose: str
    topic: str
    query: str

    def __post_init__(self):
        import re
        if (not isinstance(self.contest_id,str) or not re.fullmatch(r'[a-z0-9-]{1,60}',self.contest_id)
            or self.purpose not in {'ballot_fact','current_law','legal_reference'}
            or not isinstance(self.topic,str) or not re.fullmatch(r'[a-z][a-z0-9_-]{0,23}',self.topic)
            or not isinstance(self.query,str) or not self.query.strip() or len(self.query)>240):
            raise ValueError('Invalid application-owned public search hint')

    def descriptor(self):
        return {'contest_id':self.contest_id,'purpose':self.purpose,'topic':self.topic,'query':self.query}


class LocalVectorBackend:
    """Exact cosine search over already filtered candidates; no ANN service needed."""
    def __init__(self, registry: Registry, artifact: dict, encoder, *, check=lambda: None, search_hints=()):
        hints=tuple(search_hints)
        if len(hints)>8 or any(not isinstance(h,PublicSearchHint) or h.contest_id not in {c.contest_id for c in registry.chunks.values()} for h in hints):
            raise ValueError('Search hints require known contests and fixed public descriptors')
        self.search_hints=hints
        self.registry,self.encoder,self.check=registry,encoder,check
        unsigned={k:artifact[k] for k in ('manifest','manifest_sha256','vectors')}
        if fingerprint(unsigned)!=artifact.get('artifact_sha256') or fingerprint(artifact['manifest'])!=artifact['manifest_sha256']:
            raise ValueError('Vector artifact digest mismatch')
        manifest=artifact['manifest']
        if manifest['encoder_revision']!=encoder.revision: raise ValueError('Query encoder revision mismatch')
        self.dimensions=manifest['dimensions']
        self.records=MappingProxyType({r['chunk_id']:dict(r) for r in manifest['records']})
        if len(self.records)!=len(manifest['records']) or set(self.records)!=set(artifact['vectors']):
            raise ValueError('Vector manifest completeness mismatch')
        self.vectors=MappingProxyType({k:unit_vector(v,self.dimensions) for k,v in artifact['vectors'].items()})
        self.revision=f'{encoder.revision}:local-exact-cosine:{artifact["artifact_sha256"]}:code:{ADAPTER_CODE_SHA256}'
        if hints:
            self.revision += ":public-query-hints:" + fingerprint([h.descriptor() for h in hints])

    def validate_candidates(self, candidates):
        for chunk in candidates:
            self.check()
            record=self.records.get(chunk.id)
            if record is None: raise SemanticUnavailable('index_unavailable')
            if binding(self.registry,chunk)!=record: raise ValueError('Stale vector source binding')
            self.registry.read(chunk.id)

    def rank(self, query: str, candidates: tuple[Chunk,...]) -> list[str]:
        if not candidates: return []
        self.validate_candidates(candidates)
        # Validate the complete supplied scope FIRST, including controls. This
        # never silently excuses missing/stale vectors or weakens source checks.
        content = tuple(c for c in candidates if c.chunk_type == 'content')
        if not content: return []
        vector=unit_vector(self.encoder.embed(query),self.dimensions)
        self.check()
        scores={c.id:fsum(a*b for a,b in zip(vector,self.vectors[c.id])) for c in content}
        self.validate_candidates(candidates)
        return sorted(scores,key=lambda ident:(-scores[ident],ident))


class S3VectorBackend(LocalVectorBackend):
    """Optional read-only S3 Vectors adapter, staged until resource approval.

    Input candidate bindings restrict the query AND every response is rebound
    locally. Cloud metadata/content never becomes a citation or an instruction.
    The supplied index ARN is application-owned, never a tool argument.
    """
    def __init__(self, registry, artifact, encoder, *, client, index_arn: str, check=lambda: None):
        super().__init__(registry,artifact,encoder,check=check)
        import re
        if not re.fullmatch(r'arn:aws:s3vectors:us-east-1:123456789012:bucket/[a-z0-9-]+/index/[a-z0-9-]+',index_arn):
            raise ValueError('Expected workshop vector index ARN')
        self.client,self.index_arn=client,index_arn
        self.manifest_sha256=artifact['manifest_sha256']
        self.revision=f'{encoder.revision}:s3vectors:{self.manifest_sha256}:index:{fingerprint(index_arn)}:code:{ADAPTER_CODE_SHA256}'

    def rank(self, query, candidates):
        if not candidates: return []
        self.validate_candidates(candidates)
        content = tuple(c for c in candidates if c.chunk_type == 'content')
        if not content: return []
        allowed={fingerprint(self.records[c.id]):c.id for c in content}
        vector=unit_vector(self.encoder.embed(query),self.dimensions)
        self.check()
        try:
            result=self.client.query_vectors(indexArn=self.index_arn,topK=min(8,len(content)),
                queryVector={'float32':list(vector)},returnMetadata=True,returnDistance=True,
                filter={'$and':[{'manifest_sha256':{'$eq':self.manifest_sha256}},
                                {'binding_sha256':{'$in':sorted(allowed)}}]})
        except Exception as exc:
            from botocore.exceptions import BotoCoreError, ClientError
            if isinstance(exc,(BotoCoreError,ClientError,OSError,TimeoutError)):
                raise SemanticUnavailable('provider_unavailable') from None
            raise
        rows=[]
        seen=set()
        for row in result.get('vectors',[]):
            key=row.get('key'); metadata=row.get('metadata',{}); distance=row.get('distance')
            if key not in allowed or key in seen or metadata != {
                    'binding_sha256':key,'manifest_sha256':self.manifest_sha256}:
                raise ValueError('Unbound cloud vector result')
            if type(distance) not in (int,float) or not isfinite(distance) or not 0<=distance<=2:
                raise ValueError('Invalid cosine distance')
            seen.add(key); rows.append((float(distance),allowed[key]))
        self.validate_candidates(candidates)
        return [ident for _,ident in sorted(rows)]


def s3_vector_records(artifact: dict) -> list[dict]:
    """Pure staging only: reviewed vectors + nonsecret hashes, no source text.

    Deliberately offers no PutVectors or resource creation function. The owner
    must validate/approve a specific resource and capped upload before using it.
    """
    output=[]
    for record in artifact['manifest']['records']:
        key=fingerprint(record)
        output.append({'key':key,'data':{'float32':artifact['vectors'][record['chunk_id']]},
            'metadata':{'binding_sha256':key,'manifest_sha256':artifact['manifest_sha256']}})
    return output
