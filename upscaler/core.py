"""Core video upscaling functionality using OpenCV with type hints and error handling."""

import os
from pathlib import Path
from typing import Generator, Tuple
import cv2 as cv  # pylint: disable=import-error
import numpy as np

# pylint: disable=no-member,no-name-in-module
VALID_INTERPOLATIONS = {
    cv.INTER_NEAREST: "nearest neighbor",
    cv.INTER_LINEAR: "bilinear",
    cv.INTER_CUBIC: "bicubic",
    cv.INTER_LANCZOS4: "Lanczos",
}


def generate_test_pattern(width: int, height: int) -> cv.typing.MatLike:
    """Generate a test pattern video frame for verification.

    Args:
        width: Pattern width in pixels
        height: Pattern height in pixels

    Returns:
        Generated frame with test pattern
    """
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    cv.line(frame, (0, 0), (width, height), (0, 255, 0), 2)
    cv.line(frame, (width, 0), (0, height), (0, 255, 0), 2)
    cv.putText(
        frame,
        f"{width}x{height}",
        (10, height - 10),
        cv.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
    )
    return frame


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
) -> Generator[Tuple[int, int, cv.typing.MatLike], None, None]:
    """Process video frames with enhanced validation and error handling.

    Args:
        cap: OpenCV video capture object (must be already opened)
        scale_factor: Integer scaling multiplier (>=1)
        interpolation: OpenCV interpolation method constant

    Yields:
        Tuple containing:
        - original_width: Source frame width in pixels
        - original_height: Source frame height in pixels
        - upscaled_frame: Processed frame as numpy array

    Raises:
        RuntimeError: If frame processing fails at any stage
            or empty frame is received
    """
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame is None or frame.size == 0:
            raise RuntimeError(f"Received invalid frame at position {frame_count}")

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


def _get_video_properties(cap: cv.VideoCapture) -> tuple[float, int, int]:
    """Get and validate essential video properties from capture object.
    
    Args:
        cap: OpenCV video capture object
        
    Returns:
        Tuple of (fps, width, height)
        
    Raises:
        RuntimeError: If any property is invalid
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
        raise ValueError(f"Invalid video dimensions {width}x{height} - must be positive")

    return fps, width, height

def _create_video_writer(
    output_path: Path,
    fourcc: int,
    fps: float,
    output_width: int,
    output_height: int,
) -> cv.VideoWriter:
    """Create and validate video writer object."""
    out = cv.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (output_width, output_height))
    if not out.isOpened():
        raise RuntimeError(
            f"Failed to initialize video writer for {output_path} - "
            "verify directory permissions and codec support"
        )
    return out

def _select_video_codec() -> tuple[int, str]:
    """Select appropriate video codec with validation."""
    codec_priority = [
        ("avc1", "H.264/MPEG-4 AVC (modern compatibility)"),
        ("mp4v", "MPEG-4 Part 2 (legacy)"),
        ("X264", "X264 encoder"),
    ]
    
    for codec, description in codec_priority:
        fourcc = cv.VideoWriter_fourcc(*codec)  # pylint: disable=no-member
        if fourcc != 0:
            validate_codec(fourcc)
            return fourcc, description
    
    validate_codec(0)  # Will throw error
    raise RuntimeError("Code path should never be reached")  # For type checker

def upscale_video(
    input_path: Path,
    output_path: Path,
    scale_factor: int,
    interpolation: int = cv.INTER_CUBIC,
) -> None:
    """Upscale video frames using specified interpolation method with validation.

    Example:
        >>> upscale_video(Path("input.mp4"), Path("output.mp4"), 2, cv.INTER_CUBIC)

    Args:
        input_path: Path to existing input video file
        output_path: Path for new output video file (will be overwritten)
        scale_factor: Multiplier for video dimensions (must be >=1)
        interpolation: OpenCV interpolation method constant to use

    Raises:
        ValueError: For invalid paths or scaling parameters
        RuntimeError: If video processing fails at any stage
        FileNotFoundError: If input file doesn't exist

    Maintains original frame rate and aspect ratio using streaming processing.
    """

    def _validate_inputs() -> None:
        """Validate all input parameters and paths.

        Raises:
            FileNotFoundError: If input file is missing
            ValueError: For invalid paths or scaling parameters
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
            raise PermissionError(
                f"Output directory not writable: {output_path.parent}"
            )
        if scale_factor < 1:
            raise ValueError(f"Scale factor must be >=1 (got {scale_factor})")

    _validate_inputs()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not output_path.parent.exists():
        raise FileNotFoundError(
            f"Output directory creation failed: {output_path.parent}"
        )
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

    # Set up output video codec and writer with modern codec priority
    fourcc, selected_codec = _select_video_codec()
    output_width: int = width * scale_factor
    output_height: int = height * scale_factor
    if output_width > 7680 or output_height > 4320:  # 8K resolution check
        raise ValueError(
            f"Output dimensions {output_width}x{output_height} exceed 8K UHD resolution"
        )
    out = _create_video_writer(output_path, fourcc, fps, output_width, output_height)

    try:
        # Process frames and write output
        frame_count = 0
        for _, _, upscaled in process_frames(cap, scale_factor, interpolation):
            frame_count += 1
            if upscaled.shape[1] != output_width or upscaled.shape[0] != output_height:
                raise RuntimeError(
                    f"Frame size mismatch at frame {frame_count}: "
                    f"Expected {output_width}x{output_height}, "
                    f"got {upscaled.shape[1]}x{upscaled.shape[0]}. "
                    "This could indicate memory corruption or hardware acceleration issues."
                )
            out.write(upscaled)

    except cv.error as e:  # pylint: disable=no-member
        raise RuntimeError(f"OpenCV processing error: {e}") from e
    finally:
        cap.release()
        out.release()
