# ==============================================================================
# Acceso directo a suite de pruebas desde el directorio raíz tests/
# Reenvía la ejecución a app/tests/test_app.py
# ==============================================================================
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_TESTS_DIR = REPO_ROOT / "app" / "tests"

if str(APP_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(APP_TESTS_DIR))

from test_app import *  # noqa: F401, F403
