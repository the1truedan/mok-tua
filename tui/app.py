"""Textual full-screen conductor TUI (optional dependency)."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from tui import DEFAULT_SKIN, SKINS, __version__
from tui.bridge import HELP_TEXT, boot_banner, resolve_command, run_cli

THEMES_DIR = Path(__file__).resolve().parent / "themes"


def textual_available() -> bool:
    try:
        import textual  # noqa: F401

        return True
    except ImportError:
        return False


def build_app(skin: str = DEFAULT_SKIN):
    """Return a MokTuaApp class instance. Raises ImportError if Textual missing."""
    from textual import work
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Input, RichLog, Static

    if skin not in SKINS:
        skin = DEFAULT_SKIN

    css_path = THEMES_DIR / f"{skin}.tcss"

    class MokTuaApp(App[int]):
        """mok-tua conductor — doctor / providers / run / smoke over CLI."""

        CSS_PATH = str(css_path) if css_path.is_file() else None
        TITLE = "mok-tua"
        BINDINGS: ClassVar[list[Binding]] = [
            Binding("ctrl+c", "quit", "Quit", show=False),
            Binding("escape", "quit", "Quit", show=True),
            Binding("f1", "show_help", "Help", show=True),
            Binding("f5", "run_doctor", "Doctor", show=True),
        ]

        def __init__(self, skin_name: str = DEFAULT_SKIN) -> None:
            super().__init__()
            self.skin_name = skin_name if skin_name in SKINS else DEFAULT_SKIN
            self._busy = False

        def compose(self) -> ComposeResult:
            ver = __version__
            title = (
                f" **** MOK-TUA V{ver}  CONDUCTOR · SKIN={self.skin_name.upper()} ****"
                if self.skin_name == "c64"
                else f"mok-tua conductor  v{ver}  ·  skin={self.skin_name}"
            )
            menu = (
                "[D]octor  [P]roviders  [R]un  [S]moke  [L]ock  [T]status  [H]elp  [Q]uit"
            )
            yield Static(title, id="chrome")
            yield Static(menu, id="menu")
            with Vertical():
                yield RichLog(
                    id="log",
                    highlight=False,
                    markup=True,
                    wrap=True,
                    auto_scroll=True,
                )
            with Horizontal(id="prompt-row"):
                yield Static("READY.", id="ready")
                yield Input(
                    placeholder="type command or shortcut (H for help)…",
                    id="cmd",
                )
            yield Footer()

        def on_mount(self) -> None:
            log = self.query_one("#log", RichLog)
            for line in boot_banner(self.skin_name, __version__).splitlines():
                log.write(line)
            self.query_one("#cmd", Input).focus()

        def action_show_help(self) -> None:
            self._write_help()

        def action_run_doctor(self) -> None:
            self._start_cli("doctor", ["doctor"])

        def action_quit(self) -> None:
            self.exit(0)

        def _write_help(self) -> None:
            log = self.query_one("#log", RichLog)
            for line in HELP_TEXT.splitlines():
                log.write(line)

        def _set_ready(self, text: str = "READY.") -> None:
            self.query_one("#ready", Static).update(text)

        def on_input_submitted(self, event: Input.Submitted) -> None:
            line = event.value
            event.input.value = ""
            if self._busy:
                self.query_one("#log", RichLog).write("[dim]busy — wait for READY.[/]")
                return
            name, argv, err = resolve_command(line)
            if not name:
                return
            if err:
                self.query_one("#log", RichLog).write(f"[red]{err}[/]")
                return
            if name == "quit":
                self.exit(0)
                return
            if name == "help":
                self._write_help()
                return
            assert argv is not None
            self._start_cli(name, argv)

        def _start_cli(self, name: str, argv: list[str]) -> None:
            log = self.query_one("#log", RichLog)
            log.write(f"[yellow]RUN {name.upper()}[/]  {' '.join(argv)}")
            self._busy = True
            self._set_ready("BUSY…")
            self.run_cli_worker(argv)

        @work(thread=True, exclusive=True)
        def run_cli_worker(self, argv: list[str]) -> None:
            rc, text = run_cli(argv)
            self.call_from_thread(self._show_cli_result, rc, text)

        def _show_cli_result(self, rc: int, text: str) -> None:
            self._busy = False
            self._set_ready("READY.")
            log = self.query_one("#log", RichLog)
            color = "green" if rc == 0 else "red"
            lines = text.splitlines()
            if len(lines) > 120:
                lines = lines[:120] + [f"… ({len(text.splitlines()) - 120} more)"]
            for line in lines or ["(no output)"]:
                safe = line.replace("[", "\\[")
                log.write(f"[{color}]{safe}[/]")
            log.write("")
            log.write("[bold]READY.[/]")
            try:
                self.query_one("#cmd", Input).focus()
            except Exception:
                pass

    return MokTuaApp(skin_name=skin)


def run_textual(skin: str = DEFAULT_SKIN) -> int:
    app = build_app(skin)
    result = app.run()
    return int(result) if result is not None else 0
