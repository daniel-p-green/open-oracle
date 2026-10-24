import { immutableCopy } from "./core.mjs";
const PIN = "09406d86232da1835b4258132ad8eb7c3f22e5098e390fb7b7dcc44f3cec68ec";
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
  if (hash !== PIN) throw Error("measure_integrity");
  return immutableCopy(JSON.parse(new TextDecoder().decode(bytes)));
}

const STATUS_PIN =
  "0c8ab9d2baddce7f90972608a72e7db57d389d7102dd791bc70e44402fe42d9f";
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
  if (!(Date.now() < Date.parse(record.review_before_utc)))
    throw Error("status_stale");
  return immutableCopy(record);
}
