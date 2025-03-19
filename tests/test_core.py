<<<<<<< HEAD
"""Unit tests for core video upscaling functionality."""

import pytest
from upscaler.core import upscale_video, _validate_input_paths  # pylint: disable=import-error

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
    with pytest.raises(ValueError):
        upscale_video(input_path, output_path, 0)

    # Test with existing invalid video file
    input_path.touch()
    with pytest.raises(ValueError, match="Failed to extract frames"):
        upscale_video(input_path, output_path, 2)


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
    assert mock_run.call_count == 4  # Includes ffmpeg check + 3 processing steps
=======
"""Unit tests for core video upscaling functionality."""

import pytest
from upscaler.core import upscale_video, _validate_input_paths  # pylint: disable=import-error

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
>>>>>>> task/please_create_a_minimal_video_upscaling_python_pac_20250318_194153
