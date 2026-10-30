import sys
import types
from pathlib import Path

_backend_dir = Path(__file__).resolve().parent
_parent_dir = _backend_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

if "backend" not in sys.modules:
    backend_pkg = types.ModuleType("backend")
    backend_pkg.__path__ = [str(_backend_dir)]
    sys.modules["backend"] = backend_pkg

from .app import create_api_app, app

__all__ = ["create_api_app", "app"]
