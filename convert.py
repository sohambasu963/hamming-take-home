import assemblyai as aai

aai.settings.api_key = "911a9e96c7f94418813852a5b7fa9d1b"
transcriber = aai.Transcriber()


def speech_to_text(call_id):
    transcript = transcriber.transcribe(f"transcript_{call_id}.wav")
    print(transcript.text)

speech_to_text("cm37rgydi002axqrwwq0ezv2l")