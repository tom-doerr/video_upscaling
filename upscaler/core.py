"""Core video upscaling functionality using OpenCV."""

from pathlib import Path
import cv2 as cv  # pylint: disable=import-error


def upscale_video(  # pylint: disable=too-many-locals,too-many-branches
    input_path: Path,
    output_path: Path,
    scale_factor: int,
    interpolation: int = cv.INTER_CUBIC,
) -> None:
    """Upscale video frames using specified interpolation method.

    Processes video frame-by-frame, resizing each frame using the specified
    scaling factor and interpolation method. Maintains original frame rate
    and aspect ratio.

    Args:
        input_path: Path to existing input video file
        output_path: Path for new output video file (will be overwritten)
        scale_factor: Multiplier for video dimensions (must be ≥1)
        interpolation: OpenCV interpolation method constant to use

    Raises:
        ValueError: For invalid paths or scaling parameters
        RuntimeError: If video processing fails at any stage
        FileNotFoundError: If input file doesn't exist
    """

    def _validate_inputs() -> None:
        """Validate all input parameters and paths.

        Raises:
            FileNotFoundError: If input file is missing
            ValueError: For invalid paths or scaling parameters
        """
        if not input_path.is_file():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if output_path.is_dir():
            raise ValueError(f"Output path is a directory: {output_path}")
        if scale_factor < 1:
            raise ValueError(f"Scale factor must be ≥1 (got {scale_factor})")

    _validate_inputs()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Open input video with validation
    cap = cv.VideoCapture(str(input_path))
    if not cap.isOpened():
        raise ValueError(
            f"Could not open video file {input_path} - "
            "check if file exists and codec is supported"
        )

    # Get video properties with type hints
    def get_video_prop(prop_id: int) -> float:
        """Get video property with validation."""
        value = cap.get(prop_id)
        if value < 0:
            raise RuntimeError(f"Failed to get video property {prop_id}")
        return value

    fps: float = get_video_prop(cv.CAP_PROP_FPS)
    width: int = int(get_video_prop(cv.CAP_PROP_FRAME_WIDTH))
    height: int = int(get_video_prop(cv.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0:
        raise ValueError(f"Invalid frame rate {fps} - must be positive")
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid video dimensions {width}x{height} - must be positive"
        )

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
