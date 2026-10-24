import { immutableCopy } from "./core.mjs";
export const INVENTORY_VERSION =
  "0eda572a493274e25e845a1276b8ec28c3321dc40a8c2f13b7d761ad95645773";
const PIN = "fa7e83103a9b3aa6e7461fada14d33ad9ee8f484701df33c8d4804c63d720151";
const sha = async (bytes) =>
  [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("");
export async function loadHouseOffice(signal) {
  const response = await fetch("/house-office.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("office_unavailable");
  const bytes = await response.arrayBuffer();
  if ((await sha(bytes)) !== PIN) throw Error("office_integrity");
  const source = JSON.parse(new TextDecoder().decode(bytes));
  for (const passage of source.passages)
    if ((await sha(new TextEncoder().encode(passage.text))) !== passage.sha256)
      throw Error("office_passage");
  return immutableCopy(source);
}

export async function loadSampleHouseContest(signal) {
  const response = await fetch("/sample-house-contest.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("contest_unavailable");
  const bytes = await response.arrayBuffer();
  if (
    (await sha(bytes)) !==
    "2e32afe9e35c81640dc2208b57979f3ef8a3cb709564261d76a516dc38adedf1"
  )
    throw Error("contest_integrity");
  return immutableCopy(JSON.parse(new TextDecoder().decode(bytes)));
}

export async function loadContestInventory(signal) {
  const response = await fetch("/contest-inventory.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("inventory_unavailable");
  const bytes = await response.arrayBuffer();
  if ((await sha(bytes)) !== INVENTORY_VERSION)
    throw Error("inventory_integrity");
  const value = JSON.parse(new TextDecoder().decode(bytes));
  if (
    value.election_date !== "2026-11-03" ||
    value.scope.personal_membership !== false ||
    value.scope.individual_ballot_styles_enumerated !== false ||
    value.contests.length !== 55 ||
    new Set(value.contests.map((c) => c.id)).size !== 55
  )
    throw Error("inventory_scope");
  for (const contest of value.contests) {
    if (
      !["candidate_election", "judicial_retention", "measure"].includes(
        contest.kind,
      ) ||
      !contest.occurrences.length
    )
      throw Error("inventory_contest");
    for (const occurrence of contest.occurrences) {
      const source = value.sources[occurrence.source_id];
      if (!source || occurrence.page < 1 || occurrence.page > source.pages)
        throw Error("inventory_source");
      if (
        occurrence.wording &&
        (await sha(new TextEncoder().encode(occurrence.wording))) !==
          occurrence.wording_sha256
      )
        throw Error("inventory_wording");
    }
  }
  return immutableCopy(value);
}

export function officeFamily(contest) {
  if (contest?.kind !== "candidate_election") return null;
  if (/^us-house-\d+$/.test(contest.id)) return "us-house";
  if (/^state-house-\d+$/.test(contest.id)) return "mo-house";
  if (/^state-senate-\d+$/.test(contest.id)) return "mo-senate";
  if (contest.id === "auditor") return "mo-auditor";
  return null;
}

export async function loadOfficeContext(family, signal) {
  if (family === "us-house") {
    const value = await loadHouseOffice(signal);
    return immutableCopy({
      office: value.office,
      source_version: PIN,
      missing_fields: [],
      passages: value.passages.map((p) => ({
        ...p,
        source: {
          publisher: value.publisher,
          url: value.url,
          retrieved_utc: value.retrieved_utc,
        },
      })),
    });
  }
  if (!["mo-house", "mo-senate", "mo-auditor"].includes(family))
    throw Error("office_unadmitted");
  const response = await fetch("/office-contexts.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("office_unavailable");
  const bytes = await response.arrayBuffer();
  if (
    (await sha(bytes)) !==
    "319fe5d1a34d91ff3f6abf5ce0989abb5871f28673cb9ab752941821d48bd6b3"
  )
    throw Error("office_integrity");
  const value = JSON.parse(new TextDecoder().decode(bytes));
  if (
    value.schema !== "openoracle-office-context/v1" ||
    value.limits.candidate_performance !== false ||
    value.limits.personal_membership !== false
  )
    throw Error("office_scope");
  const office = value.offices[family];
  const passages = [];
  for (const id of office.passage_ids) {
    const passage = value.passages[id],
      source = value.sources[passage.source_id];
    if (
      !source ||
      (await sha(new TextEncoder().encode(passage.text))) !== passage.sha256
    )
      throw Error("office_passage");
    passages.push({ ...passage, source });
  }
  return immutableCopy({
    office: office.title,
    passages,
    missing_fields: office.missing_fields,
    source_version:
      "319fe5d1a34d91ff3f6abf5ce0989abb5871f28673cb9ab752941821d48bd6b3",
  });
}
