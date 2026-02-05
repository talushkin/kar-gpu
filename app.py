
from flask import Flask, request, send_file, jsonify
import os
import tempfile
from audio_utils import download_youtube_audio, separate_audio_demucs, convert_to_mp3

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
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            wav_path = os.path.join(tmpdir, f'{video_id}.wav')
            download_youtube_audio(video_id, wav_path)
            output_dir = os.path.join(tmpdir, 'separated')
            separated = separate_audio_demucs(wav_path, output_dir, device='cuda')
            # Map stems
            stems = {
                'original': wav_path,
                'karaoke': os.path.join(output_dir, 'karaoke.wav'),
                'vocals': os.path.join(output_dir, 'vocals.wav')
            }
            mp3_files = {}
            for key, wav in stems.items():
                mp3_path = os.path.join(tmpdir, f'{key}.mp3')
                convert_to_mp3(wav, mp3_path)
                mp3_files[key] = mp3_path
            # Return as files (zip or multi-part)
            # For simplicity, return one (e.g. vocals) as demo
            return send_file(mp3_files['vocals'], mimetype='audio/mpeg', as_attachment=True, download_name='vocals.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
