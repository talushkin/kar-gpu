
from flask import Flask, request, send_file, jsonify
import os
import tempfile
from audio_utils import download_youtube_audio, separate_audio_demucs, convert_to_mp3
from gpu_worker import enqueue_job

app = Flask(__name__)

@app.route('/')
def index():
    return 'YouTube Demucs Separation Service'



@app.route('/separate', methods=['POST'])
def separate():
    data = request.get_json()
    video_id = data.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id'}), 400
    enqueue_job(video_id)
    return jsonify({'status': 'queued', 'video_id': video_id})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
