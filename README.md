# Video with Image Overlay

A FastAPI web application that overlays one or multiple images onto a video for specified time intervals with audio synchronization.

## Features

- 🎬 **Web UI** - User-friendly interface to upload audio and one or multiple images with time ranges
- 🎨 **Multiple Image Overlays** - Overlay multiple images at different times in the same video
- 🔊 **Audio Sync** - Automatically syncs the image display with audio timing
- ➕ **Dynamic Image Addition** - Easily add or remove image overlays in the UI
- 📱 **Responsive Design** - Works on desktop and mobile devices
- ⚡ **Fast Processing** - Efficient video rendering using moviepy

## Getting Started

### Prerequisites

- Python 3.8 or higher
- FFmpeg (required by moviepy)

Install FFmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
choco install ffmpeg
```

### Installation

1. Clone or navigate to the project directory
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

```bash
python main.py
```

The application will start at `http://localhost:5001`

## Usage

### Web UI (Recommended)

1. Open `http://localhost:5001` in your browser
2. Upload an audio file
3. Add one or more images with time ranges:
   - **Add Image**: Click the "+ Add Image" button to add additional images
   - **Image File**: Select an image (PNG, JPG, GIF, etc.)
   - **Start Time**: When the image should appear (e.g., `0:15` or `15`)
   - **End Time**: When the image should disappear (e.g., `1:30` or `90`)
   - **Remove Image**: Click the ✕ button to remove an image row
4. Click "Generate Video"
5. Wait for processing to complete
6. Download the generated video

### Time Format

- **Seconds**: Enter plain number (e.g., `30` for 30 seconds)
- **MM:SS**: Enter in minutes:seconds format (e.g., `1:30` for 1 minute 30 seconds)
- **HH:MM:SS**: Enter in hours:minutes:seconds format (e.g., `0:1:30` for 1 minute 30 seconds)

### Example Scenarios

**Single Image Overlay:**
- Upload audio: `presentation.mp3`
- Upload image: `logo.png`
- Start: `0:00`, End: `5:00`
- Result: Logo appears for the first 5 seconds

**Multiple Image Overlays:**
- Audio: `video.mp3` (10 seconds long)
- Image 1: `intro.png` → `0:00` to `2:00`
- Image 2: `middle.png` → `3:00` to `7:00`
- Image 3: `outro.png` → `8:00` to `10:00`
- Result: Three different images at different times

### Programmatic Usage

For single image overlay:

```python
from scripts.video_with_image import create_video

create_video(
    audio_path="path/to/audio.mp3",
    image_path="path/to/image.png",
    start_time=30.0,  # seconds
    end_time=90.0,    # seconds
    output_path="output.mp4"
)
```

For multiple image overlays:

```python
from main import create_video_with_multiple_images

image_specs = [
    {
        "image_path": "path/to/image1.png",
        "start_time": 0.0,
        "end_time": 5.0
    },
    {
        "image_path": "path/to/image2.png",
        "start_time": 10.0,
        "end_time": 15.0
    }
]

create_video_with_multiple_images(
    audio_path="path/to/audio.mp3",
    image_specs=image_specs,
    output_path="output.mp4"
)
```

## Project Structure

```
.
├── main.py                      # FastAPI application with UI and API
├── scripts/
│   └── video_with_image.py      # Core video processing logic
├── requirements.txt             # Python dependencies
├── uploads/                     # Temporary upload directory
└── outputs/                     # Generated video output directory
```

## Configuration

Edit these variables in `scripts/video_with_image.py` to customize:

- `FRAME_SIZE`: Video resolution (default: 1280x720)
- `FPS`: Frames per second (default: 24)
- `BG_COLOR`: Background color RGB tuple (default: black (0,0,0))
- `OUTPUT_PATH`: Default output path

## API Endpoints

### GET `/`
Returns the main UI page

### POST `/api/create-video`
Creates a video with image overlay

**Parameters:**
- `audioFile` (file): Audio file upload
- `imageFile` (file): Image file upload
- `startTime` (string): Start time in MM:SS or seconds format
- `endTime` (string): End time in MM:SS or seconds format

**Response:**
```json
{
  "status": "success",
  "filename": "output_20240101_120000.mp4",
  "path": "/absolute/path/to/output.mp4"
}
```

### GET `/download/{filename}`
Download a generated video file

## Supported Formats

**Audio Files:**
- MP3, WAV, M4A, FLAC, OGG, and more (formats supported by ffmpeg)

**Image Files:**
- PNG, JPG, JPEG, GIF, BMP, and more

**Output:**
- MP4 (H.264 + AAC codec)

## Troubleshooting

### "Audio file not found" or "Image file not found"
- Ensure the file paths are correct
- Files should exist on the server before processing

### "Invalid time format"
- Use MM:SS (e.g., `1:30`) or seconds (e.g., `90`)
- End time must be after start time

### Video processing is slow
- This is normal for large videos
- Processing time depends on video length, resolution, and system specs
- Consider reducing FRAME_SIZE or FPS for faster processing

### "FFmpeg not found"
- Install FFmpeg on your system (see Prerequisites section)
- Verify installation: `ffmpeg -version`

## Performance Notes

- Video rendering is CPU-intensive and may take several minutes
- Processing time scales with video duration and resolution
- Temporary files are automatically cleaned up after processing

## Future Enhancements

- [ ] Batch processing
- [ ] Video trimming options
- [ ] Custom background colors/images
- [ ] Progress tracking
- [ ] Support for multiple images
- [ ] Video quality presets

## Dependencies

- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **moviepy**: Video processing
- **python-multipart**: File upload handling

## License

See LICENSE file for details.

---

Visit the [FastAPI documentation](https://fastapi.tiangolo.com/) for more information.

Or, if using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```


## Running Locally

Start the development server on http://0.0.0.0:5001

```bash
python main.py
# using uv:
uv run main.py
```

When you make changes to your project, the server will automatically reload.

## Deploying to Vercel

Deploy your project to Vercel with the following command:

```bash
npm install -g vercel
vercel --prod
```

Or `git push` to your repository with our [git integration](https://vercel.com/docs/deployments/git).

To view the source code for this template, [visit the example repository](https://github.com/vercel/vercel/tree/main/examples/fastapi).
