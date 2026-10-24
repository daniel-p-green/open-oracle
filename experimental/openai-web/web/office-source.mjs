import { immutableCopy } from "./core.mjs";
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
