from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "1.0.2"
DESCRIPTION = "Library that will allow you to manage selfbots."
LONG_DESCRIPTION = (
    "The library was written mainly for selfbots. It has a structure similar to popular libraries such as discord.py"
)

setup(
    name="pynext",
    version=VERSION,
    author="xXenvy",
    author_email="<xpimpek01@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
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
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
)
