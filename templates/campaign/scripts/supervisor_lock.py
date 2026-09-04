"""Small cross-platform ownership lock for one campaign supervisor.

The lock file is persistent. Process ownership comes from an operating-system
lock held beyond its bounded JSON metadata; that content is diagnostics only. A crashed
process therefore releases ownership without anyone deleting or breaking a
possibly-live lock file.
"""
from __future__ import annotations

import datetime as _dt
import errno
import json
import os
import secrets
import socket
import stat
import sys
from pathlib import Path


SCHEMA = "physkit.supervisor-lock/v1"
MAX_METADATA_BYTES = 8192
LOCK_OFFSET = MAX_METADATA_BYTES + 1

class SupervisorLockError(RuntimeError):
    """The ownership lock could not be used safely."""


class SupervisorLockHeld(SupervisorLockError):
    """Another process currently owns the campaign supervisor lock."""

    def __init__(self, path: Path, owner: dict | None):
        self.path = path
        self.owner = owner
        super().__init__(f"campaign already has a live supervisor ({owner_summary(owner)}); "
                         f"lock: {path}")


def _utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def owner_summary(owner: dict | None) -> str:
    if not owner:
        return "owner metadata unavailable"
    fields = []
    for key in ("backend", "host", "pid", "started_utc"):
        value = owner.get(key)
        if value not in (None, ""):
            shown = "".join(ch if ch.isprintable() and ch not in "\r\n" else "?"
                            for ch in str(value))[:120]
            fields.append(f"{key}={shown}")
    return ", ".join(fields) or "owner metadata unavailable"


def backend_label(command: str) -> str:
    """Return a diagnostic provider label without selecting or changing the command."""
    stem = Path(command).stem.casefold()
    if stem.startswith("claude"):
        return "claude"
    if stem.startswith("codex"):
        return "codex"
    return f"custom:{stem or 'unknown'}"


def _read_metadata(fd: int) -> dict | None:
    try:
        os.lseek(fd, 0, os.SEEK_SET)
        raw = os.read(fd, MAX_METADATA_BYTES + 1)
        if len(raw) > MAX_METADATA_BYTES:
            return None
        value = json.loads(raw.decode("utf-8"))
        return value if isinstance(value, dict) else None
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _write_metadata(fd: int, value: dict) -> None:
    payload = (json.dumps(value, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > MAX_METADATA_BYTES:
        raise SupervisorLockError("supervisor-lock metadata exceeded its fixed size limit")
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    remaining = memoryview(payload)
    while remaining:
        written = os.write(fd, remaining)
        if written <= 0:
            raise SupervisorLockError("short write while publishing supervisor-lock metadata")
        remaining = remaining[written:]
    os.fsync(fd)


def _lock_fd(fd: int) -> None:
    os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
    if sys.platform == "win32":
        import msvcrt
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_fd(fd: int) -> None:
    os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
    if sys.platform == "win32":
        import msvcrt
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)


def _looks_held(exc: OSError) -> bool:
    return (exc.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK, errno.EWOULDBLOCK)
            or getattr(exc, "winerror", None) in (33, 36))


def _require_path_binding(fd: int, path: Path) -> os.stat_result:
    opened = os.fstat(fd)
    try:
        current = path.lstat()
    except OSError as exc:
        raise SupervisorLockError(f"supervisor lock changed while it was opened: {path}") from exc
    if not stat.S_ISREG(opened.st_mode) or not stat.S_ISREG(current.st_mode):
        raise SupervisorLockError(f"supervisor lock is not a regular file: {path}")
    if (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
        raise SupervisorLockError(f"supervisor lock changed while it was opened: {path}")
    return opened


class SupervisorLock:
    def __init__(self, path: Path, fd: int, metadata: dict):
        self.path = path
        self.fd = fd
        self.metadata = metadata

    def release(self) -> None:
        if self.fd < 0:
            return
        fd, self.fd = self.fd, -1
        try:
            current = _read_metadata(fd)
            if current and current.get("token") == self.metadata.get("token"):
                released = dict(self.metadata, state="released", released_utc=_utc_now())
                try:
                    _write_metadata(fd, released)
                except (OSError, SupervisorLockError):
                    pass
        finally:
            try:
                _unlock_fd(fd)
            except OSError:
                pass
            try:
                os.close(fd)
            except OSError:
                pass

    def __enter__(self) -> "SupervisorLock":
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.release()


def acquire(path: Path, *, backend: str) -> SupervisorLock:
    """Acquire *path* without waiting; raise ``SupervisorLockHeld`` if owned."""
    path = Path(path)
    try:
        before = path.lstat()
    except FileNotFoundError:
        before = None
    except OSError as exc:
        raise SupervisorLockError(f"cannot inspect supervisor lock {path}: {exc}") from exc
    if before is not None and not stat.S_ISREG(before.st_mode):
        raise SupervisorLockError(f"supervisor lock is not a regular file: {path}")

    flags = (os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
             | getattr(os, "O_NOFOLLOW", 0))
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise SupervisorLockError(f"cannot open supervisor lock {path}: {exc}") from exc
    try:
        os.set_inheritable(fd, False)
        opened = _require_path_binding(fd, path)
        if before is not None and (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino):
            raise SupervisorLockError(f"supervisor lock changed while it was opened: {path}")
        try:
            _lock_fd(fd)
        except OSError as exc:
            if _looks_held(exc):
                raise SupervisorLockHeld(path, _read_metadata(fd)) from exc
            raise SupervisorLockError(f"cannot lock supervisor file {path}: {exc}") from exc
        _require_path_binding(fd, path)

        metadata = {
            "schema": SCHEMA,
            "state": "owned",
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "backend": backend,
            "started_utc": _utc_now(),
            "token": secrets.token_hex(16),
        }
        try:
            _write_metadata(fd, metadata)
        except BaseException:
            try:
                _unlock_fd(fd)
            except OSError:
                pass
            raise
        return SupervisorLock(path, fd, metadata)
    except BaseException:
        try:
            os.close(fd)
        except OSError:
            pass
        raise
