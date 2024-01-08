# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
from pynext import __version__ as pynext_version

sys.path.append(os.path.abspath(".."))

project = "Pynext"
copyright = "2023, xXenvy"
author = "xXenvy"
release = pynext_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "sphinxext.opengraph",
    "sphinx_inline_tabs",
    "enum_tools.autoenum",
]
autodoc_typehints = "both"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}

ogp_site_name = "Pynext Documentation"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

default_dark_mode = True
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["style.css"]
