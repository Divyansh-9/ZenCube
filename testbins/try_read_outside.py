#!/usr/bin/env python3
"""Attempt to read /etc/hosts so the jail wrapper can flag a violation."""

from __future__ import annotations

import sys

TARGET = "/etc/hosts"


def main() -> int:
    try:
        with open(TARGET, "r", encoding="utf-8") as handle:
            data = handle.readline().strip()
        print(f"Read succeeded: {data}")
        return 0
    except Exception as exc:  # pragma: no cover - diagnostic path
        print(f"Read failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
