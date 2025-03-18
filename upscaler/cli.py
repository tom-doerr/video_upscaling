"""Command line interface for video upscaling package."""

import argparse
from pathlib import Path
import cv2  # pylint: disable=import-error
from .core import upscale_video


def main() -> None:
    """Command line interface for video upscaling.
    
    Raises:
        ValueError: If invalid arguments are provided
        RuntimeError: If video processing fails
    """
    parser = argparse.ArgumentParser(
        description="Upscale video using interpolation methods"
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
        help="Interpolation method",
    )

    args = parser.parse_args()

    # Map interpolation names to OpenCV constants
    interpolation_map = {
        "nearest": cv2.INTER_NEAREST,  # Fastest but lowest quality
        "linear": cv2.INTER_LINEAR,    # Balance of speed/quality
        "cubic": cv2.INTER_CUBIC,     # Slower but higher quality (default)
        "lanczos": cv2.INTER_LANCZOS4, # Highest quality but slowest
    }

    upscale_video(
        input_path=args.input,
        output_path=args.output,
        scale_factor=args.scale,
        interpolation=interpolation_map[args.interpolation],
    )


if __name__ == "__main__":
    main()
