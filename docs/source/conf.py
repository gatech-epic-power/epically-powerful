# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'EPICallyPoWeRful'
copyright = '2025, EPIC Lab'
author = 'EPIC Lab'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.youtube',
    'sphinx.ext.napoleon',
    'sphinx_design',
    'sphinx_copybutton',

]

# Options for connecting other Sphinx projects
intersphinx_mapping = {
    'can': ('https://python-can.readthedocs.io/en/stable/', None),
    'python': ('https://docs.python.org/3', None),
}

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

html_theme_options = {
    "home_page_in_toc": False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'titles_only': False,
    'logo_only': True,
    'display_version': False,
    "sidebar_hide_name": True,
    'style_nav_header_background': '#bcc7cf'
}

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}:"
copybutton_prompt_is_regexp = True

html_static_path = ['_static']
html_css_files = [
    'css-style.css',
]
htmlhelp_basename = 'SphinxwithMarkdowndoc'


# html_theme = 'flask'
html_theme = 'sphinx_rtd_theme'
# html_theme = 'sphinx_book_theme'
# html_theme = 'furo'
# html_theme = 'pydata_sphinx_theme'

if html_theme == 'pydata_sphinx_theme':
    html_logo = "res/EPICally_PoWeRful_Logo_FLAT.png"
else:
    html_logo = "res/EPICally_PoWeRful_Logo.png"
