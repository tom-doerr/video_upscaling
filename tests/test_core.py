"""Tests for core upscaling functionality"""

from pathlib import Path
import subprocess
from unittest.mock import patch
import pytest
import cv2  # pylint: disable=import-error
import numpy as np
from vidscale.core import upscale_image, upscale_video


def test_upscale_image(tmp_path):
    """Test image upscaling functionality"""
    # Create test image
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    cv2.imwrite(str(input_path), test_img)  # pylint: disable=no-member

    # Test upscaling
    upscale_image(input_path, output_path, scale_factor=2)

    # Verify output
    result = cv2.imread(str(output_path))  # pylint: disable=no-member
    assert result.shape == (200, 200, 3)
    assert result.dtype == np.uint8
    # Verify some pixel values changed (not just black/white)
    assert np.any(result != test_img.repeat(2, axis=0).repeat(2, axis=1))

def test_upscale_image_invalid_path(tmp_path):
    """Test image upscaling with invalid input path"""
    with pytest.raises(ValueError):
        upscale_image(tmp_path / "nonexistent.jpg", tmp_path / "output.jpg", 2)

def test_upscale_image_invalid_scale():
    """Test invalid scale factor validation"""
    with pytest.raises(ValueError):
        upscale_image(Path("input.jpg"), Path("output.jpg"), 0)

def test_upscale_video_invalid_input(tmp_path):
    """Test video upscaling with invalid input"""
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    # Test with non-existent input file
    with pytest.raises(ValueError):
        upscale_video(input_path, output_path, 2)
    # Test with invalid scale factor
    input_path.touch()
    with pytest.raises(ValueError):
        upscale_video(input_path, output_path, 0)

@patch("subprocess.run")
def test_upscale_video_ffmpeg_failure(mock_run, tmp_path):
    """Test video upscaling when FFmpeg fails"""
    mock_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
    input_path = tmp_path / "input.mp4"
    input_path.touch()
    with pytest.raises(RuntimeError):
        upscale_video(input_path, tmp_path / "output.mp4", 2)


def test_upscale_video(mocker, tmp_path):
    """Test video upscaling functionality with mocked FFmpeg"""
    # Mock FFmpeg calls to avoid actual video processing
    mock_run = mocker.patch("subprocess.run")

    # Create test video file
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    input_path.touch()

    # Test upscaling
    upscale_video(input_path, output_path, scale_factor=2)

    # Verify FFmpeg was called
    assert mock_run.call_count == 3
