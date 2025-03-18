"""Command line interface for video upscaling package.

Example usage:
    upscale-video input.mp4 output.mp4 --scale 2 --interpolation cubic
"""

import argparse
from pathlib import Path
import cv2 as cv  # pylint: disable=import-error
from .core import upscale_video


def main() -> None:
    """Command line interface for video upscaling.

    Raises:
        ValueError: For invalid inputs or scaling parameters
        RuntimeError: If video processing fails at any stage
    """
    parser = argparse.ArgumentParser(
        description="Upscale video dimensions using spatial interpolation methods",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("input", type=Path, help="Input video path")
    parser.add_argument("output", type=Path, help="Output video path")
    parser.add_argument(
        "--scale", type=int, required=True, help="Scaling factor (integer multiplier)"
    )
    parser.add_argument(
        "--interpolation",
        type=str,
        default="cubic",
        choices=["nearest", "linear", "cubic", "lanczos"],
        help="Interpolation method (nearest=fastest, lanczos=best quality)",
    )

    args = parser.parse_args()

    if args.scale < 1:
        raise ValueError(f"Invalid scale factor {args.scale} - must be ≥1")

    # Map interpolation names to OpenCV constants
    interpolation_map = {
        "nearest": cv.INTER_NEAREST,  # Fastest but lowest quality
        "linear": cv.INTER_LINEAR,  # Balance of speed/quality
        "cubic": cv.INTER_CUBIC,  # Slower but higher quality (default)
        "lanczos": cv.INTER_LANCZOS4,  # Highest quality but slowest
    }

    try:
        interpolation_method = interpolation_map[args.interpolation]
    except KeyError as e:
        raise ValueError(
            f"Invalid interpolation method '{args.interpolation}'. "
            f"Valid choices are: {list(interpolation_map.keys())}"
        ) from e

    upscale_video(
        input_path=args.input,
        output_path=args.output,
        scale_factor=args.scale,
        interpolation=interpolation_method,
    )


if __name__ == "__main__":
    main()
