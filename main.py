from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import shutil
from pathlib import Path
from scripts.video_with_image import create_video, parse_time
from moviepy import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip


def create_video_with_multiple_images(audio_path, image_specs, output_path=None, frame_size=(1280, 720), fps=24, bg_color=(0, 0, 0)):
    """
    Create a video with multiple image overlays on audio for specified time intervals.
    
    Args:
        audio_path: Path to audio file
        image_specs: List of dicts with keys: image_path, start_time, end_time
        output_path: Output video path
        frame_size: Frame size tuple (width, height)
        fps: Frames per second
        bg_color: Background color tuple RGB
    
    Returns:
        Path to the created video file
    """
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Load audio - its length defines the total video duration.
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Background spanning the entire audio.
    background = ColorClip(size=frame_size, color=bg_color, duration=duration)
    
    # Create image clips for each image spec
    image_clips = []
    for spec in image_specs:
        image_path = spec["image_path"]
        start_time = spec["start_time"]
        end_time = spec["end_time"]
        
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load image
        image = ImageClip(image_path)
        
        # Scale the image down if needed, keeping aspect ratio
        w, h = image.size
        fw, fh = frame_size
        if w > fw or h > fh:
            scale = min(fw / w, fh / h)
            image = image.resized(scale)
        
        # Position and timing
        image = (
            image
            .with_start(start_time)
            .with_duration(end_time - start_time)
            .with_position("center")
        )
        image_clips.append(image)
    
    # Composite all images over background
    all_clips = [background] + image_clips
    video = CompositeVideoClip(all_clips, size=frame_size)
    video = video.with_audio(audio)
    
    print(f"\nRendering {duration:.1f}s video with {len(image_specs)} image(s)...")
    video.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio_codec="aac",
    )
    
    audio.close()
    video.close()
    print(f"\nDone. Saved to: {output_path}")
    return output_path


app = FastAPI(
    title="Video with Image Overlay",
    description="Overlay an image on a video for a specified time interval",
    version="1.0.0",
)

# Create directories for uploads and outputs if they don't exist
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Serve the main UI page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Video with Image Overlay</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
            }
            
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }
            
            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }
            
            .form-group {
                margin-bottom: 25px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
                font-size: 14px;
            }
            
            .input-wrapper {
                position: relative;
            }
            
            input[type="file"],
            input[type="text"],
            input[type="number"] {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                transition: all 0.3s ease;
                font-family: inherit;
            }
            
            input[type="file"]:hover,
            input[type="text"]:hover,
            input[type="number"]:hover {
                border-color: #667eea;
            }
            
            input[type="file"]:focus,
            input[type="text"]:focus,
            input[type="number"]:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .file-input-label {
                display: block;
                padding: 12px;
                background: #f5f5f5;
                border: 2px dashed #667eea;
                border-radius: 6px;
                cursor: pointer;
                text-align: center;
                transition: all 0.3s ease;
            }
            
            .file-input-label:hover {
                background: #f0f0f0;
                border-color: #764ba2;
            }
            
            input[type="file"] {
                display: none;
            }
            
            .file-name {
                display: block;
                margin-top: 8px;
                color: #667eea;
                font-size: 13px;
                font-weight: 500;
            }
            
            .time-inputs {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }
            
            .button-group {
                display: flex;
                gap: 12px;
                margin-top: 30px;
            }
            
            button {
                flex: 1;
                padding: 14px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .btn-secondary {
                background: #f0f0f0;
                color: #333;
            }
            
            .btn-secondary:hover {
                background: #e0e0e0;
            }
            
            .btn-small {
                padding: 8px 14px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-small:hover {
                background: #764ba2;
            }
            
            .btn-remove {
                padding: 8px 12px;
                background: #ff6b6b;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-remove:hover {
                background: #ff5252;
            }
            
            .alert {
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-size: 14px;
                display: none;
            }
            
            .alert-error {
                background: #fee;
                color: #c33;
                border: 1px solid #fcc;
            }
            
            .alert-success {
                background: #efe;
                color: #3c3;
                border: 1px solid #cfc;
            }
            
            .alert-info {
                background: #eef;
                color: #33c;
                border: 1px solid #ccf;
            }
            
            .alert.show {
                display: block;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin-top: 20px;
            }
            
            .loading.show {
                display: block;
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .time-format-hint {
                font-size: 12px;
                color: #999;
                margin-top: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Video Overlay</h1>
            <p class="subtitle">Overlay an image on your video for a specified time interval</p>
            
            <div id="alert" class="alert"></div>
            
            <form id="uploadForm">
                <div class="form-group">
                    <label for="audioFile">Audio File *</label>
                    <div class="input-wrapper">
                        <label for="audioFile" class="file-input-label">
                            📁 Click to upload or drag and drop
                        </label>
                        <input type="file" id="audioFile" name="audioFile" accept="audio/*" required>
                        <span class="file-name" id="audioFileName"></span>
                    </div>
                </div>
                
                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <label>Image(s) & Time Range(s) *</label>
                        <button type="button" class="btn-small" onclick="addImageRow()">+ Add Image</button>
                    </div>
                    <div id="imageRows" style="display: flex; flex-direction: column; gap: 15px;">
                        <div class="image-row" data-row-id="0">
                            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 40px; gap: 10px; align-items: end;">
                                <div>
                                    <label style="font-size: 12px; margin-bottom: 4px;">Image File</label>
                                    <div class="file-input-label" style="padding: 8px; cursor: pointer; text-align: center;">
                                        <input type="file" class="image-file" accept="image/*" required style="display: none;">
                                        <span class="image-file-name">📁 Choose image</span>
                                    </div>
                                </div>
                                <div>
                                    <label style="font-size: 12px; margin-bottom: 4px;">Start</label>
                                    <input type="text" class="start-time" placeholder="0:00" required>
                                </div>
                                <div>
                                    <label style="font-size: 12px; margin-bottom: 4px;">End</label>
                                    <input type="text" class="end-time" placeholder="0:30" required>
                                </div>
                                <button type="button" class="btn-remove" onclick="removeImageRow(this)" style="display: none;">✕</button>
                            </div>
                            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 40px; gap: 10px;">
                                <div class="time-format-hint" style="margin: 0;">Image file</div>
                                <div class="time-format-hint" style="margin: 0;">MM:SS or seconds</div>
                                <div class="time-format-hint" style="margin: 0;">MM:SS or seconds</div>
                                <div></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="button-group">
                    <button type="button" class="btn-secondary" onclick="resetForm()">Reset</button>
                    <button type="submit" class="btn-primary" id="submitBtn">Generate Video</button>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Processing your video... This may take a few minutes.</p>
                </div>
            </form>
        </div>
        
        <script>
            let imageRowCount = 0;
            
            // Setup file input for a row
            function setupRowFileInput(row) {
                const fileInput = row.querySelector('.image-file');
                const label = row.querySelector('.file-input-label');
                const nameSpan = row.querySelector('.image-file-name');
                
                label.addEventListener('click', () => fileInput.click());
                
                fileInput.addEventListener('change', function(e) {
                    nameSpan.textContent = e.target.files[0]?.name || '📁 Choose image';
                });
                
                // Drag and drop
                ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                    label.addEventListener(eventName, (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                    });
                });
                
                ['dragenter', 'dragover'].forEach(eventName => {
                    label.addEventListener(eventName, () => {
                        label.style.borderColor = '#764ba2';
                        label.style.background = '#f0e6ff';
                    });
                });
                
                ['dragleave', 'drop'].forEach(eventName => {
                    label.addEventListener(eventName, () => {
                        label.style.borderColor = '#667eea';
                        label.style.background = 'initial';
                    });
                });
                
                label.addEventListener('drop', (e) => {
                    const dt = e.dataTransfer;
                    const files = dt.files;
                    fileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                });
            }
            
            // Add new image row
            function addImageRow() {
                imageRowCount++;
                const imageRows = document.getElementById('imageRows');
                const newRow = document.createElement('div');
                newRow.className = 'image-row';
                newRow.dataset.rowId = imageRowCount;
                newRow.innerHTML = `
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 40px; gap: 10px; align-items: end;">
                        <div>
                            <label style="font-size: 12px; margin-bottom: 4px;">Image File</label>
                            <div class="file-input-label" style="padding: 8px; cursor: pointer; text-align: center;">
                                <input type="file" class="image-file" accept="image/*" required style="display: none;">
                                <span class="image-file-name">📁 Choose image</span>
                            </div>
                        </div>
                        <div>
                            <label style="font-size: 12px; margin-bottom: 4px;">Start</label>
                            <input type="text" class="start-time" placeholder="0:00" required>
                        </div>
                        <div>
                            <label style="font-size: 12px; margin-bottom: 4px;">End</label>
                            <input type="text" class="end-time" placeholder="0:30" required>
                        </div>
                        <button type="button" class="btn-remove" onclick="removeImageRow(this)">✕</button>
                    </div>
                    <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 40px; gap: 10px;">
                        <div class="time-format-hint" style="margin: 0;">Image file</div>
                        <div class="time-format-hint" style="margin: 0;">MM:SS or seconds</div>
                        <div class="time-format-hint" style="margin: 0;">MM:SS or seconds</div>
                        <div></div>
                    </div>
                `;
                imageRows.appendChild(newRow);
                setupRowFileInput(newRow);
                updateRemoveButtons();
            }
            
            // Remove image row
            function removeImageRow(btn) {
                btn.closest('.image-row').remove();
                updateRemoveButtons();
            }
            
            // Show/hide remove buttons (always show if more than 1 row)
            function updateRemoveButtons() {
                const rows = document.querySelectorAll('.image-row');
                rows.forEach((row, idx) => {
                    const removeBtn = row.querySelector('.btn-remove');
                    removeBtn.style.display = rows.length > 1 ? 'block' : 'none';
                });
            }
            
            // Setup initial row
            document.addEventListener('DOMContentLoaded', function() {
                const initialRow = document.querySelector('.image-row');
                setupRowFileInput(initialRow);
                imageRowCount = 0;
            });
            
            // Form submission
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const audioFile = document.getElementById('audioFile').files[0];
                const imageRows = document.querySelectorAll('.image-row');
                
                if (!audioFile) {
                    showAlert('Please upload an audio file', 'error');
                    return;
                }
                
                if (imageRows.length === 0) {
                    showAlert('Please add at least one image', 'error');
                    return;
                }
                
                // Validate all rows
                for (const row of imageRows) {
                    const imageFile = row.querySelector('.image-file').files[0];
                    const startTime = row.querySelector('.start-time').value;
                    const endTime = row.querySelector('.end-time').value;
                    
                    if (!imageFile || !startTime || !endTime) {
                        showAlert('All image rows must have file and time range', 'error');
                        return;
                    }
                }
                
                const formData = new FormData();
                formData.append('audioFile', audioFile);
                
                // Add each image row
                imageRows.forEach((row, idx) => {
                    const imageFile = row.querySelector('.image-file').files[0];
                    const startTime = row.querySelector('.start-time').value;
                    const endTime = row.querySelector('.end-time').value;
                    
                    formData.append(`images`, imageFile);
                    formData.append(`startTimes`, startTime);
                    formData.append(`endTimes`, endTime);
                });
                
                document.getElementById('submitBtn').disabled = true;
                document.getElementById('loading').classList.add('show');
                
                try {
                    const response = await fetch('/api/create-video', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Error processing video');
                    }
                    
                    const data = await response.json();
                    showAlert(`✓ Video created successfully! Download: ${data.filename}`, 'success');
                    
                    // Reset form
                    setTimeout(() => resetForm(), 2000);
                } catch (error) {
                    showAlert(`✗ ${error.message}`, 'error');
                } finally {
                    document.getElementById('submitBtn').disabled = false;
                    document.getElementById('loading').classList.remove('show');
                }
            });
            
            function showAlert(message, type) {
                const alert = document.getElementById('alert');
                alert.textContent = message;
                alert.className = `alert alert-${type} show`;
                setTimeout(() => alert.classList.remove('show'), 5000);
            }
            
            function resetForm() {
                document.getElementById('uploadForm').reset();
                
                // Reset all image rows to just show the first one
                const imageRows = document.getElementById('imageRows');
                const rows = imageRows.querySelectorAll('.image-row');
                rows.forEach((row, idx) => {
                    if (idx > 0) row.remove();
                });
                
                // Reset first row
                const firstRow = imageRows.querySelector('.image-row');
                if (firstRow) {
                    firstRow.querySelector('.image-file-name').textContent = '📁 Choose image';
                    firstRow.querySelector('.start-time').value = '';
                    firstRow.querySelector('.end-time').value = '';
                }
                
                document.getElementById('alert').classList.remove('show');
                imageRowCount = 0;
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/create-video")
async def create_video_api(
    audioFile: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    startTimes: list[str] = Form(...),
    endTimes: list[str] = Form(...),
):
    """API endpoint to create a video with multiple image overlays"""
    audio_path = None
    image_paths = []
    
    try:
        # Validate arrays are same length
        if len(images) != len(startTimes) or len(images) != len(endTimes):
            raise HTTPException(status_code=400, detail="Number of images and time ranges must match")
        
        if len(images) == 0:
            raise HTTPException(status_code=400, detail="At least one image is required")
        
        # Save audio file
        audio_path = UPLOAD_DIR / audioFile.filename
        with open(audio_path, "wb") as f:
            content = await audioFile.read()
            f.write(content)
        
        # Validate audio file and get duration
        try:
            audio_clip = AudioFileClip(str(audio_path))
            audio_duration = audio_clip.duration
            audio_clip.close()
        except Exception as e:
            audio_path.unlink()
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
        
        # Process each image and time range
        image_specs = []
        
        for idx, (image_file, start_time_str, end_time_str) in enumerate(zip(images, startTimes, endTimes)):
            # Save image file
            image_path = UPLOAD_DIR / f"{idx}_{image_file.filename}"
            with open(image_path, "wb") as f:
                content = await image_file.read()
                f.write(content)
            image_paths.append(image_path)
            
            # Parse times
            try:
                start_time_sec = parse_time(start_time_str)
                end_time_sec = parse_time(end_time_str)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Image {idx+1}: Invalid time format - {str(e)}")
            
            # Validate time parameters
            if start_time_sec < 0 or end_time_sec < 0:
                raise HTTPException(status_code=400, detail=f"Image {idx+1}: Times must be non-negative")
            if end_time_sec <= start_time_sec:
                raise HTTPException(status_code=400, detail=f"Image {idx+1}: End time must be after start time")
            if start_time_sec > audio_duration:
                raise HTTPException(status_code=400, detail=f"Image {idx+1}: Start time exceeds audio duration ({audio_duration:.1f}s)")
            
            # Clamp end time to audio duration
            end_time_sec = min(end_time_sec, audio_duration)
            
            image_specs.append({
                "image_path": str(image_path),
                "start_time": start_time_sec,
                "end_time": end_time_sec
            })
        
        # Create output filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"output_{timestamp}.mp4"
        output_path = OUTPUT_DIR / output_filename
        
        # Create video with multiple images
        create_video_with_multiple_images(
            str(audio_path),
            image_specs,
            output_path=str(output_path)
        )
        
        # Clean up uploaded files
        audio_path.unlink()
        for img_path in image_paths:
            img_path.unlink()
        
        return JSONResponse({
            "status": "success",
            "filename": output_filename,
            "path": str(output_path),
            "images_count": len(image_specs)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on error
        if audio_path:
            try:
                audio_path.unlink()
            except:
                pass
        for img_path in image_paths:
            try:
                img_path.unlink()
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")


@app.get("/download/{filename}")
async def download_video(filename: str):
    """Download a generated video file"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="video/mp4", filename=filename)


@app.get("/api/data")
def get_sample_data():
    return {
        "data": [
            {"id": 1, "name": "Sample Item 1", "value": 100},
            {"id": 2, "name": "Sample Item 2", "value": 200},
            {"id": 3, "name": "Sample Item 3", "value": 300}
        ],
        "total": 3,
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
