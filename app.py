from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
import io
import wave
import ffmpeg
import os

app = Flask(__name__)
CORS(app)

def convert_webm_to_wav(webm_file):
    input_file = 'input.webm'
    output_file = 'output.wav'
    
    with open(input_file, 'wb') as f:
        f.write(webm_file.read())
    
    ffmpeg.input(input_file).output(output_file).run()
    os.remove(input_file)  # Clean up input file
    
    with open(output_file, 'rb') as f:
        wav_data = f.read()
    
    os.remove(output_file)  # Clean up output file
    return wav_data

@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file uploaded'}), 400

    audio_file = request.files['audio']
    
    try:
        # Convert WebM to WAV
        wav_data = convert_webm_to_wav(audio_file)
        
        # Process the WAV data
        audio_file = io.BytesIO(wav_data)
        recognizer = sr.Recognizer()
        audio_data = sr.AudioFile(audio_file)
        with audio_data as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Failed to process audio: {e}'}), 400

if __name__ == '__main__':
    app.run(debug=True)
