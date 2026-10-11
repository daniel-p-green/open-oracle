# Numeric speech transcript fidelity

The prior punctuation-erasing comparator could treat `−0.25` as `0.25`. A synthetic valid closure/audio fixture demonstrated that counterexample; it is not evidence of a historical audible failure.

Client and WebSocket checks now preserve signed numeric tokens, decimal/grouping punctuation, percent/per-mille and currency markers. Ordinary prose punctuation and case may still vary. Numeric spelling/unit equivalences are deliberately not inferred: a changed or uncertain representation is held. Unicode minus and ASCII minus are the same explicit negative sign; removal/addition is not.

Eleven altered-value cases fail closed, unchanged-value synthetic closure passes, and client/server normalization matches. Existing Live event and lifecycle suites pass. These checks cannot prove that recorded audio says its transcript: actual heard-audio validation remains necessary. No microphone, speakers or live provider was used.
