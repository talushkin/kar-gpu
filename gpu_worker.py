import os
import time
import json
import threading
import random

QUEUE_FILE = 'job_queue.json'
RESULTS_DIR = 'results'
SLEEP_INTERVAL = 5  # seconds
MAX_RETRIES = 5

os.makedirs(RESULTS_DIR, exist_ok=True)

def exp_lin_backoff(attempt):
    return min(60, (2 ** attempt) + random.uniform(0, 2))

def enqueue_job(video_id):
    job = {'video_id': video_id, 'status': 'queued', 'retries': 0}
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'w') as f:
            json.dump([job], f)
    else:
        with open(QUEUE_FILE, 'r+') as f:
            jobs = json.load(f)
            jobs.append(job)
            f.seek(0)
            json.dump(jobs, f)
            f.truncate()

def dequeue_job():
    if not os.path.exists(QUEUE_FILE):
        return None
    with open(QUEUE_FILE, 'r+') as f:
        jobs = json.load(f)
        for job in jobs:
            if job['status'] == 'queued':
                job['status'] = 'processing'
                f.seek(0)
                json.dump(jobs, f)
                f.truncate()
                return job
    return None

def mark_job_done(video_id, result_path):
    with open(QUEUE_FILE, 'r+') as f:
        jobs = json.load(f)
        for job in jobs:
            if job['video_id'] == video_id:
                job['status'] = 'done'
                job['result'] = result_path
        f.seek(0)
        json.dump(jobs, f)
        f.truncate()

def worker_loop():
    from audio_utils import download_youtube_audio, separate_audio_demucs, convert_to_mp3
    while True:
        job = dequeue_job()
        if not job:
            time.sleep(SLEEP_INTERVAL)
            continue
        video_id = job['video_id']
        attempt = job.get('retries', 0)
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                wav_path = os.path.join(tmpdir, f'{video_id}.wav')
                download_youtube_audio(video_id, wav_path)
                output_dir = os.path.join(tmpdir, 'separated')
                separate_audio_demucs(wav_path, output_dir, device='cuda')
                vocals_mp3 = os.path.join(tmpdir, 'vocals.mp3')
                convert_to_mp3(os.path.join(output_dir, 'vocals.wav'), vocals_mp3)
                result_path = os.path.join(RESULTS_DIR, f'{video_id}_vocals.mp3')
                os.rename(vocals_mp3, result_path)
                mark_job_done(video_id, result_path)
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(exp_lin_backoff(attempt))
                job['retries'] = attempt + 1
                job['status'] = 'queued'
                with open(QUEUE_FILE, 'r+') as f:
                    jobs = json.load(f)
                    for j in jobs:
                        if j['video_id'] == video_id:
                            j.update(job)
                    f.seek(0)
                    json.dump(jobs, f)
                    f.truncate()
            else:
                print(f"Job {video_id} failed after {MAX_RETRIES} retries: {e}")
        time.sleep(1)

if __name__ == '__main__':
    t = threading.Thread(target=worker_loop)
    t.start()
    t.join()
