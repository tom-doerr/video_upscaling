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
        Parsed arguments namespace

    Raises:
        SystemExit: For invalid arguments or help request
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
        type=int, 
        required=True, 
        help="Scaling factor (integer multiplier, e.g. 2 doubles each dimension)"
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
                "Supported formats: .mp4, .avi, .mov"
            )

        # Map and validate interpolation method
        interpolation_map = {
            # pylint: disable=no-member
            "nearest": cv.INTER_NEAREST,  # Fastest but lowest quality
            "linear": cv.INTER_LINEAR,  # Balance of speed/quality
            "cubic": cv.INTER_CUBIC,  # Slower but higher quality
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
    except (ValueError, FileNotFoundError) as e:
        print(f"Input error: {e}", file=sys.stderr)
        sys.exit(1)
    except (RuntimeError, OSError) as e:
        print(f"Processing error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Unexpected error: {e.__class__.__name__} - {e}", file=sys.stderr)
        if args.debug:  # type: ignore
            traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()
