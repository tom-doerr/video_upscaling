"""Tests for core upscaling functionality"""
import pytest  # pylint: disable=unused-import
import cv2
import numpy as np
from vidscale.core import upscale_image, upscale_video

def test_upscale_image(tmp_path):
    """Test image upscaling functionality"""
    # Create test image
    test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    cv2.imwrite(str(input_path), test_img)
    
    # Test upscaling
    upscale_image(input_path, output_path, scale_factor=2)
    
    # Verify output
    result = cv2.imread(str(output_path))
    assert result.shape == (200, 200, 3)

def test_upscale_video(mocker, tmp_path):
    # Mock FFmpeg calls to avoid actual video processing
    mock_run = mocker.patch('subprocess.run')
    
    # Create test video file
    input_path = tmp_path / "input.mp4"
    output_path = tmp_path / "output.mp4"
    input_path.touch()
    
    # Test upscaling
    upscale_video(input_path, output_path, scale_factor=2)
    
    # Verify FFmpeg was called
    assert mock_run.call_count == 3
