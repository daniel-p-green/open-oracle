"""Synthetic language contracts for offline validation; no civic release authority."""
from dataclasses import asdict
import json
from pathlib import Path
import re
from .translation_validation import RetainedSource, TranslationForm, Feature, text_hash

SCOPE = {'election_date': '2026-11-03', 'jurisdiction': 'Jackson County, Missouri'}
SENTENCES = {
 'rate': 'If approved, the COMBAT sales tax would continue at 0.25 cent for 10 years.',
 'dates': 'The election date is 2026-11-03 in Jackson County, Missouri.',
 'polarity': 'A YES vote approves the printed proposal. A NO vote rejects the printed proposal.',
 'exception': 'The proposal does not repeal the tax, except under the printed condition.',
 'attribution': 'Candidate Example states: "I support the proposal." This is an attributed statement, not an independently verified result.',
}
SPAN_FEATURES = {
 'rate': [('condition','conditional','approved'),('number','0.25','0.25'),('unit','cent','cent'),('number','10','10'),('unit','year','years'),('attribution','COMBAT','COMBAT')],
 'dates': [('date','2026-11-03','2026-11-03'),('scope','Jackson County, Missouri','Jackson County, Missouri')],
 'polarity': [('polarity','YES','YES'),('polarity','approve','approves'),('polarity','NO','NO'),('polarity','reject','rejects')],
 'exception': [('negation','not_repeal','does not repeal'),('exception','except','except'),('condition','printed','the printed condition')],
 'attribution': [('attribution','Candidate Example','Candidate Example'),('attribution','states','states'),('attribution','attributed','attributed statement'),('negation','not_verified','not an independently verified result')],
}
ES = {
 'rate': ('Si se aprueba, el impuesto sobre las ventas COMBAT continuaría a una tasa de 0.25 centavo durante 10 años.', ['aprueba','0.25','centavo','10','años','COMBAT']),
 'dates': ('La fecha de la elección es 2026-11-03 en Jackson County, Missouri.', ['2026-11-03','Jackson County, Missouri']),
 'polarity': ('Un voto YES aprueba la propuesta impresa. Un voto NO rechaza la propuesta impresa.', ['YES','aprueba','NO','rechaza']),
 'exception': ('La propuesta no deroga el impuesto, excepto bajo la condición impresa.', ['no deroga','excepto','la condición impresa']),
 'attribution': ('Candidate Example declara: "Apoyo la propuesta." Esta es una declaración atribuida, no un resultado verificado de forma independiente.', ['Candidate Example','declara','declaración atribuida','no un resultado verificado de forma independiente']),
}

def fixtures():
    sources, forms = {}, []
    for key, sentence in SENTENCES.items():
        source = RetainedSource('synthetic:'+key,sentence,'en','Synthetic fixture, not an election source',
            'attributed_candidate_statement' if key=='attribution' else 'official_ballot',
            'offline synthetic; not real ballot wording',tuple(sorted(SCOPE.items())),text_hash(sentence),'current_snapshot',True)
        sources[source.id] = source
        target, anchors = ES[key]
        features = tuple(Feature(kind,value,phrase,phrase,target_phrase) for (kind,value,phrase),target_phrase in zip(SPAN_FEATURES[key],anchors))
        forms.append(TranslationForm('es:'+key,source.id,source.binding(),0,len(sentence),sentence,sentence,target,'es',features))
    expanded = Path(__file__).resolve().parents[1]/'fixtures/expanded_translations.json'
    if expanded.exists():
        for row in json.loads(expanded.read_text())['translations']:
            key,language = row['id'],row['language']
            source = sources['synthetic:'+key]
            feature_map = {f['source_phrase']: f['target_phrase'] for f in row['features']}
            features = tuple(Feature(kind,value,phrase,phrase,feature_map[phrase]) for kind,value,phrase in SPAN_FEATURES[key])
            forms.append(TranslationForm(language+':'+key,source.id,source.binding(),0,len(source.text),source.text,source.text,row['target'],language,features))
    return sources, forms

def accepted_fixture_transport(resource, request):
    """Authored API-shaped events only: never claim live semantic verification."""
    if resource != 'decisions': raise ValueError('fixture_resource')
    return {'model':'gpt-6-luna','answers':[{'type':'predicate','name':q['name'],'probability':1.0} for q in request['questions']]}

def export_fixture_result(result):
    return {**result,'execution':'offline_authored_fixture','civic_source':'synthetic_not_official'}

def official_fixtures():
    """Exact retained proposal spans; all target forms still offline fixtures."""
    root=Path(__file__).resolve().parents[1]/'fixtures'
    source=json.loads((root/'official_combat.json').read_text())['evidence']
    retained=RetainedSource(source['id'],source['text'],'en',source['issuer'],'official_ballot',
        'retained November 3, 2026 sample, not personal applicability',tuple(sorted(SCOPE.items())),source['sha256'],source['status'],True)
    forms=[]
    for row in json.loads((root/'official_translations.json').read_text())['translations']:
        pattern=r'\s+'.join(re.escape(word) for word in row['source_quote'].split())
        match=re.search(pattern,retained.text)
        if not match:raise ValueError('official_fixture_span_missing')
        features=tuple(Feature(f['kind'],f['source_phrase'],f['source_phrase'],f['english_phrase'],f['target_phrase']) for f in row['features'])
        forms.append(TranslationForm(row['language']+':'+row['id'],retained.id,retained.binding(),match.start(),match.end(),match.group(),row['english'],row['target'],row['language'],features))
    return {retained.id:retained},forms
