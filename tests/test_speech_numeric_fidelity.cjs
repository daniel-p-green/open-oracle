'use strict';
const assert=require('node:assert/strict');
const {SpeechBuffer,words}=require('../scripts/live-ws/ws-buffer.cjs');
const {speechWords}=require('../web/live.js');
const cases=[['0.25','−0.25'],['0.25','- 0.25'],['0.25','+0.25'],['0.25','025'],['0.25','0,25'],['.25','25'],['25%','25'],['$25','25'],['25‰','25%'],['1–2','12'],['March 31, 2037','March 31, 2027']];
for(const [a,b]of cases){assert.notEqual(words(a),words(b));assert.notEqual(speechWords(a),speechWords(b));}
for(const s of [...cases.flat(),"If approved, one-quarter of one cent.","If APPROVED: one quarter of one cent!",'− 0.25','-0.25',"voter’s tax"]){assert.equal(words(s),speechWords(s));}
assert.equal(words('− 0.25'),words('-0.25'));
assert.equal(words('If approved, one-quarter of one cent.'),words('If APPROVED: one quarter of one cent!'));
function complete(expected,actual){const b=new SpeechBuffer(expected,'approved');b.event({type:'session.commentary.appended',client_event_id:'approved'});b.event({type:'session.output_transcript.delta',event_id:'t1',delta:actual});const pcm=Buffer.alloc(960);pcm.writeInt16LE(1000,200);b.event({type:'session.output_audio.delta',delta:pcm.toString('base64')});b.event({type:'session.closed',reason:'close_requested',usage:{seconds:1}});return b.finish();}
for(const [a,b]of cases)assert.equal(complete(a,b).accepted,false);
assert.equal(complete('The value is 0.25.','The value is 0.25!').accepted,true);
console.log('Numeric fidelity: 11 changed-value cases held; client/server parity and unchanged-value closure passed; synthetic PCM only, zero capture/provider/playback.');
