import pytest
from click.testing import CliRunner
from vidscale.cli import main

def test_cli_image_upscaling(tmp_path):
    runner = CliRunner()
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    input_path.touch()
    
    result = runner.invoke(main, [
        "image", str(input_path), str(output_path), "--scale", "2"
    ])
    assert result.exit_code == 0
    assert output_path.exists()

def test_cli_video_upscaling(tmp_path):
    runner = CliRunner()
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    input_path.touch()
    
    result = runner.invoke(main, [
        "video", str(input_path), str(output_path), "--scale", "2"
    ])
    assert result.exit_code == 0
