"""Backward-compatible wrapper. Prefer: python3 scripts/build_municipality.py RJ"""

from build_municipality import main

if __name__ == "__main__":
    main(["RJ"])
