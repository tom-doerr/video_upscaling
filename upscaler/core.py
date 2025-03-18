"""Core video upscaling functionality using OpenCV with type hints and error handling."""

import os
from pathlib import Path
from typing import Dict, Generator, Tuple
import numpy as np
import cv2 as cv  # pylint: disable=import-error

# pylint: disable=no-member
VALID_INTERPOLATIONS: Dict[int, str] = {
    cv.INTER_NEAREST: "nearest neighbor",
    cv.INTER_LINEAR: "bilinear",
    cv.INTER_CUBIC: "bicubic",
    cv.INTER_LANCZOS4: "Lanczos",
}
"""Dictionary mapping OpenCV interpolation constants to human-readable names"""


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
    cap: cv.VideoCapture,
    scale_factor: float,
    interpolation: int,
) -> Generator[Tuple[int, int, np.ndarray], None, None]:
    """Process video frames with enhanced validation and error handling.

    Args:
        cap: OpenCV video capture object (must be already opened)
        scale_factor: Scaling multiplier (>=1)
        interpolation: OpenCV interpolation method constant

    Yields:
        Tuple containing:
        - original_width: Source frame width in pixels
        - original_height: Source frame height in pixels
        - upscaled_frame: Processed frame as numpy array

    Raises:
        RuntimeError: If frame processing fails at any stage or empty frame is received
    """
    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame is None or frame.size == 0:
            raise RuntimeError(
                f"Received invalid frame {frame_count} (size={frame.size if frame else 0})"
            )

        upscaled = cv.resize(
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


def _get_video_properties(cap: cv.VideoCapture) -> Tuple[float, int, int]:
    """Extract and validate video properties from capture object.

    Args:
        cap: OpenCV video capture object

    Returns:
        Tuple containing:
        - fps: Frame rate as float
        - width: Frame width as integer
        - height: Frame height as integer

    Raises:
        RuntimeError: If any property cannot be retrieved
        ValueError: For invalid property values
    """

    def get_checked_prop(prop_id: int, name: str) -> float:
        """Get property with validation."""
        value = cap.get(prop_id)
        if value < 0:
            raise RuntimeError(f"Failed to get {name}")
        return value

    fps = get_checked_prop(cv.CAP_PROP_FPS, "frame rate")
    width = int(get_checked_prop(cv.CAP_PROP_FRAME_WIDTH, "frame width"))
    height = int(get_checked_prop(cv.CAP_PROP_FRAME_HEIGHT, "frame height"))

    if fps <= 0:
        raise ValueError(f"Invalid frame rate {fps} - must be positive")
    if width <= 0 or height <= 0:
        raise ValueError(
            f"Invalid video dimensions {width}x{height} - must be positive"
        )

    return fps, width, height


def _create_video_writer(
    output_path: Path,
    fourcc: int,
    fps: float,
    frame_size: tuple[int, int],
    codec_priority: list[str],
) -> cv.VideoWriter:
    """Create and validate video writer object with dimension checks.

    Args:
        output_path: Path for output video file
        fourcc: OpenCV fourcc codec code
        fps: Frame rate of output video
        frame_size: Tuple of (width, height) for output frames
        codec_priority: List of codecs tried for error reporting

    Returns:
        OpenCV VideoWriter object

    Raises:
        RuntimeError: If video writer cannot be initialized
        ValueError: For invalid frame dimensions
    """
    if frame_size[0] <= 0 or frame_size[1] <= 0:
        raise ValueError(
            f"Invalid frame dimensions {frame_size} - must be positive integers"
        )
    out = cv.VideoWriter(str(output_path), fourcc, fps, frame_size)
    if not out.isOpened():
        raise RuntimeError(
            f"Failed to initialize video writer for {output_path} - "
            f"tried codecs: {codec_priority}. Verify directory permissions and codec support."
        )
    return out


def _validate_input_paths(input_path: Path, output_path: Path) -> None:
    """Validate input/output paths meet requirements.

    Args:
        input_path: Path to source video file
        output_path: Path for output video file

    Raises:
        FileNotFoundError: If input path doesn't exist
        ValueError: For invalid path configurations
        PermissionError: If output directory isn't writable
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_path}")
    if output_path.is_dir():
        raise ValueError(f"Output path is a directory: {output_path}")
    if not output_path.parent.exists():
        raise ValueError(f"Output directory does not exist: {output_path.parent}")
    if not os.access(output_path.parent, os.W_OK):
        raise PermissionError(f"Output directory not writable: {output_path.parent}")


def _select_video_codec() -> tuple[int, list[str]]:
    """Select appropriate video codec with validation.

    Returns:
        Tuple containing fourcc code and list of tried codecs

    Raises:
        RuntimeError: If no valid codec could be initialized
    """
    codec_priority = [
        "mp4v",  # MPEG-4 Part 2 (required for .mp4)
        "avc1",  # H.264/AVC (more common fourcc code)
        "xvid",  # XVID (better for .avi)
        "mjpg",  # Motion-JPEG (for .mov)
    ]
    for codec in codec_priority:
        fourcc = cv.VideoWriter_fourcc(*codec)
        if fourcc != 0:
            validate_codec(fourcc)
            return fourcc, codec_priority
    validate_codec(0)  # Will throw error
    raise RuntimeError(
        "No valid video codec found - tried codecs: "
        f"{codec_priority}. Verify OpenCV installation supports at least one "
        "of these codecs."
    )


def upscale_video(
    input_path: Path,
    output_path: Path,
    scale_factor: float,
    interpolation: int = cv.INTER_CUBIC,
) -> None:
    """Upscale video frames using specified interpolation method with validation.

    Examples:
        ```python
        upscale_video(
            input_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
            scale_factor=2.0
        )

        upscale_video(
            input_path=Path("input.mp4"),
            output_path=Path("output.mp4"),
            scale_factor=2.0,
            interpolation=cv.INTER_CUBIC
        )
        ```

    Args:
        input_path: Path to existing input video file
        output_path: Path for new output video file (will be overwritten)
        scale_factor: Multiplier for video dimensions (must be >=1)
        interpolation: OpenCV interpolation method constant to use

    Raises:
        ValueError: For invalid paths, scaling parameters, or unsupported interpolation
        RuntimeError: If video processing fails at any stage
        FileNotFoundError: If input file doesn't exist
        PermissionError: For output directory write issues

    Maintains original frame rate and aspect ratio using streaming processing.
    """

    # Validate input parameters and paths
    _validate_input_paths(input_path, output_path)
    if scale_factor < 1:
        raise ValueError(
            f"Scale factor must be >=1 (got {scale_factor}). "
            "Use --scale 2 to double video dimensions"
        )

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Open input video with validation
    cap = cv.VideoCapture(str(input_path))  # pylint: disable=no-member
    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video file {input_path} - "
            "file may be corrupted, codec unsupported, or permissions invalid"
        )

    # Get validated video properties
    fps, width, height = _get_video_properties(cap)

    # Validate interpolation method
    if interpolation not in VALID_INTERPOLATIONS:
        raise ValueError(
            f"Invalid interpolation method: {interpolation}. "
            f"Valid methods: {', '.join(VALID_INTERPOLATIONS.values())}"
        )

    # Set up output video codec and writer
    codec_info = _select_video_codec()
    output_dims = (width * scale_factor, height * scale_factor)
    if output_dims[0] > 7680 or output_dims[1] > 4320:  # 8K resolution check
        raise ValueError(
            f"Output dimensions {output_dims[0]}x{output_dims[1]} exceed 8K UHD resolution"
        )
    out = _create_video_writer(
        output_path,
        codec_info[0],
        fps,
        output_dims,
        codec_info[1],
    )

    try:
        # Process frames and write output
        for frame_count, (_, _, upscaled) in enumerate(
            process_frames(cap, scale_factor, interpolation), 1
        ):
            if (
                upscaled.shape[1] != output_dims[0]
                or upscaled.shape[0] != output_dims[1]
            ):
                raise RuntimeError(
                    f"Frame size mismatch at frame {frame_count}: "
                    f"Expected {output_dims[0]}x{output_dims[1]}, "
                    f"got {upscaled.shape[1]}x{upscaled.shape[0]}. "
                    "This could indicate memory corruption or hardware acceleration issues."
                )
            out.write(upscaled)

    except cv.error as e:  # pylint: disable=no-member
        raise RuntimeError(
            f"OpenCV processing failed: {e}. Check that input is a valid video file "
            f"and output codec supports {scale_factor}x scaling."
        ) from e
    finally:
        # Ensure proper resource cleanup even if errors occur
        cap.release()
        if "out" in locals() and out.isOpened():
            out.release()
