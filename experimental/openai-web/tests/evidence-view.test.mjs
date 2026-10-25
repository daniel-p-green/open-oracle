import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import {
  composeEvidence,
  validateEvidencePlan,
} from "../web/evidence-view.mjs";
import { QUESTION_VERSION, journeyReading } from "../web/journey-core.mjs";

test("evidence composition accepts component IDs only, preserves the shared spoken unit and holds foreign context", async () => {
  const fixture = JSON.parse(
    await readFile(new URL("../fixtures/evidence-plans.json", import.meta.url)),
  );
  for (const row of fixture.cases) {
    const draft = { components: row.components };
    if (row.accepted)
      assert.deepEqual(validateEvidencePlan(draft, row.operation), draft);
    else
      assert.throws(
        () => validateEvidencePlan(draft, row.operation),
        /unadmitted/,
      );
  }
  for (const draft of [
    null,
    {
      components: ["explanation", "original", "uncertainty"],
      url: "https://example.invalid",
    },
    {
      components: ["explanation", "original", "uncertainty"],
      visitor: "private",
    },
  ])
    assert.throws(() => validateEvidencePlan(draft, "overview"));
  const unit = {
    operation: "overview",
    language: "en",
    source_version: QUESTION_VERSION,
    request_fit: "confirmed",
    sections: [
      {
        source_id: "question",
        text: "The question asks about the congressional plan.",
      },
    ],
    presentation: { components: ["explanation", "original", "uncertainty"] },
    presentation_mode: "model_selected",
  };
  const before = journeyReading(unit);
  const context = {
    operation: "overview",
    language: "en",
    sourceVersion: QUESTION_VERSION,
    unit,
  };
  assert.equal(composeEvidence(context).mode, "model_selected");
  assert.equal(journeyReading(unit), before);
  assert.deepEqual(composeEvidence({ ...context, unit: null }).components, [
    "explanation",
    "choice_comparison",
    "original",
    "uncertainty",
    "map_reference",
  ]);
  assert.equal(composeEvidence({ ...context, unit: null }).mode, "local");
  for (const change of [
    { language: "es" },
    { sourceVersion: "foreign" },
    { operation: "limits" },
  ])
    assert.throws(() => composeEvidence({ ...context, ...change }));
  assert.throws(() =>
    composeEvidence({
      ...context,
      unit: {
        ...unit,
        presentation: {
          components: [
            "explanation",
            "original",
            "uncertainty",
            "candidate_ranking",
          ],
        },
      },
    }),
  );
});
