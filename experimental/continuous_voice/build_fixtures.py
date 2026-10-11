"""Offline source/release fixtures. Authored review labels are NOT API evidence."""
import json
from pathlib import Path
from open_oracle.corpus import Corpus
from open_oracle.engine import EvidenceLoop
from open_oracle.session_control import accepted_speech


class AuthoredReview:
    def review(self, envelope):
        return {'execution': 'real_api', 'status': 'accepted',
                'label': 'SYNTHETIC label to exercise real application source gate; no API call'}


def fixtures():
    corpus = Corpus()
    engine = EvidenceLoop(corpus, reviewer=AuthoredReview())
    turns = []
    for i, question in enumerate(('What is the COMBAT tax rate?', 'How long would the COMBAT tax last?'), 1):
        result = engine.answer(question, request_id=f'synthetic-request-{i}')
        assert accepted_speech(result, corpus), 'Offline contract fixture no longer passes canonical source gate'
        turns.append({'question': question, 'result': result})
    return {'synthetic': True, 'provider_calls': 0, 'physical_media': False, 'turns': turns}


if __name__ == '__main__':
    path = Path(__file__).with_name('proof') / 'synthetic-fixtures.json'
    path.write_text(json.dumps(fixtures(), indent=2) + '\n')
    print(json.dumps({'synthetic': True, 'generated_turns': 2, 'provider_calls': 0}))
