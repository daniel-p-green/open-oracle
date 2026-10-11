import { Component, useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from "react";
import { createRoot } from "react-dom/client";
import { Orb } from "./components/ui/orb";
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
function mount() {
  const host = document.getElementById("orb");
  if(!host) return;
  const root = createRoot(host);
  host.classList.add("orb-live");
  const event = (event:Event) => controller.dispatch((event as CustomEvent).detail);
  window.addEventListener("open-oracle:orb",event);
  root.render(<Presence host={host}/>);
  Object.assign(window,{OpenOracleOrb:{
    dispatch: controller.dispatch, getState:controller.getSnapshot,
    dispose() { window.removeEventListener("open-oracle:orb",event); root.unmount(); host.classList.remove("orb-live"); }
  }});
}
if(document.readyState === "loading") document.addEventListener("DOMContentLoaded",mount,{once:true}); else mount();

