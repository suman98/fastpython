# Quick Start Guide

## 1️⃣ Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
```bash
choco install ffmpeg
```

## 2️⃣ Setup Python Environment

```bash
cd /Users/suman/Desktop/projects/fastpython
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3️⃣ Run the Application

```bash
python main.py
```

## 4️⃣ Open in Browser

Navigate to: **http://localhost:5001**

## 5️⃣ Use the UI

1. Upload an **audio file** (MP3, WAV, etc.)
2. Upload an **image file** (PNG, JPG, etc.)
3. Enter **start time** (e.g., `0:15` or `15`)
4. Enter **end time** (e.g., `1:30` or `90`)
5. Click **"Generate Video"**
6. Wait for processing...
7. Download your video! 🎬

## ⏱️ Time Format Examples

| Format | Example | Means |
|--------|---------|-------|
| Seconds | `30` | 30 seconds |
| MM:SS | `1:30` | 1 minute 30 seconds |
| HH:MM:SS | `0:1:30` | 1 minute 30 seconds |

## 📁 Project Directories

- **uploads/** - Temporary storage for uploaded files (auto-cleaned)
- **outputs/** - Generated video files

## 🐛 Common Issues

**"FFmpeg not found"**
- Install FFmpeg (see step 1)
- Run: `ffmpeg -version` to verify

**"Module not found"**
- Make sure venv is activated: `source venv/bin/activate`
- Run: `pip install -r requirements.txt`

**Slow processing**
- This is normal! Video rendering takes time
- Wait patiently or reduce video resolution

## 📝 Next Steps

- Read [README.md](README.md) for full documentation
- Check [scripts/video_with_image.py](scripts/video_with_image.py) for code details
- Customize settings in the script as needed

---

**Need help?** Check the README.md for troubleshooting and API details.
