"""Command line interface for video upscaling package"""

from pathlib import Path
import click
from vidscale.core import upscale_image, upscale_video


@click.group()
def main():
    """Video upscaling CLI tool"""


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--scale", type=int, default=2, help="Scaling factor")
def image(input_path, output_path, scale):
    """Upscale an image"""
    input_path = Path(input_path)
    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        if output_path.exists():
            raise FileExistsError(f"Output path {output_path} already exists")
        upscale_image(input_path, output_path, scale)
        click.echo(f"Successfully upscaled image by {scale}x")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise SystemExit(1) from e


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--scale", type=int, default=2, help="Scaling factor")
def video(input_path, output_path, scale):
    """Upscale a video"""
    input_path = Path(input_path)
    output_path = Path(output_path)

    try:
        # Create parent dirs first before checking for existing output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            raise FileExistsError(f"Output path {output_path} already exists")
            
        upscale_video(input_path, output_path, scale)
        click.echo(f"Successfully upscaled video by {scale}x")
    except FileExistsError as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise SystemExit(1) from e
    except ValueError as e:
        click.echo(f"Validation error: {str(e)}", err=True)
        raise SystemExit(1) from e
    except RuntimeError as e:  # For FFmpeg errors
        click.echo(f"Video processing error: {str(e)}", err=True)
        raise SystemExit(1) from e
    except Exception as e:
        click.echo(f"Unexpected error: {str(e)}", err=True)
        raise SystemExit(1) from e
