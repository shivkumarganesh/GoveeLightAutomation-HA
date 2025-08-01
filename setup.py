"""Setup script for Govee Light Automation Integration."""

from setuptools import setup, find_packages

setup(
    name="home-assistant-govee-light-automation",
    version="1.0.0",
    description="Govee Light Automation Integration for Home Assistant",
    author="Shiv Kumar Ganesh",
    author_email="gshiv.sk@gmail.com",
    url="https://github.com/shivkumarganesh/home-assistant-govee-integration",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "voluptuous>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.18.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 