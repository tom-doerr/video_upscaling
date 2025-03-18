"""Package setup configuration"""

from setuptools import setup, find_packages

setup(
    name="vidscale",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["opencv-python", "click"],
    entry_points={"console_scripts": ["vidscale=vidscale.cli:main"]},
    python_requires=">=3.8",
)
