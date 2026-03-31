project = "wpostgresql"
copyright = "2026, William Steve Rodriguez Villamizar"
author = "William Steve Rodriguez Villamizar"

release = "0.3.0"
version = "0.3.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_tabs.tabs",
    "sphinxcontrib.mermaid",
    "sphinx.ext.todo",
    "sphinx.ext.autosummary",
    "sphinx.ext.duration",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "logo": {"text": "wpostgresql"},
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/wisrovi/wpostgresql",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/wpostgresql/",
            "icon": "fa-brands fa-python",
        },
        {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/in/william-rodriguez-villamizar-572302207",
            "icon": "fa-brands fa-linkedin",
        },
    ],
    "github_url": "https://github.com/wisrovi/wpostgresql",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "repository_url": "https://github.com/wisrovi/wpostgresql",
    "repository_branch": "main",
    "path_to_docs": "docs",
    "show_navbar_depth": 3,
    "show_toc_level": 3,
    "navbar_align": "left",
    "announcement": "🚀 New version 0.3.0 released with async support and bulk operations!",
}

# Custom sidebar templates
html_sidebars = {
    "**": ["navbar-logo.html", "icon-links.html", "search-field.html", "sbt-sidebar-nav.html"]
}

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# -- Options for intersphinx -------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "psycopg": ("https://www.psycopg.org/psycopg3/docs/", None),
    "pydantic": ("https://docs.pydantic.dev/2/", None),
    "sqlalchemy": ("https://docs.sqlalchemy.org/en/20/", None),
}

# -- Options for Napoleon (Google/NumPy docstrings) -------------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = {
    "BaseModel": "pydantic.BaseModel",
    "Connection": "psycopg.Connection",
    "AsyncConnection": "psycopg.AsyncConnection",
}

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
    "member-order": "alphabetical",
    "exclude-members": "__weakref__",
}
autodoc_mock_imports = []
autodoc_typehints = "description"
autodoc_typehints_format = "short"
autosummary_generate = True

# -- Options for copybutton -------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_input = True
copybutton_exclude = "doctest"

# -- Options for mermaid ----------------------------------------------------
mermaid_output_format = "svg"
mermaid_init_js = """{startOnLoad: true}"""

# -- Options for sphinx-tabs ------------------------------------------------
sphinx_tabs_disable_tab_title = False
sphinx_tabs_valid_builders = ["html"]

# -- Options for todo -------------------------------------------------------
todo_include_todos = True
todo_link_only = True

# -- Options for myst-parser ------------------------------------------------
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_heading_anchors = 3
myst_footnote_transition = True
myst_dmath_double_inline = True

# -- Options for HTML output ------------------------------------------------
html_title = "wpostgresql Documentation"
html_short_title = "wpostgresql"
html_show_sourcelink = True
html_show_sphinx = False
html_show_copyright = True

# Add any custom templates here
html_context = {
    "default_mode": "light",
}

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "11pt",
    "preamble": r"""
\usepackage{charter}
\usepackage[characterencodings=unicode]{hyperref}
""",
}

# -- Options for manual page output ------------------------------------------
man_pages = [
    ("index", "wpostgresql", "wpostgresql Documentation", ["William Steve Rodriguez Villamizar"], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (
        "index",
        "wpostgresql",
        "wpostgresql Documentation",
        "William Steve Rodriguez Villamizar",
        "wpostgresql",
        "High-performance, type-safe PostgreSQL ORM with Pydantic integration.",
        "Miscellaneous",
    ),
]
