"""Curated runtime facts, not an election-model answer or provider deletion promise."""
import re
import unicodedata

def erase_intent(text):
    value = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)).lower()
    value = re.sub(r'[.!?,¡¿]', '', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return bool(re.fullmatch(r'(?:please )?(?:erase|delete|clear) (?:this|my|the) session|(?:por favor )?(?:borra|borrar|elimina) (?:esta|mi) sesion|(?:efface|supprime) (?:cette|ma) session|losche (?:diese|meine) sitzung|(?:apague|apagar) (?:esta|minha) sessao', value))

def faq_intent(text):
    return bool(re.fullmatch(r'(?:please )?(?:explain |show |tell me )?(?:how (?:my|our|your) data is used|how (?:you|this app) use(?:s)? (?:my|our) data|privacy|data use)[?.!]*', text.strip(), re.I))
def data_use_faq(*, live=False, bedrock=False, reviewer=False, voice=False, websocket=False):
    model = ('Amazon Bedrock' if bedrock else 'OpenAI') if (live or bedrock) else None
    items = [
        {'title': 'What stays in this app?', 'text': 'The browser keeps your current question, transcript, answer and sources in temporary memory. The local server keeps bounded temporary operation records and the latest accepted answer receipt. Speech receipts are usable for three minutes; stale records are removed on later requests, erase or server restart. No visitor account or voting preference profile is created. The HTTP handler does not log questions or IP addresses.'},
        {'title': 'What is sent to a provider?', 'text': ('For this mode, your text question, election scope and retrieved official passages are sent to ' + model + ' through the local Strands agent. ' if model else 'This mode retrieves retained official documents locally, without model inference. ') + ('OpenAI Decisions receives your question, proposed answer, scope and supporting sources for fallible quality checks. ' if reviewer else 'Independent OpenAI review is off. ') + ('When you explicitly start microphone input, its audio is sent to OpenAI GPT-Live. Preparing speech sends the accepted answer text to GPT-Live; WebSocket speech sends generated silence, without acquiring a microphone. ' if voice and websocket else 'When enabled and explicitly started, GPT-Live receives microphone audio or the accepted answer for speech. ' if voice else 'Voice is off. No microphone audio is sent by this app mode.')},
        {'title': 'Which AWS services are used?', 'text': 'Strands is an SDK running on this Mac. ' + ('This configured mode uses Amazon Bedrock model inference. ' if bedrock else 'This configured mode does not use Amazon Bedrock inference. ') + 'The local app has no configured Bedrock Knowledge Base, AgentCore deployment, CloudWatch exporter or CloudTrail integration. Prior workshop account/catalog checks do not mean these services process this conversation.'},
        {'title': 'What does erase do?', 'text': 'Erase stops local microphone capture and playback, discards queued speech, clears the browser conversation and cancels this session’s remaining local work. The server drops its accepted receipt and rejects late results. In-flight provider processing may already have occurred; erase cannot unsend those requests or promise deletion by a provider. No session-linked helpfulness feedback collection is currently connected. Already-unlinked aggregate counts cannot be reversed by a session reset.'},
        {'title': 'Can I say erase at any time?', 'text': 'During active microphone recognition, you can say “erase this session.” The Erase this session control is always available. When capture is stopped, this app does not listen for speech; spoken erase during retrieval or playback is not yet supported. It does not start ambient microphone capture to recognize that command.'},
        {'title': 'What may OpenAI retain?', 'text': 'The app sets model and GPT-Live storage off. OpenAI’s published data controls list GPT-Live abuse-monitoring retention of 30 days and no application state unless storage is enabled. Storage off does not guarantee no provider retention. Account-specific Zero Data Retention settings have not been verified; local erase does not change them.'},
        {'title': 'Are recordings or conversations saved for improvement?', 'text': 'The default local application does not save raw visitor conversations, audio or video. Development proof artifacts use explicitly approved public or synthetic examples. Optional sensors run separately under their own permissions. No automatic prompt changes, feedback training, advertising, paid placement or public publication flow is connected.'}
    ]
    return {'status': 'product_faq', 'title': 'How your data is used', 'language': 'en', 'curated': True,
            'runtime': {'strands': 'local_sdk' if model else 'not_invoked', 'model_provider': model,
                        'decisions': bool(reviewer), 'voice': bool(voice), 'speech_transport': 'websocket' if websocket else 'webrtc' if voice else None},
            'items': items, 'sources': [{'title': 'OpenAI data controls', 'url': 'https://developers.openai.com/api/docs/guides/your-data'}],
            'account_retention_verified': False}
