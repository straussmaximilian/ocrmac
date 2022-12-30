#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("HISTORY.md") as history_file:
    history = history_file.read()

requirements = ["Click>=7.0", "pyobjc-framework-Vision", "pillow"]

test_requirements = [
    "pytest>=3",
]

setup(
    author="Maximilian Strauss",
    author_email="straussmaximilian@gmail.com",
    python_requires=">=3.6",
    
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="A python wrapper to extract text from images on a mac system. Uses the vision framework from Apple.",
    entry_points={
        "console_scripts": [
            "ocrmac=ocrmac.cli:main",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="ocrmac",
    name="ocrmac",
    packages=find_packages(include=["ocrmac", "ocrmac.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/straussmaximilian/ocrmac",
    version="0.1.0",
    zip_safe=False,
)
