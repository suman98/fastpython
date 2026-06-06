from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
from starlette.requests import Request

from services.video_service import OUTPUT_DIR, process_video_upload

app = FastAPI(
    title="Video with Image Overlay",
    description="Overlay an image on a video for a specified time interval",
    version="1.0.0",
)

# Setup templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


@app.get("/")
def read_root():
    """Redirect to audio-video page"""
    return RedirectResponse(url="/audio-video")


@app.get("/audio-video")
def audio_video_page(request: Request):
    """Serve the audio and video overlay UI"""
    return templates.TemplateResponse(request, "audio_video.html")


@app.post("/api/create-video")
async def create_video_api(
    audioFile: UploadFile = File(...),
    images: list[UploadFile] = File(...),
    startTimes: list[str] = Form(...),
    endTimes: list[str] = Form(...),
):
    """API endpoint to create a video with multiple image overlays"""
    result = await process_video_upload(audioFile, images, startTimes, endTimes)
    return JSONResponse(result)


@app.get("/download/{filename}")
async def download_video(filename: str):
    """Download a generated video file, then delete it from the outputs folder."""
    # Guard against path traversal: only allow a bare filename inside OUTPUT_DIR.
    safe_name = Path(filename).name
    file_path = (OUTPUT_DIR / safe_name).resolve()
    if file_path.parent != OUTPUT_DIR.resolve() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Delete the file after the response has finished streaming to the client.
    def cleanup():
        try:
            file_path.unlink()
        except OSError:
            pass

    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=safe_name,
        background=BackgroundTask(cleanup),
    )


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
