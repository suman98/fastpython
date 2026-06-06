"""
Overlay an image onto a video for a given time interval, synced with audio.

Given an audio file, this builds a video the length of the audio and shows
the chosen image between the start and end times you enter.

Requires moviepy 2.x:  pip install moviepy
(See the note at the bottom for moviepy 1.x method names.)
"""

import os
from moviepy import (
    AudioFileClip,
    ImageClip,
    ColorClip,
    CompositeVideoClip,
)

# The audio file path is "given" - change this to your file.
AUDIO_PATH = "/Users/suman/Downloads/pte_essay_problem_solving.mp3"

# Output video settings
OUTPUT_PATH = "output.mp4"
FRAME_SIZE = (1280, 720)   # (width, height)
FPS = 24
BG_COLOR = (0, 0, 0)       # black background


def parse_time(time_str):
    """Parse a time string into seconds.

    Accepts plain seconds ('12.5'), 'MM:SS', or 'HH:MM:SS'.
    """
    time_str = time_str.strip()
    if ":" in time_str:
        seconds = 0.0
        for part in time_str.split(":"):
            seconds = seconds * 60 + float(part)
        return seconds
    return float(time_str)


def prompt_inputs(audio_duration):
    """Prompt for start time, end time, and image path; validate them."""
    while True:
        try:
            start = parse_time(input("Enter start time (s or MM:SS): "))
            end = parse_time(input("Enter end time (s or MM:SS): "))
        except ValueError:
            print("  Could not read those times. Try again.\n")
            continue

        if start < 0 or end < 0:
            print("  Times must be non-negative. Try again.\n")
        elif end <= start:
            print("  End time must be after start time. Try again.\n")
        elif start > audio_duration:
            print(f"  Start is past the audio length ({audio_duration:.1f}s). "
                  "Try again.\n")
        else:
            # Clamp the end to the audio length if it runs over.
            end = min(end, audio_duration)
            break

    while True:
        image_path = input("Enter image file path: ").strip().strip('"')
        if os.path.isfile(image_path):
            return start, end, image_path
        print("  That image file doesn't exist. Try again.\n")


def create_video(audio_path, image_path, start_time, end_time, output_path=None, frame_size=None, fps=None, bg_color=None):
    """
    Create a video with an image overlaid on audio for a specified time interval.
    
    Args:
        audio_path: Path to audio file
        image_path: Path to image file
        start_time: Start time in seconds
        end_time: End time in seconds
        output_path: Output video path (default: OUTPUT_PATH)
        frame_size: Frame size tuple (width, height) (default: FRAME_SIZE)
        fps: Frames per second (default: FPS)
        bg_color: Background color tuple RGB (default: BG_COLOR)
    
    Returns:
        Path to the created video file
    
    Raises:
        FileNotFoundError: If audio or image files don't exist
        ValueError: If time parameters are invalid
    """
    # Use defaults if not provided
    out_path = output_path or OUTPUT_PATH
    frame = frame_size or FRAME_SIZE
    fps_val = fps or FPS
    bg = bg_color or BG_COLOR
    
    # Validate files exist
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Load audio - its length defines the total video duration.
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Validate times
    if start_time < 0 or end_time < 0:
        raise ValueError("Times must be non-negative")
    if end_time <= start_time:
        raise ValueError("End time must be after start time")
    if start_time > duration:
        raise ValueError(f"Start time {start_time} is past audio length {duration}")
    
    # Clamp end to audio duration
    end_time = min(end_time, duration)

    # Background spanning the entire audio.
    background = ColorClip(size=frame, color=bg, duration=duration)

    # Image clip shown only during [start_time, end_time].
    image = ImageClip(image_path)

    # Scale the image down if it's wider/taller than the frame, keeping aspect.
    w, h = image.size
    fw, fh = frame
    if w > fw or h > fh:
        scale = min(fw / w, fh / h)
        image = image.resized(scale)

    image = (
        image
        .with_start(start_time)
        .with_duration(end_time - start_time)
        .with_position("center")
    )

    # Composite the image over the background, then attach the audio.
    video = CompositeVideoClip([background, image], size=frame)
    video = video.with_audio(audio)

    print(f"\nRendering {duration:.1f}s video, image visible "
          f"{start_time:.1f}s -> {end_time:.1f}s ...")
    video.write_videofile(
        out_path,
        fps=fps_val,
        codec="libx264",
        audio_codec="aac",
    )

    audio.close()
    video.close()
    print(f"\nDone. Saved to: {out_path}")
    return out_path


def main():
    if not os.path.isfile(AUDIO_PATH):
        print(f"Audio file not found: {AUDIO_PATH}")
        print("Set AUDIO_PATH at the top of the script to your audio file.")
        return

    audio = AudioFileClip(AUDIO_PATH)
    audio_duration = audio.duration
    audio.close()
    print(f"Audio length: {audio_duration:.1f} seconds\n")

    start, end, image_path = prompt_inputs(audio_duration)
    create_video(AUDIO_PATH, image_path, start, end)


if __name__ == "__main__":
    main()


# -----------------------------------------------------------------------------
# moviepy 1.x note:
# If you're on moviepy < 2.0, rename the methods:
#   .with_start(...)    -> .set_start(...)
#   .with_duration(...) -> .set_duration(...)
#   .with_position(...) -> .set_position(...)
#   .with_audio(...)    -> .set_audio(...)
#   .resized(scale)     -> .resize(scale)
# and import via: from moviepy.editor import (...)
# -----------------------------------------------------------------------------