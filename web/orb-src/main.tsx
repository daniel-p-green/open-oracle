import { Component, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { Orb } from "./components/ui/orb";
import { LiveWaveform } from "./components/ui/live-waveform";
import { ShimmeringText } from "./components/ui/shimmering-text";
import { createOrbController, AGENT_STATE } from "./controller.mjs";
const controller = createOrbController();
const colors: Record<string, [string,string]> = {
  ready: ["#C9A545","#F4E6B4"], listening: ["#3F7D60","#C4DDB4"],
  thinking: ["#B07F2C","#F1D99A"], speaking: ["#285846","#A6CFB0"], uncertain: ["#8F8672","#DAD4C4"]
};
class Boundary extends Component<{children: ReactNode}, {failed:boolean}> {
  state = {failed:false};
  static getDerivedStateFromError() { return {failed:true}; }
  render() { return this.state.failed ? <span className="orb-static" aria-hidden="true" /> : this.props.children; }
}
function Presence({host}: {host:HTMLElement}) {
  const state = useSyncExternalStore(controller.subscribe, controller.getSnapshot);
  const stateRef = useRef(state);
  stateRef.current = state;
  const [calm,setCalm] = useState(matchMedia("(prefers-reduced-motion: reduce)").matches);
  const [available,setAvailable] = useState(false);
  useEffect(() => {
    const media = matchMedia("(prefers-reduced-motion: reduce)");
    const change = () => setCalm(media.matches);
    media.addEventListener("change",change);
    // Probe a separate, immediately released context. Never request camera/microphone.
    const probe = document.createElement("canvas").getContext("webgl2");
    setAvailable(Boolean(probe));
    probe?.getExtension("WEBGL_lose_context")?.loseContext();
    return () => media.removeEventListener("change",change);
  },[]);
  useEffect(() => {
    host.dataset.state = state.state;
    const label = document.getElementById("presence-state");
    if(label) label.textContent = state.label;
    const gap = document.getElementById("orb-uncertainty");
    if(gap) gap.hidden = state.state !== "uncertain";
  },[host,state]);
  return <div className="orb-island" data-state={state.state}>
    {available && !calm ? <Boundary><Orb colors={colors[state.state]} seed={2026}
      agentState={AGENT_STATE[state.state]} volumeMode="manual"
      getInputVolume={() => stateRef.current.inputLevel}
      getOutputVolume={() => stateRef.current.outputLevel}
      noiseTextureUrl="/orb-noise.png" pixelRatio={1} /></Boundary>
      : <span className="orb-static" aria-hidden="true" />}
  </div>;
}

// app.js is a classic script: its top-level `live` and `latest` bindings are readable
// here by name. Read-only. Nothing in this island starts capture, playback or a request.
declare const live: { stream?: MediaStream | null } | undefined;
declare const latest: { request_id?: string; triage?: Triage } | null | undefined;
type Triage = { status?: string; intent?: string; engine_invoked?: boolean; route?: string; multiple_parts?: boolean; view?: { choice?: string; applied?: boolean } };
const appStream = () => {
  try {
    const stream = live?.stream;
    return stream instanceof MediaStream && stream.getAudioTracks().some(t => t.enabled && t.readyState === "live") ? stream : null;
  } catch { return null; }
};
const appTriage = (requestId: string | null) => {
  try { return latest && latest.request_id === requestId && latest.triage ? latest.triage : null; } catch { return null; }
};
function useCalm() {
  const [calm,setCalm] = useState(matchMedia("(prefers-reduced-motion: reduce)").matches);
  useEffect(() => {
    const media = matchMedia("(prefers-reduced-motion: reduce)");
    const change = () => setCalm(media.matches);
    media.addEventListener("change",change);
    return () => media.removeEventListener("change",change);
  },[]);
  return calm;
}
// ElevenLabs UI LiveWaveform and ShimmeringText beside the Orb. The waveform shows the
// real level of the microphone stream the app already opened; the shimmer repeats the
// app's own status text while it works. Neither invents activity.
function Voice() {
  const state = useSyncExternalStore(controller.subscribe, controller.getSnapshot);
  const calm = useCalm();
  const [stream,setStream] = useState<MediaStream|null>(null);
  const [label,setLabel] = useState("");
  useEffect(() => { setStream(state.state === "listening" ? appStream() : null); },[state]);
  useEffect(() => {
    const node = document.getElementById("presence-state");
    if(!node) return;
    const read = () => setLabel(node.textContent || "");
    read();
    const observer = new MutationObserver(read);
    observer.observe(node,{childList:true,characterData:true,subtree:true});
    return () => observer.disconnect();
  },[]);
  const shimmer = state.state === "thinking" && !calm && Boolean(label);
  useEffect(() => {
    const node = document.getElementById("presence-state");
    node?.classList.toggle("oo-visually-hidden",shimmer);
    return () => node?.classList.remove("oo-visually-hidden");
  },[shimmer]);
  return <>
    {shimmer && <span aria-hidden="true"><ShimmeringText text={label} className="oo-shimmer" startOnView={false} duration={1.6} color="#5b6472" shimmerColor="#002664" /></span>}
    {stream && !calm && <LiveWaveform active stream={stream} mode="static" height={40} barWidth={4} barGap={2} barColor="#002664" fadeEdges={false} className="oo-wave" aria-label="Microphone level" />}
  </>;
}
const INTENT: Record<string,string> = {
  measure_explanation: "ballot measure wording", candidate_comparison: "candidate statements", candidate_roster: "who is on the ballot",
  retention: "judicial retention", logistics: "voting logistics", vote_advice: "a request for voting advice", prediction: "a request for a prediction",
  personal_ballot: "a personal ballot question", privacy: "data use", off_topic: "outside this election"
};
const VIEW: Record<string,string> = {
  measure_parts: "every part in order", measure_decision: "what YES and NO mean", measure_rate: "the printed rate",
  measure_time: "how long it lasts", measure_purpose: "the stated purpose", measure_fund: "where the money goes"
};
// Fixed application wording chosen from closed lists. No model text is displayed.
function routeText(triage: Triage | null) {
  if(!triage || triage.status === "skipped") return "";
  if(triage.status !== "classified" || !triage.intent || !INTENT[triage.intent]) return "Automated sorting was unavailable, so the ordinary path ran.";
  const parts = ["An automated check sorted this question as " + INTENT[triage.intent] + "."];
  if(triage.engine_invoked === false) parts.push("It was answered with a fixed response. The research agent was not run.");
  if(triage.view?.applied && triage.view.choice && VIEW[triage.view.choice]) parts.push("The view opens on " + VIEW[triage.view.choice] + ".");
  if(triage.multiple_parts) parts.push("This looks like more than one question. Ask one part at a time if something is missing.");
  parts.push("Automated sorting can be wrong.");
  return parts.join(" ");
}
function Route() {
  const state = useSyncExternalStore(controller.subscribe, controller.getSnapshot);
  const text = state.state === "thinking" || state.state === "listening" ? "" : routeText(appTriage(state.requestId));
  return text ? <p className="fine oo-route" data-route="decisions">{text}</p> : null;
}
function mount() {
  const host = document.getElementById("orb");
  if(!host) return;
  const root = createRoot(host);
  host.classList.add("orb-live");
  const event = (event:Event) => controller.dispatch((event as CustomEvent).detail);
  window.addEventListener("open-oracle:orb",event);
  root.render(<Presence host={host}/>);
  const extras: Array<{unmount():void}> = [], added: HTMLElement[] = [];
  const beside = document.createElement("span");
  beside.id = "orb-voice"; beside.className = "orb-voice";
  host.parentElement?.append(beside);
  const heading = document.querySelector("#answer-region .answer-heading");
  const route = document.createElement("div");
  route.id = "orb-route";
  heading?.after(route);
  for(const [node,view] of [[beside,<Voice/>],[route,<Route/>]] as const) {
    if(!node.isConnected) continue;
    const extra = createRoot(node); extra.render(<Boundary>{view}</Boundary>); extras.push(extra); added.push(node);
  }
  Object.assign(window,{OpenOracleOrb:{
    dispatch: controller.dispatch, getState:controller.getSnapshot,
    dispose() { window.removeEventListener("open-oracle:orb",event); root.unmount(); extras.forEach(extra => extra.unmount()); added.forEach(node => node.remove()); host.classList.remove("orb-live"); }
  }});
}
if(document.readyState === "loading") document.addEventListener("DOMContentLoaded",mount,{once:true}); else mount();

