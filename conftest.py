import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

# Ensure both project root and src/ are importable
for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)
