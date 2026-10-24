import { immutableCopy } from "./core.mjs";
export const INVENTORY_VERSION =
  "81b3a31203b7522b8489dadf4d5497490116ba08f8b0cc3d6320a091d04b39b2";
const NOTICE_VERSION =
  "0eda572a493274e25e845a1276b8ec28c3321dc40a8c2f13b7d761ad95645773";
const SAMPLE_VERSION =
  "690a32a8df2b24ccec68fb6d725f469a9467a7ce8ba76cfc1c74244cbb39323e";
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
  if ((await sha(bytes)) !== NOTICE_VERSION) throw Error("inventory_integrity");
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

export async function loadKcPublicSample(signal) {
  const response = await fetch("/kc-public-sample.json", {
    cache: "no-store",
    signal,
  });
  if (!response.ok) throw Error("sample_unavailable");
  const bytes = await response.arrayBuffer();
  if ((await sha(bytes)) !== SAMPLE_VERSION) throw Error("sample_integrity");
  const sample = JSON.parse(new TextDecoder().decode(bytes));
  if (
    sample.schema !== "openoracle-public-sample/v1" ||
    sample.sample_variant !== "W1-P7" ||
    sample.election_date !== "2026-11-03" ||
    sample.scope.personal_membership !== false ||
    sample.scope.county_inventory_complete !== false ||
    sample.contests.length !== 25 ||
    new Set(sample.contests.map((c) => c.id)).size !== 25
  )
    throw Error("sample_scope");
  for (const contest of sample.contests) {
    const occurrence = contest.occurrences[0];
    if (
      contest.occurrences.length !== 1 ||
      occurrence.source_id !== "kc-sample" ||
      occurrence.page < 1 ||
      occurrence.page > 2
    )
      throw Error("sample_source");
    if (
      occurrence.wording &&
      (await sha(new TextEncoder().encode(occurrence.wording))) !==
        occurrence.wording_sha256
    )
      throw Error("sample_wording");
  }
  return immutableCopy(sample);
}

export async function loadBrowseInventory(signal) {
  // Independently pinned contexts. Never label the notice union as W1-P7 or
  // join notice-only municipal questions into the sample's ballot style.
  const [notices, sample] = await Promise.all([
    loadContestInventory(signal),
    loadKcPublicSample(signal),
  ]);
  const browseVersion = await sha(
    new TextEncoder().encode(NOTICE_VERSION + ":" + SAMPLE_VERSION),
  );
  if (browseVersion !== INVENTORY_VERSION) throw Error("browse_version");
  const contests = structuredClone(notices.contests);
  for (const contest of sample.contests) {
    const target = contests.find((c) => c.id === contest.id);
    if (
      !target ||
      target.kind !== contest.kind ||
      target.label !== contest.label ||
      contest.occurrences.length !== 1
    )
      throw Error("sample_contest");
    target.occurrences.push(contest.occurrences[0]);
  }
  return immutableCopy({
    ...notices,
    browse_version: browseVersion,
    sources: { ...notices.sources, "kc-sample": sample.source },
    contests,
  });
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
