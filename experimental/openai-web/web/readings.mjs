// Application-owned language/intent/evidence bindings, not model-authored facts.
import { immutableCopy } from "./core.mjs";
export function admittedReadings(corpus, mapPin) {
  return immutableCopy([
    {
      id: "rate-en",
      intent: "rate",
      locale: "en",
      text:
        corpus.claims.rate.text +
        " This is a retained public sample, not your personal ballot.",
      source_version: corpus.sources[0].text_sha256,
      release_policy: "admitted_en_measure",
    },
    {
      id: "maps-en",
      intent: "maps",
      locale: "en",
      text: "Both maps are shown together. Choose a view or a district number. Read the source and version notes below. Your personal district has not been verified.",
      source_version: mapPin.sha256,
      release_policy: "ui_navigation",
    },
    {
      id: "maps-es",
      intent: "maps",
      locale: "es",
      text: "Los dos mapas se muestran juntos. Elija una vista o un número de distrito. Consulte las fuentes y las versiones debajo de los mapas. No se ha verificado su distrito personal.",
      source_version: mapPin.sha256,
      release_policy: "ui_navigation",
    },
  ]);
}
export function bindReading(asset, readings, intent, locale) {
  const admitted = readings.find(
    (r) => r.intent === intent && r.locale === locale,
  );
  if (
    !admitted ||
    !asset ||
    Object.entries(admitted).some(([key, value]) => asset[key] !== value) ||
    asset.kind !== "synthetic_prepared_voice" ||
    !/^[a-f0-9]{64}$/.test(asset.sha256) ||
    !Number.isInteger(asset.bytes) ||
    asset.bytes < 44 ||
    asset.bytes > 4 * 1024 * 1024
  )
    return null;
  return immutableCopy({
    asset,
    text: admitted.text,
    sourceVersion: admitted.source_version,
  });
}
