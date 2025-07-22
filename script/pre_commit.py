#!/usr/bin/env python3
import sys
from pathlib import Path

BANNED_WORDS = ["debug", "print(", "pdb.set_trace"]


def check_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            for word in BANNED_WORDS:
                if word in line:
                    print(f"❌ Mot interdit '{word}' trouvé dans {file_path}:{i}")
                    return True
    return False


def main():
    files = [Path(f) for f in sys.argv[1:] if f.endswith(".py")]
    failed = any(check_file(f) for f in files)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
