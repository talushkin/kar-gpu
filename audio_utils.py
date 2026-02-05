import os
import subprocess
from pydub import AudioSegment
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model as get_pretrained_model
from demucs.audio import AudioFile


# Download YouTube audio as WAV
import yt_dlp as youtube_dl

def download_youtube_audio(video_id, out_path):
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return out_path

def separate_audio_demucs(wav_path, output_dir, device='cuda'):
    model = get_pretrained_model('htdemucs')
    model.to(device)
    wav, sr = sf.read(wav_path)
    if sr != 32000:
        # Resample to 32kHz
        audio = AudioSegment.from_wav(wav_path)
        audio = audio.set_frame_rate(32000)
        audio.export(wav_path, format="wav")
        wav, sr = sf.read(wav_path)
    sources = apply_model(model, torch.tensor(wav).float().unsqueeze(0).to(device), split=True, overlap=0.25)
    stems = ['drums', 'bass', 'other', 'vocals']
    os.makedirs(output_dir, exist_ok=True)
    for i, stem in enumerate(stems):
        out_file = os.path.join(output_dir, f"{stem}.wav")
        sf.write(out_file, sources[0, i].cpu().numpy(), 32000)
    # Karaoke = all but vocals
    karaoke = sum([sources[0, i] for i in range(3)])
    sf.write(os.path.join(output_dir, "karaoke.wav"), karaoke.cpu().numpy(), 32000)
    return [os.path.join(output_dir, f) for f in ["drums.wav", "bass.wav", "other.wav", "vocals.wav", "karaoke.wav"]]

def convert_to_mp3(wav_path, mp3_path):
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")
    return mp3_path
