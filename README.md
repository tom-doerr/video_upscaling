# VidScale - Video Upscaling Tool

A CLI tool for upscaling images and videos using bicubic interpolation.

## Features

- Upscale images (JPEG, PNG) by integer scale factors
- Upscale videos (MP4) while preserving original frame rate
- Preserve directory structure for output files
- Overwrite protection for existing files

## Installation

```bash
pip install vidscale
```

## Requirements

- Python 3.8+
- FFmpeg (for video processing)

## Usage

### Image Upscaling
```bash
vidscale image input.jpg output.jpg --scale 2
```

### Video Upscaling 
```bash
vidscale video input.mp4 output.mp4 --scale 2
```

## Options

- `--scale` - Scaling factor (integer >=1, default: 2)
- `--help` - Show help message for any command

## Examples

Upscale image by 3x:
```bash
vidscale image photo.jpg upscaled_photo.jpg --scale 3
```

Upscale video and create output directory:
```bash
vidscale video home_movie.mp4 upscaled/improved_movie.mp4 --scale 2
```

## Limitations

- Output quality depends on source material
- Video processing requires significant disk space for temporary frames
