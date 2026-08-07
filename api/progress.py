"""Shared progress bus — uv-like bars in CLI, VIC-II bars in TUI."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ProgressEvent:
    id: str
    label: str
    frac: float | None = None  # 0..1 or None = indeterminate
    detail: str = ""
    done: bool = False
    failed: bool = False


ProgressCallback = Callable[[ProgressEvent], None]


def _clamp(frac: float | None) -> float | None:
    if frac is None:
        return None
    return max(0.0, min(1.0, float(frac)))


class ProgressBus:
    """Collect events; optionally drive rich.progress or plain stderr."""

    def __init__(self, *, enabled: bool = True, use_rich: bool = True) -> None:
        self.enabled = enabled
        self.events: list[ProgressEvent] = []
        self._callbacks: list[ProgressCallback] = []
        self._rich = None
        self._tasks: dict[str, Any] = {}
        if enabled and use_rich:
            try:
                from rich.progress import (
                    BarColumn,
                    Progress,
                    SpinnerColumn,
                    TaskProgressColumn,
                    TextColumn,
                    TimeElapsedColumn,
                )

                self._rich = Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(bar_width=28),
                    TaskProgressColumn(),
                    TimeElapsedColumn(),
                    TextColumn("[dim]{task.fields[detail]}"),
                    transient=False,
                )
                self._rich.start()
            except Exception:
                self._rich = None

    def add_callback(self, cb: ProgressCallback) -> None:
        self._callbacks.append(cb)

    def emit(self, event: ProgressEvent) -> None:
        event.frac = _clamp(event.frac)
        self.events.append(event)
        for cb in self._callbacks:
            try:
                cb(event)
            except Exception:
                pass
        if not self.enabled:
            return
        if self._rich is not None:
            if event.id not in self._tasks:
                total = 100 if event.frac is not None else None
                self._tasks[event.id] = self._rich.add_task(
                    event.label[:48], total=total, detail=event.detail[:40]
                )
            tid = self._tasks[event.id]
            if event.frac is not None:
                self._rich.update(
                    tid,
                    completed=int(event.frac * 100),
                    description=event.label[:48],
                    detail=(event.detail or "")[:40],
                )
            else:
                self._rich.update(
                    tid,
                    description=event.label[:48],
                    detail=(event.detail or "…")[:40],
                )
            if event.done or event.failed:
                self._rich.update(
                    tid,
                    completed=100 if event.done else 0,
                    detail=("done" if event.done else "FAIL")[:40],
                )
        else:
            # plain fallback
            if event.frac is None:
                bar = "░" * 20
                pct = "  ?"
            else:
                n = int(event.frac * 20)
                bar = "█" * n + "░" * (20 - n)
                pct = f"{int(event.frac * 100):3d}%"
            status = "DONE" if event.done else ("FAIL" if event.failed else "    ")
            line = f"\r[{bar}] {pct} {event.label[:32]:<32} {event.detail[:28]:<28} {status}"
            sys.stderr.write(line)
            if event.done or event.failed:
                sys.stderr.write("\n")
            sys.stderr.flush()

    def task(self, id: str, label: str, *, detail: str = "") -> None:
        self.emit(ProgressEvent(id=id, label=label, frac=0.0, detail=detail))

    def update(self, id: str, *, frac: float | None = None, detail: str = "", label: str | None = None) -> None:
        self.emit(
            ProgressEvent(
                id=id,
                label=label or id,
                frac=frac,
                detail=detail,
            )
        )

    def done(self, id: str, *, detail: str = "ok", label: str | None = None) -> None:
        self.emit(ProgressEvent(id=id, label=label or id, frac=1.0, detail=detail, done=True))

    def fail(self, id: str, *, detail: str = "error", label: str | None = None) -> None:
        self.emit(ProgressEvent(id=id, label=label or id, frac=None, detail=detail, failed=True))

    def close(self) -> None:
        if self._rich is not None:
            try:
                self._rich.stop()
            except Exception:
                pass
            self._rich = None


def vic_bar(frac: float | None, width: int = 16) -> str:
    if frac is None:
        return "░" * width
    n = int(max(0.0, min(1.0, frac)) * width)
    return "█" * n + "░" * (width - n)


def elapsed_spinner(t0: float, width: int = 8) -> str:
    frames = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    i = int((time.time() - t0) * 8) % len(frames)
    return frames[i] + " " + ("░" * (width - 2))
