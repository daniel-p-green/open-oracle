/** Type contract for the runtime-validating controller; no capture or playback implementation. */
export type OrbState = 'ready' | 'listening' | 'thinking' | 'speaking' | 'uncertain';
export interface OrbSnapshot {
  readonly sessionId: string;
  readonly requestId: string | null;
  readonly releasedRequestId: string | null;
  readonly state: OrbState;
  readonly label: string;
  readonly inputLevel: number;
  readonly outputLevel: number;
}
export const AGENT_STATE: Readonly<Record<OrbState, 'listening' | 'thinking' | 'talking' | null>>;
export function createOrbController(): {
  getSnapshot(): OrbSnapshot;
  subscribe(listener: () => void): () => boolean;
  /** Unknown events are validated before updating the snapshot. */
  dispatch(event: unknown): boolean;
};
