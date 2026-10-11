# Frontend playback event contract

Core owner checkpoint; visual preview must preserve these fields and release checks. Changes to typography/layout do not start capture or playback.

`OpenOracleLive.notify` emits `speaking` only from the player native `onplaying` callback after the accepted buffer's display and playback-generation checks. Payload:

```js
{type:'speaking',request_id:ready.contract.request_id,validated:true,
 playing:live.player.paused === false,text:'Playing the displayed answer.'}
```

`paused`/`finished` carry the same `request_id` and `playing:false`. Generation/buffering/ready are not speaking. No fake input/output amplitude; orb remains manual volume mode. Physical audibility remains a separate supervised check.

`web/app.js` forwards:

```js
orbEvent('playback-started', {
 requestId:event.request_id, validated:event.validated === true,
 playing:event.playing === true
});
orbEvent('playback-stopped', {
 requestId:event.request_id || latest?.request_id
});
```

`orbEvent` supplies `sessionId:'visitor-'+epoch`. The real orb controller accepts start only when `requestId` equals both current and released request identities and validated/playing are true. Stop must match current request. Reset changes visitor epoch and clears released identity. The existing app response checks require `result.request_id` to match its request; display text/language must match the speech contract.

Verified offline browser fixture executes actual app forwarding and actual controller with authored Play/Stop callbacks: generation does not set Speaking, validated Play does, Stop returns Ready, reset holds old speech, consumed voice quota stays disabled. No real playback claim. Core buffered release still held on latest actual trial; further native recording/decoder diagnosis is in progress. Preserve source/Decisions/acknowledgement/transcript/final closure checks.
