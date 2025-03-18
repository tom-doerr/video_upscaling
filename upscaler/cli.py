"""Command line interface for video upscaling package.

Example usage:
    upscale-video input.mp4 output.mp4 --scale 2 --interpolation cubic
"""

import argparse
import sys
from pathlib import Path

import cv2 as cv  # pylint: disable=import-error,no-member
from .core import upscale_video


def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        Parsed arguments namespace

    Raises:
        SystemExit: For invalid arguments or help request
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
        help="Interpolation algorithm to use (default: %(default)s)",
    )

    return parser.parse_args()


def main() -> None:
    """Command line interface entry point for video upscaling.

    Exit codes:
        0: Success
        1: Input validation error
        2: Processing error
        3: Unexpected error

    Raises:
        SystemExit: Always exits with status code
    """
    try:
        args = parse_args()
        # Validate scale factor early
        if args.scale < 1:
            raise ValueError(f"Invalid scale factor {args.scale} - must be >= 1")

        # Validate output format
        if args.output.suffix.lower() not in (".mp4", ".avi", ".mov"):
            raise ValueError(
                f"Unsupported output format '{args.output.suffix}'. "
                "Supported formats: .mp4, .avi, .mov"
            )

        # Map and validate interpolation method
        interpolation_map = {
            "nearest": cv.INTER_NEAREST,  # pylint: disable=no-member  # Fastest but lowest quality
            "linear": cv.INTER_LINEAR,  # pylint: disable=no-member  # Balance of speed/quality
            "cubic": cv.INTER_CUBIC,  # pylint: disable=no-member  # Slower but higher quality (default)
            "lanczos": cv.INTER_LANCZOS4,  # pylint: disable=no-member  # Highest quality but slowest
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
    except PermissionError as e:
        print(f"Permission denied: {e}", file=sys.stderr)
        sys.exit(3)
    except (ValueError, RuntimeError, FileNotFoundError, OSError) as e:
        error_msg = f"Error processing {args.input}: {e.__class__.__name__} - {e}"
        print(error_msg, file=sys.stderr)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error: {e.__class__.__name__} - {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
