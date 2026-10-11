"""Two outputs from existing readability reports; no duplicate Strands tool."""
from copy import deepcopy
from .review_contract import CLARITY_CHECKS, request, parse_review

STYLES = ('college_detail', 'high_school', 'middle_school', 'simplest_useful')


def clarity_draft(candidate, original, paired_english=None):
    if candidate['language'] not in ('en', 'es') or candidate['explanation_style'] not in STYLES:
        raise ValueError('Unsupported controlled fixture style/language')
    return request({'candidate': candidate['text'], 'requested_language': candidate['language'],
                    'requested_style': candidate['explanation_style'], 'original_source': original,
                    'scope': candidate['scope'], 'election_date': candidate['election_date'],
                    'paired_english': paired_english, 'education_inference': 'forbidden'}, CLARITY_CHECKS)


def checked_result(formula_report, clarity_payload, clarity_raw=None):
    """Formula stays byte-equivalent. Model findings are distinct and diagnostic only.

    Caller must verify source/language/operation binding independently. This pure
    offline projection does not create a checked-result receipt or release token.
    """
    from open_oracle.readability import analyze_readability
    formula = deepcopy(formula_report)
    expected = analyze_readability(formula['raw_text'], formula['label'], formula['provenance'],
                                   formula['language'], formula['extraction_method'])
    if any(formula.get(k) != value for k, value in expected.items()):
        raise ValueError('Formula report differs from existing reproducible implementation')
    if formula.get('language') not in ('en', 'en-US', 'en-GB') and formula.get('scores') is not None:
        raise ValueError('Inapplicable English formula cannot score non-English')
    clarity = ({'status': 'unrun', 'checks': [], 'calibration': 'not_validated',
                'comprehension': 'not_measured', 'release_authorized': False}
               if clarity_raw is None else parse_review(clarity_payload, clarity_raw))
    return {'contract': 'readability_two_output_eval_v1', 'formula': formula,
            'clarity_review': clarity, 'composite_score': None,
            'factual_admission': 'separate_mandatory', 'production_release_authorized': False,
            'education_inference': 'forbidden', 'human_comprehension': 'not_measured'}


def run_fixture_matrix(bundle):
    """Invoke actual existing tool eight times, never infer provider/style quality."""
    from open_oracle.readability import build_readability_tool
    scorer = build_readability_tool()
    out = []
    for row in bundle['styles']:
        report = scorer(text=row['text'], label='Authored COMBAT explanation fixture', language=row['language'])
        english = next(x['text'] for x in bundle['styles'] if x['language'] == 'en'
                       and x['explanation_style'] == row['explanation_style'])
        draft = clarity_draft(row, bundle['source'], english)
        out.append({'language': row['language'], 'style': row['explanation_style'],
                    'execution': 'actual_sdk_tool_with_authored_public_fixture',
                    'label_status': 'agent_authored_unreviewed',
                    'outputs': checked_result(report, draft), 'decisions_request_unexecuted': draft})
    return out
