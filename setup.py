"""Package configuration for video upscaling tool.

The package provides spatial resolution enhancement through various
interpolation methods using OpenCV's optimized algorithms.
"""

from pathlib import Path
from setuptools import setup, find_packages

setup(
    name="upscaler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "opencv-python-headless",
    ],
    entry_points={
        "console_scripts": [
            "upscale-video=upscaler.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Video Upscaler Maintainers",
    author_email="maintainers@vidupscale.example",
    description="High-quality video upscaling with multiple interpolation algorithms",
    long_description=(
        Path("README.md").read_text(encoding="utf-8")
        if Path("README.md").exists()
        else ""
    ),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/video-upscaler",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
