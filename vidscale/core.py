"""Core video upscaling functionality"""
from pathlib import Path
import subprocess
import cv2

def upscale_image(input_path: Path, output_path: Path, scale_factor: int = 2) -> None:
    """Upscale an image using bicubic interpolation"""
    img = cv2.imread(str(input_path))
    if img is None:
        raise ValueError(f"Could not read image from {input_path}")
    height, width = img.shape[:2]
    upscaled = cv2.resize(
        img,
        (width * scale_factor, height * scale_factor),
        interpolation=cv2.INTER_CUBIC
    )
    cv2.imwrite(str(output_path), upscaled)

def upscale_video(input_path: Path, output_path: Path, scale_factor: int = 2) -> None:
    """Upscale video by processing individual frames"""
    temp_dir = input_path.parent / "temp_frames"
    temp_dir.mkdir(exist_ok=True)
    # Extract frames
    subprocess.run([
        "ffmpeg", "-i", str(input_path),
        str(temp_dir / "frame_%04d.png")
    ], check=True)
    # Process frames
    for frame_path in temp_dir.glob("*.png"):
        upscale_image(frame_path, frame_path, scale_factor)
    # Rebuild video
    subprocess.run([
        "ffmpeg", "-framerate", "30", "-i", str(temp_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "slow", "-crf", "20",
        str(output_path)
    ], check=True)
