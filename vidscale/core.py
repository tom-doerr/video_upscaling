"""Core video upscaling functionality"""

from pathlib import Path
import subprocess
import shutil
import cv2  # pylint: disable=import-error


def upscale_image(
    input_path: Path, output_path: Path, scale_factor: int = 2
) -> None:  # pylint: disable=too-many-arguments
    """Upscale an image using bicubic interpolation.

    Args:
        input_path: Path to source image
        output_path: Path to save upscaled image
        scale_factor: Multiplier for image dimensions (must be ≥1)

    Raises:
        ValueError: For invalid inputs or processing errors
    """
    if scale_factor < 1:
        raise ValueError("Scale factor must be ≥1")
    img = cv2.imread(str(input_path))  # pylint: disable=no-member
    if img is None:
        raise ValueError(f"Could not read image from {input_path}")
    height, width = img.shape[:2]
    upscaled = cv2.resize(  # pylint: disable=no-member
        img,
        (width * scale_factor, height * scale_factor),
        interpolation=cv2.INTER_CUBIC,  # pylint: disable=no-member
    )
    cv2.imwrite(str(output_path), upscaled)  # pylint: disable=no-member


def _validate_ffmpeg() -> None:
    """Check if FFmpeg is available and executable."""
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        raise RuntimeError("FFmpeg is required for video processing") from e

def upscale_video(input_path: Path, output_path: Path, scale_factor: int = 2) -> None:
    """Upscale video by processing individual frames.

    Args:
        input_path: Path to source video
        output_path: Path to save upscaled video
        scale_factor: Multiplier for video dimensions (must be ≥1)

    Raises:
        RuntimeError: If FFmpeg is not available
        ValueError: For invalid inputs
    """
    _validate_ffmpeg()
    if scale_factor < 1:
        raise ValueError("Scale factor must be ≥1")

    if not input_path.exists():
        raise ValueError(f"Input file {input_path} does not exist")

    temp_dir = input_path.parent / "temp_frames"
    temp_dir.mkdir(exist_ok=True)

    # Extract frames
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(input_path), str(temp_dir / "frame_%04d.png")],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to extract frames: {e.stderr}") from e
    # Process frames
    for frame_path in temp_dir.glob("*.png"):
        upscale_image(frame_path, frame_path, scale_factor)
    # Get source video frame rate
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=r_frame_rate",
            "-of",
            "csv=p=0",
            str(input_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    frame_rate = probe.stdout.strip()
    # Rebuild video with original frame rate
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-framerate",
                frame_rate,
                "-i",
                str(temp_dir / "frame_%04d.png"),
                "-c:v",
                "libx264",
                "-preset",
                "slow",
                "-crf",
                "20",
                str(output_path),
            ],
            check=True,
        )
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
