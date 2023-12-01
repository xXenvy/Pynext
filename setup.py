from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "1.0.3"
DESCRIPTION = "Library that will allow you to manage selfbots."
LONG_DESCRIPTION = (
    "The library was written mainly for selfbots. It has a structure similar to popular libraries such as discord.py"
)

extras_require = {
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
    extras_require=extras_require,
    python_requires=">=3.9.0",
    packages=find_packages(),
    install_requires=["colorlog", "aiohttp"],
    keywords=[
        "python",
        "requests",
        "discord selfbot",
        "selfbot",
        "discord.py",
        "aiohttp",
        "nextcord",
        "pycord"
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
        "Typing :: Typed"
    ],
)
