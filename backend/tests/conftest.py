import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent

for path in (BACKEND_DIR, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
