"""Routers package initializer.

Keep this file minimal so `from routers import ...` and direct submodule imports work
consistently when the app is started from different current working directories.
"""

__all__ = ["auth", "forum", "profile"]
from routers import auth, forum, profile
