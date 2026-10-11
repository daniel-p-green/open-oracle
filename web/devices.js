'use strict';
// Operator-only local check: exact selected devices, no MediaRecorder, fetch or persistence.
const deviceElement = id => document.getElementById(id);
let deviceGeneration = 0, deviceStream = null, deviceContext = null, deviceTimer = null, deviceFrame = null, deviceAttempt = false;
function deviceStatus(text) { deviceElement('device-status').textContent = text; }
function deviceSelectable() { return ['video-device','audio-device'].every(id => !!deviceElement(id).value); }
async function stopDeviceCheck(text = 'Camera and microphone are off.') {
  const generation = ++deviceGeneration; deviceAttempt = false; clearTimeout(deviceTimer); cancelAnimationFrame(deviceFrame);
  deviceStream?.getTracks().forEach(t => t.stop()); deviceStream = null;
  const context = deviceContext; deviceContext = null; if (context) { let timer; try { await Promise.race([context.close(), new Promise(resolve=>{timer=setTimeout(resolve,1500)})]); } catch {} finally {clearTimeout(timer)} }
  if (generation !== deviceGeneration) return;
  deviceElement('device-preview').srcObject = null; deviceElement('device-preview').hidden = true;
  deviceElement('device-meter').value = 0; deviceElement('device-start').disabled = !deviceSelectable(); deviceElement('device-stop').disabled = true;
  deviceStatus(text);
}
async function refreshDevices() {
  await stopDeviceCheck();
  try {
    if (!isSecureContext || !navigator.mediaDevices?.enumerateDevices) throw Error('A secure browser context is required. Use the verified localhost tunnel.');
    const devices = await navigator.mediaDevices.enumerateDevices();
    for (const [id,kind] of [['video-device','videoinput'],['audio-device','audioinput']]) {
      const select = deviceElement(id); select.replaceChildren(new Option('Select the confirmed '+(kind==='videoinput'?'camera':'microphone'),''));
      for (const device of devices.filter(d=>d.kind===kind && d.deviceId && !['default','communications'].includes(d.deviceId) && d.label)) select.add(new Option(device.label,device.deviceId));
    }
    deviceElement('device-start').disabled = !deviceSelectable();
    deviceStatus('Choose the named devices. If names are unavailable, grant this site camera/microphone access through the browser controls, then refresh. No default capture was attempted.');
  } catch (error) { deviceStatus(error.message); }
}
async function startDeviceCheck() {
  if (!deviceSelectable() || deviceAttempt || !isSecureContext || !navigator.mediaDevices?.getUserMedia) return;
  const generation = ++deviceGeneration; deviceAttempt = true;
  deviceElement('device-start').disabled = true; deviceElement('device-stop').disabled = false;
  deviceStatus('Requesting the explicitly selected devices. Stop or the 30-second limit cancels this attempt.');
  deviceTimer = setTimeout(()=>stopDeviceCheck('30-second check ended. Camera and microphone are off.'),30000);
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { deviceId: {exact:deviceElement('video-device').value},width:{ideal:1280},height:{ideal:720},frameRate:{ideal:15} }, audio:{deviceId:{exact:deviceElement('audio-device').value},echoCancellation:true} });
    if (generation !== deviceGeneration) { stream.getTracks().forEach(t=>t.stop()); return; }
    deviceStream = stream;
    const video = deviceElement('device-preview'); video.srcObject = stream; video.hidden = false;
    deviceContext = new AudioContext(); const analyser = deviceContext.createAnalyser(); analyser.fftSize = 1024;
    deviceContext.createMediaStreamSource(stream).connect(analyser); // Never connect to speakers.
    await deviceContext.resume(); if (generation !== deviceGeneration) return;
    const samples = new Float32Array(analyser.fftSize);
    const frame = () => { if (generation !== deviceGeneration) return; analyser.getFloatTimeDomainData(samples); const rms=Math.sqrt(samples.reduce((sum,v)=>sum+v*v,0)/samples.length);deviceElement('device-meter').value=Math.min(1,rms*8);deviceFrame=requestAnimationFrame(frame); }; frame();
    deviceStatus('Selected devices are acquired locally. Confirm the picture and speak to check the meter. This does not establish gesture detection or audible output.');
  } catch (error) { if (generation === deviceGeneration) await stopDeviceCheck('Device check failed: '+error.message); }
}
['video-device','audio-device'].forEach(id=>deviceElement(id).addEventListener('change',()=>stopDeviceCheck()));
deviceElement('refresh-devices').addEventListener('click',refreshDevices);
deviceElement('device-start').addEventListener('click',startDeviceCheck);
deviceElement('device-stop').addEventListener('click',()=>stopDeviceCheck());
window.addEventListener('pagehide',()=>{deviceGeneration++;clearTimeout(deviceTimer);cancelAnimationFrame(deviceFrame);deviceStream?.getTracks().forEach(t=>t.stop());deviceContext?.close().catch(()=>{});});
