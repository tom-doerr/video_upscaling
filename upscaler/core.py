"""Core video upscaling functionality using OpenCV."""

from pathlib import Path
import cv2  # pylint: disable=import-error


def upscale_video(
    input_path: Path,
    output_path: Path,
    scale_factor: int,
    interpolation: int = cv2.INTER_CUBIC,
) -> None:
    """Upscale video frames using specified interpolation method.

    Args:
        input_path: Path to input video file
        output_path: Path for output video file
        scale_factor: Multiplier for video dimensions (must be ≥1)
        interpolation: OpenCV interpolation method constant to use

    Raises:
        ValueError: For invalid inputs or scaling parameters
        RuntimeError: If video processing fails at any stage
    """
    # Open input video with validation
    cap = cv.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(
            f"Could not open video file {input_path} - "
            "check if file exists and codec is supported"
        )

    # Get and validate video properties
    fps: float = cap.get(cv2.CAP_PROP_FPS)
    width: int = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height: int = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0:
        raise ValueError(f"Invalid frame rate {fps} - must be positive")
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid video dimensions {width}x{height} - must be positive"
        )
    # Validate scaling parameters
    if scale_factor < 1:
        raise ValueError(f"Scale factor must be ≥1, got {scale_factor}")

    # Set up output video codec and writer
    fourcc: int = cv.VideoWriter_fourcc(*"mp4v")
    if fourcc == 0:
        raise RuntimeError("Failed to initialize MP4V codec - check codec support")
    output_width: int = width * scale_factor
    output_height: int = height * scale_factor
    if output_width > 7680 or output_height > 4320:  # 8K resolution check
        raise ValueError(
            f"Output dimensions {output_width}x{output_height} exceed 8K UHD resolution"
        )
    out = cv.VideoWriter(str(output_path), fourcc, fps, (output_width, output_height))

    if not out.isOpened():
        raise RuntimeError(
            f"Failed to initialize video writer for {output_path} - "
            "verify directory permissions and codec support"
        )

    try:
        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            # Upscale frame with validation
            if frame.size == 0:
                raise RuntimeError(f"Received empty frame at position {frame_count}")

            upscaled = cv.resize(
                frame,
                None,
                fx=scale_factor,
                fy=scale_factor,
                interpolation=interpolation,
            )
            out.write(upscaled)
            frame_count += 1

        if frame_count == 0:
            raise RuntimeError("No frames processed - input video may be corrupted")

    except cv.error as e:
        raise RuntimeError(f"OpenCV processing error: {e}") from e
    finally:
        cap.release()
        out.release()
