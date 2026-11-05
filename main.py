"""peforth 2.1.0"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from projectk import VM


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    vm = VM({"__file__dir__": str(HERE), "argv": list(args)})
    vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
