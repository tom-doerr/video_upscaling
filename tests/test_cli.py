"""Tests for command line interface"""

import numpy as np
import cv2
from click.testing import CliRunner
from vidscale.cli import main


def test_cli_image_upscaling(tmp_path):
    """Test image upscaling CLI command"""
    runner = CliRunner()
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"

    # Create valid test image
    cv2.imwrite(str(input_path), np.zeros((100, 100, 3), dtype=np.uint8))
    
    result = runner.invoke(
        main, ["image", str(input_path), str(output_path), "--scale", "2"]
    )
    assert result.exit_code == 0
    assert output_path.exists()

    # Test overwrite protection
    result = runner.invoke(
        main, ["image", str(input_path), str(output_path), "--scale", "2"]
    )
    assert "already exists" in result.output


def test_cli_invalid_scale_factor(tmp_path):
    """Test invalid scale factor handling"""
    runner = CliRunner()
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    input_path.touch()
    result = runner.invoke(
        main, ["image", str(input_path), str(output_path), "--scale", "0"]
    )
    assert result.exit_code != 0
    assert "Scale factor must be ≥1" in result.output


def test_cli_video_upscaling(tmp_path):
    """Test video upscaling CLI command"""
    runner = CliRunner()
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "nested/output.mp4"  # Test directory creation
    input_path.touch()

    result = runner.invoke(
        main, ["video", str(input_path), str(output_path), "--scale", "2"]
    )
    assert result.exit_code == 0
    assert output_path.exists()


def test_cli_nonexistent_input(tmp_path):
    """Test handling of non-existent input file"""
    runner = CliRunner()
    output_path = tmp_path / "output.jpg"
    result = runner.invoke(
        main, ["image", "nonexistent.jpg", str(output_path), "--scale", "2"]
    )
    assert result.exit_code != 0
    assert "does not exist" in result.output
