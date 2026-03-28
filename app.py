from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# Render backend se automatically tumhari key le lega
ASSEMBLY_AI_KEY = os.environ.get("ASSEMBLY_AI_KEY") 

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    language = request.form.get('language', 'auto') # Frontend se aayi language
    
    headers = {'authorization': ASSEMBLY_AI_KEY}
    
    # 1. Upload Video
    upload_response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, data=file.read())
    audio_url = upload_response.json().get('upload_url')
    
    # 2. Transcription Start Command with Language Support
    json_data = {'audio_url': audio_url, 'speech_models': ["universal-2"]}
    
    if language == 'auto':
        json_data['language_detection'] = True
    elif language == 'hinglish':
        json_data['language_code'] = 'hi'
    else:
        json_data['language_code'] = language
        
    transcript_response = requests.post('https://api.assemblyai.com/v2/transcript', json=json_data, headers=headers)
    
    return jsonify(transcript_response.json())

# 3. YAHAN NAYA ROUTE ADD KIYA HAI STATUS CHECK KARNE KE LIYE
@app.route('/status/<transcript_id>', methods=['GET'])
def get_status(transcript_id):
    headers = {'authorization': ASSEMBLY_AI_KEY}
    response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
