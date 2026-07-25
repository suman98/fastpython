"""Video creation and upload-processing logic for the audio/video overlay app."""

import os
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from moviepy import AudioFileClip, ImageClip, ColorClip, CompositeVideoClip

from scripts.video_with_image import parse_time

# Directories for uploads and outputs.
# On serverless hosts (Vercel) only /tmp is writable, so the base dir is
# configurable via DATA_DIR and defaults to /tmp when running on Vercel.
_DEFAULT_BASE = "/tmp" if os.environ.get("VERCEL") else "."
BASE_DIR = Path(os.environ.get("DATA_DIR", _DEFAULT_BASE))
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


async def process_video_upload(audioFile: UploadFile, images: list[UploadFile], startTimes: list[str], endTimes: list[str]):
    """Save uploads, validate, render the overlay video, and clean up temp files.

    Returns a result dict; raises HTTPException on validation/processing errors.
    """
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

        return {
            "status": "success",
            "filename": output_filename,
            "path": str(output_path),
            "images_count": len(image_specs)
        }

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
