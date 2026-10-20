from setuptools import setup, find_packages

setup(
    name="croctech",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pydantic>=2.0.0",
        "click>=8.0.0",
        "rich>=12.0.0",
        "Flask>=2.2.0",
        "pymupdf>=1.20.0",
        "pytest>=7.0.0",
    ],
    entry_points={
        "console_scripts": [
            "croctech=croctech.cli:cli",
        ],
    },
)

