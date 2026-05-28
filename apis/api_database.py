"""
Shared database connection for ACTORS APIs.

Import and call `get_api_store()` from any API module to obtain the
singleton APIStore instance.  Initialisation is lazy – the database
file is only opened on the first call.
"""

import sys
from pathlib import Path

# Allow imports from the repo root when this file is loaded from apis/
sys.path.append(str(Path(__file__).parent.parent))

from database.api_store import APIStore
from database.config import L2Config

_api_store: APIStore = None


def get_api_store() -> APIStore:
    """Return the singleton APIStore, creating it on first call."""
    global _api_store
    if _api_store is None:
        _api_store = APIStore(L2Config())
    return _api_store
