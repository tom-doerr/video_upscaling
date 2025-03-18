"""Core video upscaling functionality using OpenCV."""

from pathlib import Path
from typing import Generator, Tuple
import cv2 as cv  # pylint: disable=import-error,no-member


def validate_codec(fourcc: int) -> None:
    """Validate video codec is supported.

    Args:
        fourcc: OpenCV fourcc code

    Raises:
        RuntimeError: If codec is not supported
    """
    if fourcc == 0:
        raise RuntimeError(
            "Failed to initialize video codec - try different output extension "
            "(supported formats: .mp4, .avi, .mov)"
        )


def process_frames(
    cap: cv.VideoCapture,  # pylint: disable=no-member
    scale_factor: int,
    interpolation: int,  # pylint: disable=no-member
) -> Generator[Tuple[int, int, cv.typing.MatLike], None, None]:
    """Process video frames and yield upscaled versions in real-time.

    Args:
        cap: OpenCV video capture object (must be already opened)
        scale_factor: Integer scaling multiplier (≥1)
        interpolation: OpenCV interpolation method constant

    Yields:
        Tuple containing:
        - Original frame width
        - Original frame height
        - Upscaled frame as numpy array

    Raises:
        RuntimeError: If frame processing fails at any stage
    """
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame.size == 0:
            raise RuntimeError(f"Received empty frame at position {frame_count}")

        upscaled = cv.resize(  # pylint: disable=no-member
            frame,
            None,
            fx=scale_factor,
            fy=scale_factor,
            interpolation=interpolation,
        )
        yield frame.shape[1], frame.shape[0], upscaled
        frame_count += 1

    if frame_count == 0:
        raise RuntimeError("No frames processed - input video may be corrupted")


def upscale_video(  # pylint: disable=too-many-locals
    input_path: Path,
    output_path: Path,
    scale_factor: int,
    interpolation: int = cv.INTER_CUBIC,  # pylint: disable=no-member
) -> None:
    """Upscale video frames using specified interpolation method with validation.

    The upscaling process:
    1. Validates input parameters and paths
    2. Reads video metadata
    3. Initializes output video writer
    4. Processes frames in streaming fashion
    5. Maintains original frame rate and aspect ratio

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
    cap = cv.VideoCapture(str(input_path))  # pylint: disable=no-member
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

    fps: float = get_video_prop(cv.CAP_PROP_FPS)  # pylint: disable=no-member
    width: int = int(
        get_video_prop(cv.CAP_PROP_FRAME_WIDTH)  # pylint: disable=no-member
    )  # pylint: disable=no-member
    height: int = int(
        get_video_prop(cv.CAP_PROP_FRAME_HEIGHT)  # pylint: disable=no-member
    )  # pylint: disable=no-member
    if fps <= 0:
        raise ValueError(f"Invalid frame rate {fps} - must be positive")
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid video dimensions {width}x{height} - must be positive"
        )

    # Validate interpolation method
    valid_interpolations = {
        cv.INTER_NEAREST: "nearest neighbor",  # pylint: disable=no-member
        cv.INTER_LINEAR: "bilinear",  # pylint: disable=no-member
        cv.INTER_CUBIC: "bicubic",  # pylint: disable=no-member
        cv.INTER_LANCZOS4: "Lanczos",  # pylint: disable=no-member
    }
    if interpolation not in valid_interpolations:
        raise ValueError(
            f"Invalid interpolation method: {interpolation}. "
            f"Valid methods: {', '.join(valid_interpolations.values())}"
        )

    # Set up output video codec and writer
    # Try more modern codecs first before falling back to MP4V
    for codec in ["avc1", "mp4v", "X264"]:
        fourcc = cv.VideoWriter_fourcc(*codec)  # pylint: disable=no-member
        if fourcc != 0:
            break
    validate_codec(fourcc)
    output_width: int = width * scale_factor
    output_height: int = height * scale_factor
    if output_width > 7680 or output_height > 4320:  # 8K resolution check
        raise ValueError(
            f"Output dimensions {output_width}x{output_height} exceed 8K UHD resolution"
        )
    out = cv.VideoWriter(  # pylint: disable=no-member
        str(output_path), fourcc, fps, (output_width, output_height)
    )

    if not out.isOpened():
        raise RuntimeError(
            f"Failed to initialize video writer for {output_path} - "
            "verify directory permissions and codec support"
        )

    try:
        # Process frames and write output
        for _, _, upscaled in process_frames(cap, scale_factor, interpolation):
            if (upscaled.shape[1], upscaled.shape[0]) != (output_width, output_height):
                raise RuntimeError(
                    f"Frame size mismatch: Expected {output_width}x{output_height}, "
                    f"got {upscaled.shape[1]}x{upscaled.shape[0]}"
                )
            out.write(upscaled)

    except cv.error as e:  # pylint: disable=no-member
        raise RuntimeError(f"OpenCV processing error: {e}") from e
    finally:
        cap.release()
        out.release()
