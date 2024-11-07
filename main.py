import httpx
import asyncio
from flask import Flask, request, jsonify
from threading import Thread
import assemblyai as aai

aai.settings.api_key = "911a9e96c7f94418813852a5b7fa9d1b"
transcriber = aai.Transcriber()

API_TOKEN = "sk-cfbde6579b8ad510bf0b7aecf311fa93"
PHONE_NUMBER = "+12898284206"
PROMPT = "Hello, my name is Soham"
WEBHOOK_URL = "https://9263-74-15-94-178.ngrok-free.app/call"
CALL_URL = "https://app.hamming.ai/api/rest/exercise/start-call"
TRANSCRIBE_URL = "https://app.hamming.ai/api/media/exercise"



async def start_call(client, url, headers, data):
    """Initiate the call and return the call ID"""
    response = await client.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("Call started")
    return response.json()['id']


async def wait_for_recording(call_id):
    while not recording_status.get(call_id):
        print(f"Waiting for recording to be available for call ID {call_id}...")
        await asyncio.sleep(1)
    print("Recording available")


async def get_call_transcript(client, url, call_id, headers):
    """Fetch the audio file of the call and save it as a .wav file"""
    try:
        response = await client.get(f"{url}?id={call_id}", headers=headers)
        response.raise_for_status()

        if response.headers.get("Content-Type") == "audio/wav":
            file_path = f"transcript_{call_id}.wav"
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"Audio saved to {file_path}")
            return file_path
        else:
            print("Error: Unexpected Content-Type, expected audio/wav.")
            return None

    except httpx.HTTPStatusError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None


def create_conversation(file_path):
    aaiConfig = aai.TranscriptionConfig(speaker_labels=True)
    response = transcriber.transcribe(file_path, config=aaiConfig)

    conversation = {}
    for i, utterance in enumerate(response.utterances):
        node_id = str(i + 1)
        next_id = str(i + 2) if i + 1 < len(response.utterances) else None
        conversation[node_id] = {
            "speaker": f"Speaker {utterance.speaker}",
            "text": utterance.text,
            "next": [next_id] if next_id else []
        }

    return conversation



def print_conversation(conversation):
    """Print the conversation object in a readable format."""
    for _, data in conversation.items():
        print(f"{data['speaker']}: {data['text']}\n")


headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

call_data = {
    "phone_number": PHONE_NUMBER,
    "prompt": PROMPT,
    "webhook_url": WEBHOOK_URL
}

recording_status = {}




async def main():

    async with httpx.AsyncClient() as client:
        call_id = await start_call(client, CALL_URL, headers, call_data)
        print(f"Call ID: {call_id}")

        recording_status[call_id] = False
        await wait_for_recording(call_id)

        file_path = await get_call_transcript(client, TRANSCRIBE_URL, call_id, headers)
        
        conversation = create_conversation(file_path)
        print_conversation(conversation)




app = Flask(__name__)

@app.route('/call', methods=['POST'])
def webhook():
    """Handle webhook notifications and update recording status"""
    data = request.json
    call_id = data.get("id")
    recording_available = data.get("recording_available", False)

    if call_id:
        recording_status[call_id] = recording_available
        print(f"Webhook received: Call ID {call_id}, Recording Available: {recording_available}")

    return jsonify({"status": "success"}), 200



if __name__ == '__main__':
    flask_thread = Thread(target=app.run, kwargs={'port': 5000})
    flask_thread.start()

    asyncio.run(main())

    # conversation = create_conversation("transcript_cm37rr5p80023cdjryj145vnw.wav")
    # print_conversation(conversation)

