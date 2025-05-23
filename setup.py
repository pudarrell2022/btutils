#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join("btutils", "__init__.py"), encoding="utf-8") as f:
    version = re.search(r'__version__ = [\'"]([^\'"]*)[\'"]', f.read()).group(1)

setup(
    name="btutils",
    version=version if version else "0.1.0",
    description="A lightweight Python library for backtesting analysis and visualization of trading strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Darrell",
    author_email="pudarrell@gmail.com",
    url="https://github.com/pudarrell2022/btutils",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.3.0",
        "pandas>=1.0.0",
        "scipy>=1.5.0",
        "seaborn>=0.11.0",
        "tabulate>=0.8.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="finance, trading, investing, backtesting, quantitative, analysis",
    license="MIT",
    project_urls={
        "Bug Reports": "https://github.com/pudarrell2022/btutils/issues",
        "Source": "https://github.com/pudarrell2022/btutils",
    },
)
