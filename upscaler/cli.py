"""Command line interface for video upscaling package.

Example usage:
    upscale-video input.mp4 output.mp4 --scale 2 --interpolation cubic
"""

import argparse
import sys
import traceback
from pathlib import Path

import cv2 as cv  # pylint: disable=import-error,no-member
from . import __version__
from .core import upscale_video


def parse_args() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments

    Raises:
        SystemExit: For help request or argument parsing failure
    """
    parser = argparse.ArgumentParser(
        prog="upscale-video",
        description="Upscale video dimensions using spatial interpolation methods",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Note: Output video format is determined by the file extension "
        "(supports .mp4, .avi, .mov)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("input", type=Path, help="Input video path")
    parser.add_argument("output", type=Path, help="Output video path")
    parser.add_argument(
        "--scale",
        type=float,
        required=True,
        help="Scaling factor (e.g. 2.0 doubles dimensions, 1.5 increases by 50%)",
    )
    parser.add_argument(
        "--interpolation",
        type=str,
        default="cubic",
        choices=["nearest", "linear", "cubic", "lanczos"],
        help="Interpolation algorithm (nearest=fastest, lanczos=best quality)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with stack traces on error",
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
                "Supported formats: .mp4, .avi, .mov (case-insensitive)"
            )

        # Map interpolation names to OpenCV constants with quality notes
        interpolation_map = {
            "nearest": cv.INTER_NEAREST,  # Fastest, lowest quality (good for pixel art)
            "linear": cv.INTER_LINEAR,  # Balanced quality/speed (recommended for most cases)
            "cubic": cv.INTER_CUBIC,  # Higher quality, slower (better for photos)
            "lanczos": cv.INTER_LANCZOS4,  # Highest quality, very slow (8x8 kernel)
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
    except (ValueError, FileNotFoundError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError) as e:
        print(f"Processing error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error: {e.__class__.__name__} - {e}", file=sys.stderr)
        if 'args' in locals() and args.debug:  # Safer check for debug mode
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
