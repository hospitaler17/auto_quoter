"""Package for auto_quoter source code.

Expose subpackages for easier imports, e.g. `from src import parser, github`.
"""

from . import github, parser  # re-export packages

__all__ = ["parser", "github"]
