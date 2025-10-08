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
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

# Autodoc/Napoleon settings for clear, human-friendly API pages
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "inherited-members": True,
    "show-inheritance": True,
    "exclude-members": "with_traceback, add_note, args",
}
# include class and __init__ docstrings
autoclass_content = "both"
# keep methods/properties in the order they appear in the source
autodoc_member_order = "bysource"
# move type hints from signatures into the description for readability
autodoc_typehints = "description"

# Make Napoleon render NumPy/Google param & return sections nicely
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

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
html_logo = "_static/pkonfig_logo_2.png"
html_static_path = ["_static"]

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
# Strengthen the SEO title to include keyword and purpose
html_title = "PKonfig – Python configuration library (env, YAML, TOML, INI)"
# Base URL for canonical links on GitHub Pages (used by some crawlers)
html_baseurl = "https://ngladkikh.github.io/pkonfig/"
# Include extra static files like robots.txt
html_extra_path = ["_extra"]

# -- Autosummary options ------------------------------------------------------
autosummary_generate = True

# -- MyST configuration ------------------------------------------------------

myst_enable_extensions = [
    "linkify",
    "colon_fence",
]

# Suppress MyST header structure warnings (e.g., non-consecutive header levels)
suppress_warnings = [
    "myst.header",
]
