project = "wpostgresql"
copyright = "2026, William Steve Rodriguez Villamizar"
author = "William Steve Rodriguez Villamizar"

release = "0.3.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_copybutton",
    "myst_parser",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

html_theme_options = {}

import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "psycopg": ("https://www.psycopg.org/psycopg3/docs/", None),
    "pydantic": ("https://docs.pydantic.dev/2/", None),
}

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = {
    "BaseModel": "pydantic.BaseModel",
}

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_input = True
