# Configuration file for the Sphinx documentation builder.
#
# Minimal Sphinx config tailored for PKonfig.

import os
import sys
from datetime import datetime

# -- Path setup --------------------------------------------------------------

# Add project root to sys.path for autodoc (if needed later)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# -- Project information -----------------------------------------------------

project = "PKonfig"
author = "Nikita Gladkikh"
current_year = str(datetime.now().year)
copyright = f"{current_year}, {author}"

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Support both .rst and .md (MyST) files
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
html_title = "PKonfig Documentation"

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "linkify",
]
