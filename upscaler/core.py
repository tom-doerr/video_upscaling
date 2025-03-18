"""Core video upscaling functionality using OpenCV."""
from pathlib import Path
import cv2

def upscale_video(
    input_path: Path,
    output_path: Path,
    scale_factor: int,
    interpolation: int = cv2.INTER_CUBIC
) -> None:
    """Upscale video frames using specified interpolation method.
    
    Args:
        input_path: Path to input video file
        output_path: Path for output video file
        scale_factor: Multiplier for video dimensions
        interpolation: OpenCV interpolation method to use
    """
    # Open input video
    cap = cv2.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file {input_path}")

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Set up output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width * scale_factor, height * scale_factor)
    )

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Upscale frame
            upscaled = cv2.resize(
                frame,
                None,
                fx=scale_factor,
                fy=scale_factor,
                interpolation=interpolation
            )
            out.write(upscaled)
    finally:
        cap.release()
        out.release()
