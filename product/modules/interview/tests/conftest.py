import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_MODULES = _HERE.parents[1]
for p in (_MODULES, _HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
