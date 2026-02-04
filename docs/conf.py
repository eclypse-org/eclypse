# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys
from datetime import datetime
from importlib import import_module
from importlib.metadata import distribution

from jinja2.filters import FILTERS

sys.path.insert(0, os.path.abspath(".."))

# # -- Core package import -----------------------------------------------------
# core_dist = distribution("eclypse-core")
# core_path = os.path.join(core_dist.locate_file("."), "eclypse_core-stubs")
# print("Including", core_path)
# sys.path.insert(0, core_path)


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = "ECLYPSE"
author = "Valerio De Caro & Jacopo Massa"
copyright = f"{(datetime.now().year)}, {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # "enum_tools.autoenum",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinxcontrib.icon",
    "sphinx_copybutton",
    "sphinx_favicon",
    "sphinx_design",
    "myst_parser",
]
viewcode_follow_imported_members = True
autosummary_generate = True
myst_enable_extensions = ["colon_fence"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

coverage_show_missing_items = True
# Automatically extract typehints when specified and place them in
# descriptions of the relevant function/method.
autodoc_typehints = "description"
autodoc_member_order = "bysource"
# Don't show class signature with the class' name.
autodoc_class_signature = "separated"

autodoc_default_options = {"undoc-members": True}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_logo = "_static/images/light.png"

html_static_path = ["_static"]
html_extra_path = ["_static/landing"]
html_css_files = ["css/home.css"]  # ["css/custom.css", "css/landing.css"]
html_js_files = ["js/custom.js"]

html_context = {
    "github_url": "https://github.com",
    "github_user": "eclypse-org",
    "github_repo": "eclypse",
    "github_version": "main",
    "doc_path": "docs",
}

html_additional_pages = {"index": "index.html"}

# external_links = [
#     {
#         "name": "Changelog",
#         "url": "https://github.com/eclypse-org/eclypse/blob/main/CHANGELOG.md",
#     }
# ]

favicons = [
    {
        "rel": "icon",
        "sizes": "16x16",
        "href": "favicon/favicon-16x16.png",
    },
    {
        "rel": "icon",
        "sizes": "32x32",
        "href": "favicon/favicon-32x32.png",
    },
    {
        "rel": "apple-touch-icon",
        "sizes": "180x180",
        "href": "favicon/apple-touch-icon.png",
        "color": "#000000",
    },
    {
        "rel": "android-chrome",
        "sizes": "192x192",
        "href": "favicon/android-chrome-192x192.png",
    },
    {
        "rel": "android-chrome",
        "sizes": "512x512",
        "href": "favicon/android-chrome-512x512.png",
    },
    {
        "rel": "manifest",
        "href": "favicon/site.webmanifest",
    },
    {
        "rel": "shortcut icon",
        "href": "favicon/favicon.ico",
    },
]

icon_links = [
    {
        "name": "GitHub",
        "url": "https://github.com/eclypse-org/eclypse",
        "icon": "fa-brands fa-github",
        "type": "fontawesome",
    }
]

html_theme_options = {
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "navbar_persistent": ["search-button-field"],
    "navbar_align": "left",
    "secondary_sidebar_items": ["page-toc", "edit-this-page"],
    "footer_start": ["last-updated", "copyright"],
    "footer_center": ["sphinx-version"],
    "footer_end": ["theme-version"],
    "show_nav_level": 1,
    "navigation_depth": 4,
    "icon_links": icon_links,
    # "external_links": external_links,
    "header_links_before_dropdown": 4,
    "logo": {
        "text": "ECLYPSE",
        "alt_text": "ECLYPSE - Home",
        "image_dark": "_static/images/dark.png",
        "image_light": "_static/images/light.png",
    },
}
source_suffix = [".rst", ".pyi"]
html_sidebars = {"**": ["sidebar-nav-bs", "sidebar-ethical-ads"]}

html_scaled_image_link = False


def filter_out_undoc_class_members(member_name, class_name, module_name):
    module = import_module(module_name)
    cls = getattr(module, class_name)
    if getattr(cls, member_name).__doc__:
        return f"~{class_name}.{member_name}"
    else:
        return ""


def filter_out_parent_class_members(member_name, class_name, module_name):
    module = import_module(module_name)
    cls = getattr(module, class_name)
    if member_name in cls.__dict__:
        return f"~{class_name}.{member_name}"
    else:
        return ""


FILTERS["filter_out_undoc_class_members"] = filter_out_undoc_class_members
FILTERS["filter_out_parent_class_members"] = filter_out_parent_class_members
