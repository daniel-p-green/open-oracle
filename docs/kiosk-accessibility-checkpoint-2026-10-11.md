# Kiosk accessibility checkpoint — October 11, 2026

Actual headless Mac Chrome inspected root and Copilot at 1280×720 and 320×700,
in idle, Amendment 7 answer and expanded-source states: twelve states total.
This used a separate source-only 18810 test instance; existing rehearsal servers
and shared GUI state were unchanged. Voice/provider requests, external network
and media capture were blocked. The test-only browser bypassed CSP to inject axe;
the application CSP was not changed.

Axe-core 4.10.3 (official npm distribution, MIT license) reported zero automated
WCAG-tagged violations. All twelve states had no horizontal overflow; no measured
visible enabled button was below 24×24 pixels. Keyboard Enter reached the answer
and source disclosure; Erase restored question focus. Page errors, external
requests, provider calls and capture calls were all zero. Screenshots and JSON
are in the isolated integration directory, not the public repository.

Injected axe distribution SHA256: `880970c081707360e64f34cea25ff91892f5bc95675b0776925b9709dd8a68bb`.

The root idle ARIA finding was fixed by giving the labeled example-question
container its semantic `group` role. The actual rerun at 11:54 UTC (6:54 a.m.
Central) has no root incomplete checks. This changes no visual styles.
Audit harness SHA256: `6e841bd8b27899e2004f8e10585abe07da467e84e72306305dc444ba2f69114e`.

## Still requires acceptance

- Copilot: contrast could not be automatically decided for 12 idle, 21 answer and
  44 source nodes at each size. Incomplete checks are not passing contrast proof.
- Actual screen-reader behavior, 200–400% magnification, full keyboard order/
  focus visibility, hardware TV/Pi behavior, human audio/captions and Daniel's
  visual acceptance were not verified.

This is a scoped automated/keyboard/reflow audit, not WCAG conformance or a final
physical kiosk accessibility sign-off. Keep OO-A11Y-001 ready for manual verification.
