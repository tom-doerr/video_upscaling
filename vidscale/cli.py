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
    
    if not input_path.exists():
        raise click.BadParameter(f"Input file {input_path} does not exist")
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        upscale_image(input_path, output_path, scale)
        click.echo(f"Successfully upscaled image by {scale}x")
    except Exception as e:
        click.echo(f"Error processing image: {str(e)}", err=True)
        raise click.Abort()


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--scale", type=int, default=2, help="Scaling factor")
def video(input_path, output_path, scale):
    """Upscale a video"""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        raise click.BadParameter(f"Input file {input_path} does not exist")
        
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        upscale_video(input_path, output_path, scale)
        click.echo(f"Successfully upscaled video by {scale}x")
    except Exception as e:
        click.echo(f"Error processing video: {str(e)}", err=True)
        raise click.Abort()
