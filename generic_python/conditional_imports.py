from __future__ import annotations

import sys

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    pass
else:  # pragma: <3.11 cover
    pass

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    pass
