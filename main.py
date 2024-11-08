import httpx
import asyncio
from flask import Flask, request, jsonify
from threading import Thread
import assemblyai as aai
from dotenv import load_dotenv
import os
from prompts import CALL_PROMPT_ONE, CALL_PROMPT_TWO, CALL_PROMPT_THREE, MERGE_CONVERSATIONS_PROMPT
from response import conversation_response_format
from openai import OpenAI
import json

load_dotenv()


aai.settings.api_key = os.getenv("ASSEMBLY_API_KEY")
transcriber = aai.Transcriber()

API_TOKEN = os.getenv("HAMMING_API_KEY")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
WEBHOOK_URL = "https://9263-74-15-94-178.ngrok-free.app/call"
CALL_URL = "https://app.hamming.ai/api/rest/exercise/start-call"
TRANSCRIBE_URL = "https://app.hamming.ai/api/media/exercise"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

recording_status = {}
conversations = []


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


async def start_call(client, url, headers, data):
    """Initiate the call and return the call ID"""
    response = await client.post(url, headers=headers, json=data)
    response.raise_for_status()
    print("Call started")
    return response.json()['id']


async def wait_for_recording(call_id):
    """Wait until the recording is available"""
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
    """Process transcript and create a string with highlighted speakers"""
    aaiConfig = aai.TranscriptionConfig(speaker_labels=True)
    response = transcriber.transcribe(file_path, config=aaiConfig)

    text = ""
    for utterance in response.utterances:
        text += f"Speaker {utterance.speaker}: {utterance.text}\n"

    return text

    # conversation = {}
    # for i, utterance in enumerate(response.utterances):
    #     node_id = str(i + 1)
    #     next_id = str(i + 2) if i + 1 < len(response.utterances) else None
    #     conversation[node_id] = {
    #         "speaker": f"Speaker {utterance.speaker}",
    #         "text": utterance.text,
    #         "next": [next_id] if next_id else []
    #     }

    # return conversation

async def handle_conversation(prompt_text, client):
    """Handle a single conversation and return the conversation object"""

    call_data = {
        "phone_number": PHONE_NUMBER,
        "prompt": prompt_text,
        "webhook_url": WEBHOOK_URL
    }
    call_id = await start_call(client, CALL_URL, headers, call_data)
    print(f"Call ID: {call_id}")


    recording_status[call_id] = False
    await wait_for_recording(call_id)


    file_path = await get_call_transcript(client, TRANSCRIBE_URL, call_id, headers)
    if file_path:
        conversation = create_conversation(file_path)
        conversations.append(conversation)
        print(conversation)
        print("Conversation added to conversation objects.")


def merge_conversations(conversations):
    """Merge multiple conversation objects into a single structure"""

    formatted_prompt = MERGE_CONVERSATIONS_PROMPT.format(
        transcript_one=conversations[0],
        transcript_two=conversations[1],
        transcript_three=conversations[2]
    )


    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": "..."}
        ],
        response_format=conversation_response_format,
    )

    return completion.choices[0].message.content


async def main():
    async with httpx.AsyncClient() as client:
        # Process each prompt sequentially and store each as a unique conversation object
        await handle_conversation(CALL_PROMPT_ONE, client)
        await handle_conversation(CALL_PROMPT_TWO, client)
        await handle_conversation(CALL_PROMPT_THREE, client)

        # sample_conversations = [
        #     # Conversation 1
        #     """Speaker B: Hello.
        # Speaker A: Hello. I'm having an issue with my Costco membership card. Can you help me?
        # Speaker B: Sure.
        # Speaker A: Great. Thank you. Could you please let me know what information you need from me to get started?
        # Speaker B: Yes. When was the last time you tried using the card?
        # Speaker A: I tried using it last week, but it didn't work. Could you guide me on what I should do next?
        # Speaker B: How long have you been using the card for?
        # Speaker A: I've been a member for about a month now.
        # Speaker B: Are you a new member or a longtime member?
        # Speaker A: I'm a new member.""",

        #     # Conversation 2
        #     """Speaker B: Hello.
        # Speaker A: Hello. I'm having an issue with my Costco membership card. Can you help me?
        # Speaker B: Absolutely, I'd be happy to help.
        # Speaker A: Thank you! What information do you need from me to begin?
        # Speaker B: When was the last time you attempted to use the card?
        # Speaker A: I'm not sure. Could you let me know what I should do next?
        # Speaker B: How long have you had the card?
        # Speaker A: Just a couple of weeks. This issue happened when I first tried to use it.
        # Speaker B: Are you new to Costco, or have you been a member for a while?
        # Speaker A: I'm new.""",

        #     # Conversation 3
        #     """Speaker B: Hello.
        # Speaker A: Hi, I'm having trouble with my Costco membership card. Could you help me with this?
        # Speaker B: Of course. Let's see what we can do to assist.
        # Speaker A: Thank you. Could you tell me what information you need to get started?
        # Speaker B: When was the last time you used your card?
        # Speaker A: I actually haven’t used it yet; I just received it recently.
        # Speaker B: Got it. How long have you had your membership?
        # Speaker A: Only a couple of days. I just joined.
        # Speaker B: I see. Are you a new member or have you been with Costco for some time?
        # Speaker A: I'm a brand new member.""",
        # ]


        
        merged_conversation = merge_conversations(conversations)
        print(merged_conversation)



if __name__ == '__main__':
    flask_thread = Thread(target=app.run, kwargs={'port': 5000})
    flask_thread.start()

    asyncio.run(main())
