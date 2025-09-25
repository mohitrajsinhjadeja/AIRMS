from setuptools import setup, find_namespace_packages

setup(
    name="risk_detection",
    version="1.0.0",
    packages=find_namespace_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.1.0",
        "fastapi>=0.68.0",
    ],
    python_requires=">=3.8",
)