import { immutableCopy } from "./core.mjs";
import { loadKcPublicSample } from "./office-source.mjs";
export const QUESTION_VERSION =
  "09406d86232da1835b4258132ad8eb7c3f22e5098e390fb7b7dcc44f3cec68ec";
export async function loadMapMeasure(signal) {
  const response = await fetch("/proposition-a.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("measure_unavailable");
  const bytes = await response.arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
  if (hash !== QUESTION_VERSION) throw Error("measure_integrity");
  const question = JSON.parse(new TextDecoder().decode(bytes));
  const sample = await loadKcPublicSample(signal);
  const wording = sample.contests.find((c) => c.id === "proposition-a")
    ?.occurrences[0];
  const normalized = (text) => text.replace(/\s+/g, " ").trim();
  const fullText = normalized(wording?.wording ?? "");
  const sentence = normalized(question.text);
  if (
    sample.source.original_sha256 !== question.artifact_sha256 ||
    wording?.page !== question.page ||
    !fullText.startsWith(sentence + " ")
  )
    throw Error("measure_sample_parity");
  return immutableCopy({
    ...question,
    complete_wording: wording.wording,
    printed_fiscal_note: fullText.slice(sentence.length).trim(),
    source_version: QUESTION_VERSION,
  });
}

const STATUS_PIN =
  "0c8ab9d2baddce7f90972608a72e7db57d389d7102dd791bc70e44402fe42d9f";
export function mapStatusCurrent(record, now = Date.now()) {
  return (
    Number.isFinite(now) &&
    Number.isFinite(Date.parse(record?.review_before_utc)) &&
    now < Date.parse(record.review_before_utc)
  );
}
export async function loadMapStatus(signal) {
  const response = await fetch("/map-status.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("status_unavailable");
  const bytes = await response.arrayBuffer();
  const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
  if (hash !== STATUS_PIN) throw Error("status_integrity");
  const record = JSON.parse(new TextDecoder().decode(bytes));
  if (!mapStatusCurrent(record)) throw Error("status_stale");
  return immutableCopy(record);
}
