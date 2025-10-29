# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Epically Powerful'
copyright = '2025, EPIC Lab'
author = 'EPIC Lab'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.youtube',
    'sphinx.ext.napoleon',
    'sphinx_design',
    'sphinx_copybutton',
    'sphinx.ext.todo',
    'sphinxarg.ext',
    'sphinx_argparse_cli',
]

# Options for connecting other Sphinx projects
intersphinx_mapping = {
    'can': ('https://python-can.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3', None),
}

autodoc_mock_imports = ["mscl"]

source_suffix = ['.rst', '.md']
master_doc = 'index'

templates_path = ['_templates']
exclude_patterns = []

# MyST settings
myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
html_favicon = '_static/EPLogoCaps.png'


# Napoleon settings (for converting Google + NumPy docstrings to Sphinx format)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# SETTINGS FOR SPHINX RTD
# html_theme_options = {
#     "home_page_in_toc": False,
#     'collapse_navigation': False,
#     'style_nav_header_background': '#333333',
#     'sticky_navigation': True,
#     'navigation_depth': 3,
#     'titles_only': False,
#     'logo_only': True,
#     'display_version': True,
#     "sidebar_hide_name": True,
#     'style_nav_header_background': 'black' # Use this to change the nave bar background color (under logo)
# }

#SETTINGS FOR SPHINX MATERIAL THEME
# html_theme_options = {
#     'repo_url': 'https://github.com/gatech-epic-power/epically-powerful',
#     'repo_name': 'Epically Powerful',
#     'repo_type': 'github',
#     'nav_title': 'Epically Powerful',
#     'logo_icon': 'res/EPLogoCaps.png',
#     'globaltoc_depth': 3,
#     'color_primary': 'black',
#     'color_accent': 'grey',
#     'theme_navbar': 'dark',
#     'theme_sidebar': 'dark',
# }



# html_sidebars = {
#     "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
# }


# FURO
# html_theme_options = {
#     "light_css_variables": {
#         "color-brand-primary": "red",
#         "color-brand-content": "#CC3333",
#     },
# }

html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "#EA6432",
        "color-brand-content": "#EA6432",
    },
    "light_css_variables": {
        "color-brand-primary": "#B02317",
        "color-brand-content": "#B02317",
    },
}


html_title = 'Epically Powerful'
pygments_style = "manni"
pygments_dark_style = "gruvbox-dark"








copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}:"
copybutton_prompt_is_regexp = True

html_static_path = ['_static']
html_css_files = [
    'css-style.css',
]
htmlhelp_basename = 'SphinxwithMarkdowndoc'


# html_theme = 'flask'
#html_theme = 'sphinx_rtd_theme'
#html_theme = 'sphinx_material'
# html_theme = 'sphinx_book_theme'
# html_theme = 'furo'
# html_theme = 'pydata_sphinx_theme'
html_theme = 'furo'


if html_theme == 'pydata_sphinx_theme':
    html_logo = "res/EPLogoCaps.png"
else:
    html_logo = "res/EPLogoCaps.png"
