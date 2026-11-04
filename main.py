"""peforth 2.1.0"""

from pathlib import Path
from projectk import VM

HERE = Path(__file__).resolve().parent


def main():
    vm = VM({"__file__dir__": str(HERE)})
    vm.dictate((HERE / "init.f").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
