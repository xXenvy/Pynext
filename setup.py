from setuptools import setup, find_packages
import codecs
import os

from pynext import pynext_version

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = pynext_version
DESCRIPTION = "Library that will allow you to manage selfbots."
LONG_DESCRIPTION = (
    "The library was written mainly for selfbots. "
    "It has a structure similar to popular libraries such as discord.py"
)

extras_require: dict[str, list[str]] = {
    "speed": ["orjson", "aiohttp[speedups]"],
}

setup(
    name="pynext",
    version=VERSION,
    author="xXenvy",
    author_email="<xpimpek01@gmail.com>",
    description=DESCRIPTION,
    license="MIT",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/xxenvy/pynext",
    project_urls={
        "Documentation": "https://pynext.readthedocs.io/en/latest/",
        "Issue tracker": "https://github.com//xxenvy/pynext/issues",
    },
    extras_require=extras_require,
    python_requires=">=3.9.0",
    packages=find_packages(),
    install_requires=["colorlog>=6.7.0", "aiohttp>=3.8.0"],
    keywords=[
        "python",
        "requests",
        "discord selfbot",
        "selfbot",
        "discord.py",
        "aiohttp",
        "nextcord",
        "pycord",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: AsyncIO",
        "Framework :: aiohttp",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Typing :: Typed",
    ],
)
