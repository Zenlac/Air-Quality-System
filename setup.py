"""
Setup script for Air Pollution Forecasting System

Author: Air Quality Commission
Created: 2026-02-25
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Air Pollution Forecasting System"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="air-pollution-forecasting",
    version="1.0.0",
    author="Air Quality Commission",
    author_email="info@airquality.gov",
    description="Advanced air pollution forecasting system using Prophet and ARIMA models",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/airquality/air-pollution-forecasting",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Government",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.25.0",
            "notebook>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "air-pollution-forecast=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    keywords="air pollution, forecasting, time series, prophet, arima, environmental, aqi",
    project_urls={
        "Bug Reports": "https://github.com/airquality/air-pollution-forecasting/issues",
        "Source": "https://github.com/airquality/air-pollution-forecasting",
        "Documentation": "https://air-pollution-forecasting.readthedocs.io/",
    },
)
