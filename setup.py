"""Package configuration for video upscaling tool."""

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
)
