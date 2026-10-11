'use strict';
// Pure bounded PCM/transcript gate. No network, microphone, or playback here.
const words=value=>String(value).normalize('NFKC').toLowerCase().replace(/[’‘]/g,"'").replace(/[^\p{L}\p{N}']/gu,' ').replace(/\s+/g,' ').trim();
class SpeechBuffer{
 constructor(text,commentaryId){if(typeof text!=='string'||!text||text.length>1800)throw Error('Invalid approved text');this.text=text;this.commentaryId=commentaryId;this.transcript='';this.chunks=[];this.bytes=0;this.ids=new Set();this.invalid=false;this.ack=false;this.closed=null;}
 event(e){if(!e||typeof e.type!=='string'){this.invalid=true;return;}if(e.type==='error'||e.type==='session.delegation.created')this.invalid=true;
  if(e.type==='session.commentary.appended'&&e.client_event_id===this.commentaryId)this.ack=true;
  if(['session.output_audio.delta','session.output_transcript.delta'].includes(e.type)){
   // Primary WS audio chunks are ordered by transport and need not have event_id.
   if((e.type==='session.output_transcript.delta'&&typeof e.event_id!=='string')||(e.event_id!==undefined&&(typeof e.event_id!=='string'||this.ids.has(e.event_id)))||typeof e.delta!=='string'){this.invalid=true;return;}
   if(e.event_id!==undefined)this.ids.add(e.event_id);if(this.ids.size>6000||this.chunks.length>6000){this.invalid=true;return;}
   if(e.type==='session.output_transcript.delta'){this.transcript+=e.delta;if(this.transcript.length>2400)this.invalid=true;}
   else{if(!/^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$/.test(e.delta)){this.invalid=true;return;}const b=Buffer.from(e.delta,'base64');if(b.length%2||this.bytes+b.length>4320000){this.invalid=true;return;}this.bytes+=b.length;this.chunks.push(b);}
  }
  if(e.type==='session.closed')this.closed={reason:e.reason,usage:e.usage};
 }
 finish(){const report={acknowledged:this.ack,transcript_matches:words(this.transcript)===words(this.text),invalid_output:this.invalid,final_usage_confirmed:Number.isFinite(this.closed?.usage?.seconds)&&this.closed.usage.seconds>=0,close_reason:this.closed?.reason??null,buffered_bytes:this.bytes};
  if(!report.acknowledged||!report.transcript_matches||report.invalid_output||!report.final_usage_confirmed||report.close_reason!=='close_requested'||!this.bytes)return{accepted:false,report};
  const pcm=Buffer.concat(this.chunks);let first=0,last=pcm.length/2-1,peak=0,sum=0;for(let i=0;i<pcm.length;i+=2){const v=pcm.readInt16LE(i)/32768;peak=Math.max(peak,Math.abs(v));sum+=v*v;}
  report.peak=peak;report.rms=Math.sqrt(sum/(pcm.length/2));if(peak<.0005)return{accepted:false,report:{...report,silent:true}};
  while(first<last&&Math.abs(pcm.readInt16LE(first*2))<17)first++;while(last>first&&Math.abs(pcm.readInt16LE(last*2))<17)last--;
  first=Math.max(0,first-3600);last=Math.min(pcm.length/2-1,last+3600);const audio=pcm.subarray(first*2,(last+1)*2),wav=Buffer.alloc(44+audio.length);
  wav.write('RIFF',0);wav.writeUInt32LE(36+audio.length,4);wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);wav.writeUInt32LE(24000,24);wav.writeUInt32LE(48000,28);wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);wav.write('data',36);wav.writeUInt32LE(audio.length,40);audio.copy(wav,44);
  return{accepted:true,transcript:this.transcript,wav,report:{...report,duration_ms:Math.round(audio.length/48),trimmed_silence_ms:Math.round((pcm.length-audio.length)/48)}};
 }
 clear(){this.chunks=[];this.bytes=0;this.transcript='';this.ids.clear();this.invalid=true;}
}
module.exports={SpeechBuffer,words};
