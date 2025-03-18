"""Unit tests for core video upscaling functionality."""

from upscaler.core import upscale_video, _validate_input_paths  # pylint: disable=import-error
import pytest

def test_validate_input_paths_nonexistent_file(tmp_path):
    """Test validation fails when input file doesn't exist."""
    fake_file = tmp_path / "nonexistent.mp4"
    with pytest.raises(FileNotFoundError):
        _validate_input_paths(fake_file, tmp_path / "output.mp4")

def test_validate_input_paths_directory_input(tmp_path):
    """Test validation fails when input path is a directory."""
    with pytest.raises(ValueError):
        _validate_input_paths(tmp_path, tmp_path / "output.mp4")

def test_validate_input_paths_output_directory_not_writable(tmp_path):
    """Test validation fails when output directory isn't writable."""
    read_only_dir = tmp_path / "readonly"
    read_only_dir.mkdir()
    read_only_dir.chmod(0o444)

    test_file = tmp_path / "test.mp4"
    test_file.touch()
    with pytest.raises(PermissionError):
        _validate_input_paths(test_file, read_only_dir / "output.mp4")

def test_upscale_video_invalid_scale_factor(tmp_path):
    """Test upscaling fails with invalid scale factor."""
    input_path = tmp_path / "input.mp4"
    input_path.touch()
    with pytest.raises(ValueError):
        upscale_video(input_path, tmp_path / "output.mp4", scale_factor=0.5)
