"""One bounded Responses composition. No visitor text or generated facts."""
import json
from providers import Held, check_cancel
from journey import JourneyPipeline, TASKS
from fresh_speech import FreshSpeechPipeline, TASKS as SPEECH_TASKS

RECIPES = {
    'effects': ['scope', 'effects', 'original'],
    'rate': ['scope', 'facts', 'original'],
    'duration': ['scope', 'facts', 'original'],
    'purpose': ['scope', 'facts', 'original'],
    'maps': ['scope', 'maps', 'map_sources'],
    'candidates': ['scope', 'coverage'],
    'unknown': ['scope', 'coverage'],
}


class ProductPipeline:
    def __init__(self, base, allow_spanish=False, text_model='gpt-6-luna', voice_fixtures=None):
        self.base = base
        self.journey = JourneyPipeline(base.provider, allow_spanish, text_model)
        self.speech = FreshSpeechPipeline(base.provider, allow_spanish)
        # The four-purpose manual trial package is consumed. A web review
        # switch/max_runs cannot silently authorize another native session.
        if voice_fixtures: raise Held('native_voice_package_closed')
        self.voice_fixtures=None
        self.voice_languages=[]

    def run(self, cancel, stage, meter):
        return self.base.run(cancel, stage, meter)

    def run_task(self, task, cancel, stage, meter, prior=None):
        check_cancel(cancel)
        if task in {'voice:synthetic:en','voice:synthetic:es'}:
            if not self.voice_fixtures: raise Held('synthetic_voice_unavailable')
            import asyncio
            from voice_agent import PublicSyntheticVoiceLoop, load_synthetic_fixtures
            language=task.rsplit(':',1)[1]
            fixtures=load_synthetic_fixtures(self.voice_fixtures,language)
            result=asyncio.run(PublicSyntheticVoiceLoop(self.base.provider,language=language,seconds=45).run(
                fixtures,cancel,meter,lambda value:stage('audio',value)))
            if result.get('all_turns_checked') is not True:
                raise Held('voice_native_usage_unconfirmed' if 'voice_native_usage_unconfirmed' in result.get('errors',[]) else 'voice_deadline' if 'voice_deadline' in result.get('errors',[]) else 'voice_session_held')
            return result,b''
        if task in TASKS:
            return self.journey.run_task(task, cancel, stage, meter, prior=prior)
        if task in SPEECH_TASKS:
            return self.speech.run_task(task,cancel,stage,meter,prior=prior)
        if not isinstance(task, str) or not task.startswith('layout:') or task[7:] not in RECIPES:
            raise Held('task_unadmitted')
        intent = task[7:]
        components = RECIPES[intent]
        schema = {'type': 'object', 'properties': {
            'intent': {'type': 'string', 'enum': [intent]},
            'components': {'type': 'array', 'items': {'type': 'string', 'enum': components},
                           'minItems': len(components), 'maxItems': len(components)}},
            'required': ['intent', 'components'], 'additionalProperties': False}
        body = {'model': 'gpt-6-luna', 'store': False, 'max_output_tokens': 128,
                'service_tier': 'default', 'reasoning': {'effort': 'none'},
                'input': [{'role': 'developer', 'content': 'Compose a civic explanation interface using admitted component IDs only. Include every provided component exactly once. Put scope first. Prefer the visual explanation before original source details. Do not produce facts, links, prose or HTML.'},
                          {'role': 'user', 'content': json.dumps({'public_example_intent': intent, 'admitted_components': components})}],
                'text': {'format': {'type': 'json_schema', 'name': 'civic_layout', 'strict': True, 'schema': schema}}}
        # The transport's <=12,000-byte request bounds all input, including schema.
        # 128 total output tokens, no tools/history/background/retries. A $0.01
        # reservation covers even a conservative 12,000-token higher-write-rate
        # input estimate ($0.003064). This is token arithmetic, not an invoice.
        stage('text')
        generated = self.base.provider.post('responses', body, cancel)
        meter('text', generated.get('usage'))
        check_cancel(cancel)
        if generated.get('status') != 'completed': raise Held('layout_incomplete')
        raw = ''.join(c.get('text', '') for o in generated.get('output', []) if o.get('type') == 'message'
                      for c in o.get('content', []) if c.get('type') == 'output_text')
        try: draft = json.loads(raw)
        except Exception: raise Held('layout_invalid') from None
        if (type(draft) is not dict or set(draft) != {'intent', 'components'} or draft['intent'] != intent
                or type(draft['components']) is not list or len(draft['components']) != len(components)
                or any(type(c) is not str for c in draft['components'])
                or set(draft['components']) != set(components) or draft['components'][0] != 'scope'):
            raise Held('layout_unadmitted')
        return {'layout': draft, 'model': 'gpt-6-luna', 'mode': 'live_bounded_composition',
                'facts_generated': False, 'raw_visitor_input_sent': False}, b''
