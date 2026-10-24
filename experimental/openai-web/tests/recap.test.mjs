import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { webcrypto } from "node:crypto";
import {
  loadBrowseInventory,
  INVENTORY_VERSION,
} from "../web/office-source.mjs";
import {
  addRecapSource,
  recapSourceCards,
  loadOfficialNextSteps,
} from "../web/recap-view.mjs";

test("explicit recap selections stay versioned and source-specific without inventing a ballot", async () => {
  Object.defineProperty(globalThis, "crypto", {
    value: webcrypto,
    configurable: true,
  });
  const oldFetch = globalThis.fetch;
  try {
    globalThis.fetch = async (url) => {
      const bytes = await readFile(
        new URL("../fixtures/" + url.slice(1), import.meta.url),
      );
      return {
        ok: true,
        arrayBuffer: async () => Uint8Array.from(bytes).buffer,
      };
    };
    const inventory = await loadBrowseInventory(new AbortController().signal);
    const select = (source_id, contest_id) => ({
      source_id,
      contest_id,
      browse_version: INVENTORY_VERSION,
    });
    const kc = select("kc-sample", "us-house-5"),
      bond = select("jceb", "independence-bond-1");
    let choices = addRecapSource([], kc, inventory);
    choices = addRecapSource(choices, bond, inventory);
    choices = addRecapSource(choices, kc, inventory);
    assert.equal(choices.length, 2);
    const [municipal, house] = recapSourceCards(choices, inventory);
    assert.match(municipal.wording, /\$19,900,000/);
    assert.match(municipal.url, /jcebmo\.org\/.*#page=2$/);
    assert.equal(house.rows.length, 3);
    assert.equal(house.rows[2].name, "RANDALL (RANDY) LANGKRAEHR");
    assert.match(house.context, /W1-P7/);
    assert.equal(house.background_missing, true);
    assert.match(house.url, /kceb\.org\/ballots\/01-00006-01-NON.pdf#page=1$/);
    assert.throws(
      () =>
        addRecapSource(
          choices,
          select("kc-sample", "independence-bond-1"),
          inventory,
        ),
      /recap_context/,
    );
    assert.throws(
      () =>
        addRecapSource(choices, { ...kc, browse_version: "old" }, inventory),
      /recap_version/,
    );
    assert.throws(
      () =>
        addRecapSource(
          choices,
          { ...kc, visitor_text: "unapproved" },
          inventory,
        ),
      /recap_version/,
    );
    const unsafe = structuredClone(inventory);
    unsafe.sources.jceb.url = "javascript:alert(1)";
    assert.throws(() => recapSourceCards([bond], unsafe), /recap_url/);
    const changed = structuredClone(inventory);
    changed.contests.find((c) => c.id === "us-house-5").kind = "generated_html";
    assert.throws(() => recapSourceCards([kc], changed), /recap_component/);
    for (const id of [
      "auditor",
      "state-house-24",
      "county-executive",
      "county-at-large-1",
      "county-at-large-2",
      "county-at-large-3",
    ])
      choices = addRecapSource(choices, select("kc-sample", id), inventory);
    assert.equal(choices.length, 6);
    assert.ok(!choices.some((s) => s.contest_id === "independence-bond-1"));
    const next = await loadOfficialNextSteps(new AbortController().signal);
    assert.equal(next.sources.kceb.url, "https://kceb.org/voters/status/");
    assert.equal(next.sources.jceb.url, "https://jcebmo.org/sample-ballot/");
    assert.equal(next.limits.private_input_collected, false);
    assert.equal(next.limits.lookup_results_imported, false);
    globalThis.fetch = async () => ({
      ok: true,
      arrayBuffer: async () => new TextEncoder().encode("{}").buffer,
    });
    await assert.rejects(
      loadOfficialNextSteps(new AbortController().signal),
      /nextsteps_integrity/,
    );
  } finally {
    globalThis.fetch = oldFetch;
  }
});
