# AWS GPU Worker Installation Guide

This guide explains how to set up the kar-gpu Flask app and GPU worker on an AWS GPU instance for YouTube audio separation using Demucs.

## 1. Launch an AWS GPU Instance
- Recommended: g4dn.xlarge, g5.xlarge, or p3.2xlarge (NVIDIA GPU, CUDA support)
- OS: Ubuntu 20.04 LTS or Amazon Linux 2
- Storage: At least 50GB
- Security Group: Open TCP port 5000 for Flask API access (or restrict as needed)

## 2. Connect to Your Instance
```
ssh -i <your-key.pem> ubuntu@<instance-public-ip>
```

## 3. Install System Dependencies
```
sudo apt update && sudo apt install -y python3 python3-pip ffmpeg git
# (Optional) Install NVIDIA drivers and CUDA if not pre-installed
```

## 4. Clone the Repository
```
git clone https://github.com/talushkin/kar-gpu.git
cd kar-gpu
```

## 5. Install Python Dependencies
```
pip3 install -r requirements.txt
```

## 6. Run the Flask API (Job Submitter)
```
python3 app.py
# The API will be available at http://<instance-ip>:5000
```

## 7. Start the GPU Worker
```
python3 gpu_worker.py
```

## 8. Submit Jobs
Send a POST request to `/separate` with JSON:
```
{
  "video_id": "<YouTubeVideoID>"
}
```

## 9. Retrieve Results
- Processed files will be saved in the `results/` directory on the instance.
- You can download them via SCP or expose a download endpoint if needed.

## Notes
- For production, use a process manager (e.g., systemd, tmux, or supervisord) to keep the worker and API running.
- For cost savings, use spot instances or scale down when idle.
- Ensure your instance has a supported NVIDIA GPU and CUDA drivers.
- For troubleshooting, check logs and ensure ffmpeg, CUDA, and all Python dependencies are installed.
