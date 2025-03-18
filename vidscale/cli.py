"""Command line interface for video upscaling package"""
import click
from pathlib import Path
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
    upscale_image(Path(input_path), Path(output_path), scale)
    click.echo(f"Successfully upscaled image by {scale}x")

@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
@click.option("--scale", type=int, default=2, help="Scaling factor")
def video(input_path, output_path, scale):
    """Upscale a video"""
    upscale_video(Path(input_path), Path(output_path), scale)
    click.echo(f"Successfully upscaled video by {scale}x")
