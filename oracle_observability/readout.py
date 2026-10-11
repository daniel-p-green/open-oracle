"""Accessible operator readout from aggregates only. No scripts or external assets."""
from html import escape


def render_dashboard(snapshot):
    esc = lambda v: escape(str(v), quote=True)
    tables = []
    for title, rows in (("Operation totals", snapshot["totals"]), *snapshot["counts"].items(),
                        *[("Observed " + k + " usage (lower bound)", v) for k, v in snapshot["observed_usage_lower_bound"].items()]):
        body = "".join(f"<tr><th scope='row'>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in sorted(rows.items()))
        tables.append(f"<section><h2>{esc(title)}</h2><table><caption>{esc(title)}</caption><thead><tr><th scope='col'>Metric</th><th scope='col'>Count or value</th></tr></thead><tbody>{body}</tbody></table></section>")
    notes = "".join(f"<li>{esc(x)}</li>" for x in snapshot["limitations"])
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Open Oracle operations</title><main><h1>Open Oracle operations</h1>"
            "<p>Local volatile aggregates. Refresh to read current counters. This readout contains no visitor questions or request history.</p>"
            f"<p>Deployment: <code>{esc(snapshot['deployment_sha256'])}</code><br>Source catalog: <code>{esc(snapshot['source_catalog_sha256'])}</code></p>"
            "<p>Small samples have no p95 estimate. Usage is an observed lower bound; unknown counters are shown separately. Costs are estimates, not invoices.</p>"
            + "".join(tables) + f"<h2>Limits</h2><ul>{notes}</ul></main></html>")
