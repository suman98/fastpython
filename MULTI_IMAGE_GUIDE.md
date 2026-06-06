# 🎬 Multi-Image Overlay Feature - Quick Reference

## ✅ What's New

Users can now add **multiple images** with **individual time ranges** for each image!

## 🎯 Key Changes

### UI Changes
- **Dynamic Image Rows** - Add/remove image inputs without page reload
- **"+ Add Image" Button** - Easily add more image overlays
- **Delete Buttons** - Remove unwanted images (shows when 2+ images exist)
- **Grid Layout** - Clean 4-column layout (Image | Start | End | Delete)

### Backend Changes
- **`create_video_with_multiple_images()`** - New function to handle multiple images
- **Updated API** - `/api/create-video` now accepts arrays of images/times
- **Better Validation** - Validates each image/time pair individually
- **Error Messages** - Clear messages for each image (e.g., "Image 2: Invalid time")

## 💡 How to Use

### Step 1: Open the App
```bash
python main.py
# Open http://localhost:5001
```

### Step 2: Upload Audio
Click and upload your audio file (MP3, WAV, FLAC, etc.)

### Step 3: Add Images
1. **First image**: Fill in image file, start time, end time
2. **Additional images**: Click "+ Add Image" button
3. **Remove images**: Click ✕ button (if multiple rows exist)

### Step 4: Generate
Click "Generate Video" and wait for processing

## 📝 Examples

### Example 1: Two Images in Sequence
```
Audio: presentation.mp3 (30 seconds)

Image 1: intro.png      → 0:00 - 0:10
Image 2: content.png    → 0:10 - 0:30
```

### Example 2: Three Overlays
```
Audio: speech.mp3 (60 seconds)

Image 1: title.png      → 0:00 - 0:15
Image 2: logo.png       → 0:15 - 0:45
Image 3: outro.png      → 0:45 - 1:00
```

### Example 3: Overlapping Images
```
Audio: music.mp3 (20 seconds)

Image 1: background.png → 0:00 - 0:20  (entire duration)
Image 2: watermark.png  → 0:05 - 0:15  (overlaps with Image 1)
```

## 🔧 Programmatic Usage

### Python API - Multiple Images
```python
from main import create_video_with_multiple_images

image_specs = [
    {
        "image_path": "/path/to/image1.png",
        "start_time": 0.0,
        "end_time": 5.0
    },
    {
        "image_path": "/path/to/image2.png",
        "start_time": 5.0,
        "end_time": 10.0
    },
    {
        "image_path": "/path/to/image3.png",
        "start_time": 10.0,
        "end_time": 15.0
    }
]

create_video_with_multiple_images(
    audio_path="/path/to/audio.mp3",
    image_specs=image_specs,
    output_path="output.mp4"
)
```

### API Endpoint - Multiple Images
```bash
curl -X POST http://localhost:5001/api/create-video \
  -F "audioFile=@audio.mp3" \
  -F "images=@image1.png" \
  -F "images=@image2.png" \
  -F "images=@image3.png" \
  -F "startTimes=0:00" \
  -F "startTimes=0:05" \
  -F "startTimes=0:10" \
  -F "endTimes=0:05" \
  -F "endTimes=0:10" \
  -F "endTimes=0:15"
```

## 📊 Supported Formats

**Audio**: MP3, WAV, FLAC, OGG, M4A, etc.
**Images**: PNG, JPG, JPEG, GIF, BMP, etc.
**Output**: MP4 (H.264 + AAC)

## ⏱️ Time Format

All three formats work:
- `30` (30 seconds)
- `1:30` (1 minute 30 seconds)
- `0:1:30` (0 hours, 1 minute, 30 seconds)

## 🚀 Features

- ✅ Add unlimited images
- ✅ Each image gets its own time range
- ✅ Images can overlap in time
- ✅ Drag & drop for all image rows
- ✅ Real-time validation
- ✅ Auto cleanup of temp files
- ✅ Unique numbered output files
- ✅ Works on desktop & mobile

## 📝 Files Modified

| File | Changes |
|------|---------|
| `main.py` | Added multi-image UI, new function, updated API |
| `README.md` | Updated with multi-image examples |
| `requirements.txt` | No changes needed |
| `scripts/video_with_image.py` | No changes (backward compatible) |

## 🔄 Backward Compatibility

✅ Single image still works
✅ Old `create_video()` function still works
✅ Original CLI script unchanged
✅ API can be called programmatically

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Add Image button doesn't work" | Check browser console, reload page |
| "Image validation fails" | Check image format and file size |
| "Time format error" | Use MM:SS format (e.g., 1:30 not 1.30) |
| "Video processing slow" | Normal - larger videos take time |
| "Temporary files not cleaning" | Check uploads/ directory permissions |

## 📚 Documentation Files

- `README.md` - Full documentation
- `QUICKSTART.md` - Quick setup guide
- `MULTIPLE_IMAGES.md` - Detailed implementation notes
- `IMPLEMENTATION.md` - Original implementation summary

---

**Ready to create amazing multi-image overlays!** 🎉
