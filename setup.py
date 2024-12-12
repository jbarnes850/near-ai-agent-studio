from setuptools import setup, find_packages

setup(
    name="near-swarm",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "python-dotenv>=0.19.0",
        "near-api-py>=0.1.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.18.0",
        "pytest-cov>=3.0.0",
        "openai>=1.12.0",  # Required for async LLM provider interface
    ],
    extras_require={
        "dev": [
            "black",
            "flake8",
            "isort",
            "mypy",
        ]
    },
    entry_points={
        'console_scripts': [
            'near-swarm=near_swarm.core.cli:main',
        ],
    },
    python_requires=">=3.8",
    author="Jarrod Barnes",
    author_email="horizon@near.foundation",
    description="NEAR Protocol Swarm Intelligence Framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jbarnes850/near-swarm-intelligence",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 