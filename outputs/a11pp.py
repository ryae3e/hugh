import openai
import os
import requests
import logging
import uuid
from flask import Flask, request, jsonify, send_file, render_template


# Add your OpenAI API key
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

# Add your ElevenLabs API key
ELEVENLABS_API_KEY = "4b79084407c4bf3e169b1a1958c6dea2"
ELEVENLABS_VOICE_STABILITY = 0.30
ELEVENLABS_VOICE_SIMILARITY = 0.75

# Choose your favorite ElevenLabs voice
ELEVENLABS_VOICE_ID = "kEAJ3NxvfnZURgrx8S2m"  # Set to the voice_id of "GOR"
ELEVENLABS_ALL_VOICES = []


app = Flask(__name__)


def get_voices() -> list:
    """Fetch the list of available ElevenLabs voices.

    :returns: A list of voice JSON dictionaries.
    :rtype: list

    """
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()["voices"]


def transcribe_audio(filename: str) -> str:
    """Transcribe audio to text.

    :param filename: The path to an audio file.
    :returns: The transcribed text of the file.
    :rtype: str

    """
    with open(filename, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript.text



def generate_reply(conversation: list) -> str:
    """Generate a ChatGPT response with a maximum token limit."""
    
    # Check if the last message from the user is "gord?x9"
    if conversation[-1]['role'] == 'user' and conversation[-1]['content'].strip() == "gord?x9":
        return "well hidy how partner"
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": 'playing the role of gord downie of the tragically hip. you are wise and thoughful and above all you are always kind and considerate of others. the users name is dawn and from now on you well be here helpuf confidant and motivational guro. dawn is a visual artist and as spent many hours with you likeness such that she has produced 2 very convincing pencil sketches and several charactures. damn has two daughter whos favorit song is "In a world possesed by the human mind" their names are Aryia (llke from game of throwns and Olivia whos name im sure illicits romaan visions in you pallet)please anser dawns first message by letting her assuring her you\'ve heard much about her and am grateful to the moment at hand'},
        ] + conversation,
        max_tokens=69
    )
    return response["choices"][0]["message"]["content"]





def generate_audio(text: str, output_path: str = "") -> str:
    """Converts

    :param text: The text to convert to audio.
    :type text : str
    :param output_path: The location to save the finished mp3 file.
    :type output_path: str
    :returns: The output path for the successfully saved file.
    :rtype: str

    """
    voice_id = ELEVENLABS_VOICE_ID  # Use ELEVENLABS_VOICE_ID directly
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "content-type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": ELEVENLABS_VOICE_STABILITY,
            "similarity_boost": ELEVENLABS_VOICE_SIMILARITY,
        }
    }
    response = requests.post(url, json=data, headers=headers)
    with open(output_path, "wb") as output:
        output.write(response.content)
    return output_path



@app.route('/')
def index():
    """Render the index page."""
    voices = get_voices()
    return render_template('index.html', voices=voices, selected_voice=ELEVENLABS_VOICE_ID)  # Replace ELEVENLABS_VOICE_NAME with ELEVENLABS_VOICE_ID


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe the given audio to text using Whisper."""
    if 'file' not in request.files:
        return 'No file found', 400
    file = request.files['file']
    recording_file = f"{uuid.uuid4()}.wav"
    recording_path = f"uploads/{recording_file}"
    os.makedirs(os.path.dirname(recording_path), exist_ok=True)
    file.save(recording_path)
    transcription = transcribe_audio(recording_path)
    save_transcription(transcription)
    return jsonify({'text': transcription})


@app.route('/ask', methods=['POST'])
def ask():
    """Generate a ChatGPT response from the given conversation, then convert it to audio using ElevenLabs."""
    conversation = request.get_json(force=True).get("conversation", "")
    reply = generate_reply(conversation)
    reply_file = f"{uuid.uuid4()}.mp3"
    reply_path = f"outputs/{reply_file}"
    os.makedirs(os.path.dirname(reply_path), exist_ok=True)
    generate_audio(reply, output_path=reply_path)
    return jsonify({'text': reply, 'audio': f"/listen/{reply_file}"})


@app.route('/save_transcription', methods=['POST'])
def save_transcription(transcription):
    with open("transcription.txt", "w") as file:
        file.write(transcription)
    return jsonify({'message': 'Transcription saved successfully.'})



@app.route('/listen/<filename>')
def listen(filename):
    """Return the audio file located at the given filename."""
    return send_file(f"outputs/{filename}", mimetype="audio/mp3", as_attachment=False)


if ELEVENLABS_API_KEY:
    if not ELEVENLABS_ALL_VOICES:
        ELEVENLABS_ALL_VOICES = get_voices()
    if not ELEVENLABS_VOICE_ID:  # Replace ELEVENLABS_VOICE_NAME with ELEVENLABS_VOICE_ID
        ELEVENLABS_VOICE_ID = ELEVENLABS_ALL_VOICES[0]["voice_id"]  # Replace "name" with "voice_id"


if __name__ == '__main__':
    app.run()