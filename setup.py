from pathlib import Path
from setuptools import find_packages, setup

README = Path(__file__).with_name("README.md").read_text(encoding="utf-8")

setup(
    name="complexity-simulation",
    version="0.1.0",
    description="Computational life simulator inspired by Agüera y Arcas et al. (2024)",
    long_description=README,
    long_description_content_type="text/markdown",
    author="",
    python_requires=">=3.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pytest>=7.0.0",
        "tqdm>=4.62.0",
        "brotli>=1.0.9",
    ],
)
