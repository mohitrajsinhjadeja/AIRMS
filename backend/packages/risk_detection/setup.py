from setuptools import setup, find_packages

setup(
    name="risk_detection",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "transformers>=4.0.0",
        "torch>=1.9.0",
        "tensorflow>=2.0.0",
        "spacy>=3.0.0",
        "regex>=2021.0.0",
        "python-jose[cryptography]>=3.3.0",
        "pydantic>=2.0.0",
        "fastapi>=0.68.0"
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.18.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'mypy>=0.900'
        ]
    },
    author="AIRMS Team",
    description="Risk detection module for AIRMS",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ]
)