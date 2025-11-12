#!/usr/bin/env python3
"""Development-friendly network restriction wrapper.

This module monkey-patches Python's socket interfaces to raise
``PermissionError`` whenever code attempts to open a network socket. It is
intended for dev-safe environments where seccomp or iptables cannot be applied
and is used via ``python3 -m monitor.net_wrapper -- <command ...>``.

Each blocked attempt is logged to ``monitor/logs/net_restrict_*.json`` so the
sandbox GUI and tests can audit behaviour without root access.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import runpy
import sys
import traceback
from typing import Any, Dict, List, Sequence

LOG_DIR = pathlib.Path(__file__).resolve().parent / "logs"
BLOCK_MESSAGE = "Network disabled by sandbox"


def _timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _safe_repr(value: Any, *, limit: int = 120) -> str:
    try:
        rendered = repr(value)
    except Exception as exc:  # pragma: no cover - defensive
        rendered = f"<repr-error {type(exc).__name__}>"
    if len(rendered) > limit:
        return f"{rendered[:limit]}…"
    return rendered


class NetRestrictionLogger:
    """Structured logger that records network violations to JSON."""

    def __init__(self, command: Sequence[str], log_dir: pathlib.Path) -> None:
        self._command = list(command)
        self._log_dir = log_dir
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._timestamp = _timestamp()
        self._path = self._log_dir / f"net_restrict_{self._timestamp}_{os.getpid()}.json"
        self._data: Dict[str, Any] = {
            "timestamp": self._timestamp,
            "pid": os.getpid(),
            "mode": "dev-safe",
            "command": self._command,
            "events": [],
            "event_count": 0,
            "status": "running",
            "exit_code": None,
        }
        self._write()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def record_violation(self, api: str, args: Sequence[Any], kwargs: Dict[str, Any]) -> None:
        event = {
            "timestamp": _timestamp(),
            "api": api,
            "args": [_safe_repr(arg) for arg in args],
            "kwargs": {key: _safe_repr(value) for key, value in kwargs.items()},
            "stack": traceback.format_stack(limit=6),
        }
        self._data["events"].append(event)
        self._data["event_count"] = len(self._data["events"])
        self._write()

    def record_exception(self, exc: BaseException) -> None:
        self._data["status"] = "exception"
        self._data["exception"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exception(exc),
        }
        self._write()

    def finalize(self, exit_code: int) -> None:
        self._data["status"] = "completed"
        self._data["exit_code"] = exit_code
        self._write()

    def _write(self) -> None:
        with self._path.open("w", encoding="utf-8") as handle:
            json.dump(self._data, handle, indent=2)
            handle.write("\n")


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a Python command with network access disabled via monkey-patching.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "--log-dir",
        default=str(LOG_DIR),
        help="Directory to write net_restrict JSON logs (default: monitor/logs)",
    )
    parser.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="Command to execute (use -- to separate wrapper options from the command)",
    )
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.error("Missing command. Use -- to separate wrapper options from the target command.")
    if args.cmd[0] == "--":
        args.cmd = args.cmd[1:]
    if not args.cmd:
        parser.error("Target command after -- is empty.")
    args.log_dir = pathlib.Path(args.log_dir).expanduser().resolve()
    return args


def _strip_python_launchers(command: Sequence[str]) -> List[str]:
    remaining = list(command)
    executable = os.path.realpath(sys.executable)
    seen: set[str] = {executable, os.path.basename(executable)}
    while remaining:
        head = remaining[0]
        head_base = os.path.basename(head)
        if head in seen or head_base.startswith("python"):
            remaining.pop(0)
            continue
        break
    return remaining


def normalise_target(command: Sequence[str]) -> tuple[str, str, List[str]]:
    stripped = _strip_python_launchers(command)
    if not stripped:
        raise ValueError("No Python entrypoint provided for network wrapper.")

    head, *tail = stripped
    if head == "-m":
        if not tail:
            raise ValueError("-m provided without module name.")
        module = tail[0]
        return ("module", module, tail[1:])
    if head == "-c":
        raise ValueError("-c is not supported by net_wrapper (cannot safely evaluate).")

    return ("script", head, tail)


def patch_sockets(logger: NetRestrictionLogger) -> None:
    import socket

    original_socket = socket.socket
    original_create_connection = socket.create_connection
    original_socketpair = getattr(socket, "socketpair", None)
    original_fromfd = getattr(socket, "fromfd", None)

    def _block(api_name: str, *args: Any, **kwargs: Any) -> None:
        logger.record_violation(api_name, args, kwargs)
        raise PermissionError(BLOCK_MESSAGE)

    def blocked_socket(*args: Any, **kwargs: Any):  # type: ignore[override]
        _block("socket.socket", *args, **kwargs)

    def blocked_create_connection(*args: Any, **kwargs: Any):  # type: ignore[override]
        _block("socket.create_connection", *args, **kwargs)

    socket.socket = blocked_socket  # type: ignore[assignment]
    socket.create_connection = blocked_create_connection  # type: ignore[assignment]

    if original_socketpair is not None:
        def blocked_socketpair(*args: Any, **kwargs: Any):  # type: ignore[override]
            _block("socket.socketpair", *args, **kwargs)

        socket.socketpair = blocked_socketpair  # type: ignore[assignment]

    if original_fromfd is not None:
        def blocked_fromfd(*args: Any, **kwargs: Any):  # type: ignore[override]
            _block("socket.fromfd", *args, **kwargs)

        socket.fromfd = blocked_fromfd  # type: ignore[assignment]

    # Ensure lower level module coatings respect the block as well.
    try:
        import _socket  # type: ignore
    except ImportError:  # pragma: no cover - some platforms omit the module name
        _socket = None  # type: ignore
    if _socket is not None:
        setattr(_socket, "socket", blocked_socket)

    os.environ["ZENCUBE_NET_DISABLED"] = "1"
    # Disable distro-provided excepthook (apport) to avoid recursive socket usage.
    try:
        sys.excepthook = sys.__excepthook__
    except AttributeError:  # pragma: no cover - extremely rare
        pass


def run_target(command: Sequence[str], logger: NetRestrictionLogger) -> None:
    entry_type, entry, tail = normalise_target(command)

    if entry_type == "module":
        sys.argv = [entry, *tail]
        runpy.run_module(entry, run_name="__main__", alter_sys=True)
    else:
        script_path = pathlib.Path(entry)
        if not script_path.exists():
            raise FileNotFoundError(f"Target script not found: {script_path}")
        sys.argv = [str(script_path), *tail]
        runpy.run_path(str(script_path), run_name="__main__")


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    logger = NetRestrictionLogger(args.cmd, args.log_dir)
    patch_sockets(logger)

    try:
        run_target(args.cmd, logger)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        logger.finalize(code)
        raise
    except BaseException as exc:  # pragma: no cover - surfaced to caller
        logger.record_exception(exc)
        logger.finalize(1)
        raise
    else:
        logger.finalize(0)
        return 0


if __name__ == "__main__":
    sys.exit(main())
