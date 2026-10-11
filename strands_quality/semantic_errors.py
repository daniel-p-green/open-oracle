"""Only these fixed availability failures permit lexical fallback."""


class SemanticUnavailable(RuntimeError):
    def __init__(self, reason: str):
        if reason not in {'input_not_approved', 'call_budget', 'provider_unavailable',
                          'index_unavailable', 'no_semantic_matches'}:
            raise ValueError('Unknown semantic availability reason')
        self.reason = reason
        super().__init__(reason)
