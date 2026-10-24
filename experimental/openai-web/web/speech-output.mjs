import { immutableCopy } from "./core.mjs";
export function createSpeechOutput({
  session,
  fetchAudio = (url, signal) => fetch(url, { signal, cache: "no-store" }),
  audioFactory = () => new Audio(),
  onChange = () => {},
}) {
  let generation = 0,
    controller,
    preparationTimer,
    prepared,
    player,
    url,
    consent = false,
    stage = "off";
  const emit = () =>
    onChange(
      immutableCopy({
        stage,
        reading: prepared?.asset.text ?? "",
        locale: prepared?.asset.locale ?? "",
        consent,
        playable: stage === "ready" && consent,
      }),
    );
  function discard() {
    clearTimeout(preparationTimer);
    controller?.abort();
    controller = null;
    if (player) {
      player.pause();
      player.removeAttribute?.("src");
      player.load?.();
      player = null;
    }
    if (url) {
      URL.revokeObjectURL(url);
      url = null;
    }
    prepared = null;
  }
  function stop({ revokeConsent = false } = {}) {
    ++generation;
    discard();
    if (revokeConsent) consent = false;
    stage = "off";
    emit();
  }
  async function prepare(asset, binding) {
    stop();
    if (!asset) {
      stage = "held";
      emit();
      return false;
    }
    const g = generation,
      ticket = binding.ticket;
    // Snapshot before the first await: a caller cannot rewrite the checked reading.
    [asset, binding] = immutableCopy([asset, binding]);
    if (
      !session.current(ticket) ||
      asset.locale !== binding.locale ||
      asset.text !== binding.text ||
      asset.source_version !== binding.sourceVersion ||
      asset.kind !== "synthetic_prepared_voice" ||
      !["ui_navigation", "admitted_en_measure"].includes(
        asset.release_policy,
      ) ||
      (asset.release_policy === "admitted_en_measure" && asset.locale !== "en")
    ) {
      stage = "held";
      emit();
      return false;
    }
    const ownController = new AbortController();
    controller = ownController;
    const audioSignal = AbortSignal.any([
      ownController.signal,
      AbortSignal.timeout(5000),
    ]);
    stage = "loading";
    emit();
    let timer;
    const deadline = new Promise((_, reject) => {
      timer = setTimeout(() => {
        ownController.abort();
        reject(Error("audio_timeout"));
      }, 5000);
      preparationTimer = timer;
    });
    try {
      const bytes = await Promise.race([
        (async () => {
          const response = await fetchAudio(
            "/experience/audio/" + asset.id + ".wav",
            audioSignal,
          );
          if (!response.ok) throw Error("audio_unavailable");
          return response.arrayBuffer();
        })(),
        deadline,
      ]);
      clearTimeout(timer);
      if (bytes.byteLength < 44 || bytes.byteLength > 4 * 1024 * 1024)
        throw Error("audio_bound");
      const hash = [
        ...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes)),
      ]
        .map((x) => x.toString(16).padStart(2, "0"))
        .join("");
      if (g !== generation || !session.current(ticket)) return false;
      if (hash !== asset.sha256 || bytes.byteLength !== asset.bytes)
        throw Error("audio_integrity");
      prepared = { asset, binding, bytes };
      stage = "ready";
      emit();
      return true;
    } catch {
      clearTimeout(timer);
      if (g === generation && session.current(ticket)) {
        discard();
        stage = "held";
        emit();
      }
      return false;
    }
  }
  async function play({ silent = false } = {}) {
    if (
      stage !== "ready" ||
      !prepared ||
      !session.current(prepared.binding.ticket) ||
      (!silent && !consent)
    )
      return false;
    const g = generation,
      ticket = prepared.binding.ticket;
    if (silent) {
      stage = "ready";
      emit();
      return true;
    }
    const current = prepared,
      ownURL = URL.createObjectURL(
        new Blob([current.bytes], { type: "audio/wav" }),
      ),
      ownPlayer = audioFactory();
    url = ownURL;
    player = ownPlayer;
    ownPlayer.preload = "none";
    ownPlayer.src = ownURL;
    ownPlayer.addEventListener("error", () => {
      ownPlayer.pause();
      if (g === generation && session.current(ticket)) {
        discard();
        stage = "held";
        emit();
      }
    });
    ownPlayer.addEventListener("ended", () => {
      ownPlayer.pause();
      if (g === generation && session.current(ticket)) {
        URL.revokeObjectURL(ownURL);
        url = null;
        player = null;
        stage = "ready";
        emit();
      }
    });
    // Lock before invoking asynchronous browser playback; a second click cannot
    // create a second audio queue while play() is still resolving.
    stage = "starting";
    emit();
    try {
      await ownPlayer.play();
      if (g !== generation || !session.current(ticket)) {
        ownPlayer.pause();
        return false;
      }
      stage = "playing";
      emit();
      return true;
    } catch {
      if (g === generation) {
        discard();
        stage = "held";
        emit();
      }
      return false;
    }
  }
  return {
    prepare,
    play,
    stop,
    setConsent(value) {
      consent = value === true;
      if (!consent && ["playing", "starting"].includes(stage)) stop();
      else emit();
    },
    snapshot() {
      return immutableCopy({
        stage,
        reading: prepared?.asset.text ?? "",
        consent,
      });
    },
  };
}
