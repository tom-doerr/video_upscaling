"""Package setup configuration"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vidscale",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"vidscale": "vidscale"},
    package_data={"vidscale": ["py.typed"]},
    install_requires=["opencv-python>=4.5", "click>=8.0", "ffmpeg-python>=0.2"],
    entry_points={
        "console_scripts": ["vidscale=vidscale.cli:main"]
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Video upscaling toolkit with CLI interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vidscale",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
