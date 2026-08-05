"""Textual full-screen conductor TUI (optional dependency).

Launch: PETSCII demoscene MOK-TUA splash → two-pane deck
  left  = intro (prompt arg or recommendations) + log
  right = system stats with VIC-II bars
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from tui import DEFAULT_SKIN, SKINS, resolve_skin, __version__
from tui.bridge import HELP_TEXT, boot_banner, resolve_command, run_cli
from tui.media import classify, media_status, play_external, render_image_preview
from tui.petscii import intro_recommendations, intro_with_prompt, loading_screen_text
from tui.stats_panel import format_stats_panel, sample_gpu_host, sample_local_cpu

THEMES_DIR = Path(__file__).resolve().parent / "themes"


def textual_available() -> bool:
    try:
        import textual  # noqa: F401

        return True
    except ImportError:
        return False


def build_app(
    skin: str = DEFAULT_SKIN,
    *,
    seed_prompt: str | None = None,
):
    """Return a MokTuaApp class instance. Raises ImportError if Textual missing."""
    from textual import work
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Input, RichLog, Static

    skin = resolve_skin(skin)
    css_name = skin if (THEMES_DIR / f"{skin}.tcss").is_file() else "c64"
    # aliases map to c64.tcss
    if skin in ("1980crt", "tui-c64-mode-default-1980crt-tui"):
        css_name = "c64"
    elif skin == "matrix":
        css_name = "green"
    elif skin == "paper":
        css_name = "mono"
    css_path = THEMES_DIR / f"{css_name}.tcss"

    class MokTuaApp(App[int]):
        """mok-tua conductor — doctor / providers / run / smoke over CLI."""

        CSS_PATH = str(css_path) if css_path.is_file() else None
        TITLE = "mok-tua"
        BINDINGS: ClassVar[list[Binding]] = [
            Binding("ctrl+c", "quit", "Quit", show=False),
            Binding("escape", "quit", "Quit", show=True),
            Binding("f1", "show_help", "Help", show=True),
            Binding("f5", "run_doctor", "Doctor", show=True),
            Binding("f6", "refresh_stats", "Stats", show=True),
        ]

        def __init__(
            self,
            skin_name: str = DEFAULT_SKIN,
            seed_prompt: str | None = None,
        ) -> None:
            super().__init__()
            self.skin_name = resolve_skin(skin_name)
            self.seed_prompt = (seed_prompt or "").strip() or None
            self._busy = False
            self._booting = True
            self._boot_step = 0
            self._last_receipt_line: str | None = None
            self._boot_timer = None

        def compose(self) -> ComposeResult:
            ver = __version__
            title = (
                f" **** MOK-TUA V{ver}  CONDUCTOR · SKIN={self.skin_name.upper()} ****"
                if self.skin_name in ("c64", "1980crt", "tui-c64-mode-default-1980crt-tui")
                else f"mok-tua conductor  v{ver}  ·  skin={self.skin_name}"
            )
            menu = (
                "[D]octor  [P]roviders  [R]un  [S]moke  [L]ock  [T]status  "
                "[M]onitor  [H]elp  [Q]uit  ·  show/play/receipt"
            )
            yield Static(title, id="chrome")
            yield Static(menu, id="menu")
            # Boot splash (full width) then replaced by panes via display toggle
            yield Static(loading_screen_text(ver, step=0), id="boot")
            with Horizontal(id="main-panes"):
                with Vertical(id="left-pane"):
                    yield RichLog(
                        id="log",
                        highlight=False,
                        markup=True,
                        wrap=True,
                        auto_scroll=True,
                    )
                with Vertical(id="right-pane"):
                    yield Static("loading stats…", id="stats")
            with Horizontal(id="prompt-row"):
                yield Static("READY.", id="ready")
                yield Input(
                    placeholder="type command or shortcut (H for help)…",
                    id="cmd",
                )
            yield Footer()

        def on_mount(self) -> None:
            # hide panes during boot
            try:
                self.query_one("#main-panes").styles.display = "none"
                self.query_one("#prompt-row").styles.display = "none"
            except Exception:
                pass
            self._boot_timer = self.set_interval(0.12, self._boot_tick, name="boot")

        def _boot_tick(self) -> None:
            if not self._booting:
                return
            self._boot_step += 1
            boot = self.query_one("#boot", Static)
            boot.update(loading_screen_text(__version__, step=self._boot_step))
            if self._boot_step >= 18:
                self._booting = False
                if self._boot_timer is not None:
                    try:
                        self._boot_timer.stop()
                    except Exception:
                        pass
                self._enter_deck()

        def _enter_deck(self) -> None:
            try:
                self.query_one("#boot").styles.display = "none"
                self.query_one("#main-panes").styles.display = "block"
                self.query_one("#prompt-row").styles.display = "block"
            except Exception:
                pass
            log = self.query_one("#log", RichLog)
            for line in boot_banner(self.skin_name, __version__).splitlines():
                log.write(line)
            log.write("")
            if self.seed_prompt:
                for line in intro_with_prompt(self.seed_prompt).splitlines():
                    log.write(line)
            else:
                for line in intro_recommendations().splitlines():
                    log.write(line)
            log.write("")
            log.write(media_status())
            log.write("[bold]READY.[/]")
            self._refresh_stats()
            self._stats_timer = self.set_interval(3.0, self._refresh_stats, name="stats")
            try:
                self.query_one("#cmd", Input).focus()
            except Exception:
                pass

        def _refresh_stats(self) -> None:
            try:
                panel = format_stats_panel(
                    gpu_sample=sample_gpu_host(),
                    local=sample_local_cpu(),
                    last_receipt_line=self._last_receipt_line,
                    skin=self.skin_name,
                )
                self.query_one("#stats", Static).update(panel)
            except Exception as exc:
                try:
                    self.query_one("#stats", Static).update(f"stats error: {exc}")
                except Exception:
                    pass

        def action_show_help(self) -> None:
            self._write_help()

        def action_run_doctor(self) -> None:
            if self._booting:
                return
            self._start_cli("doctor", ["doctor"])

        def action_refresh_stats(self) -> None:
            self._refresh_stats()

        def action_quit(self) -> None:
            self.exit(0)

        def _write_help(self) -> None:
            log = self.query_one("#log", RichLog)
            for line in HELP_TEXT.splitlines():
                log.write(line)

        def _set_ready(self, text: str = "READY.") -> None:
            self.query_one("#ready", Static).update(text)

        def on_input_submitted(self, event: Input.Submitted) -> None:
            if self._booting:
                return
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
            if name == "show":
                self._handle_show(argv or [])
                return
            if name == "play":
                self._handle_play(argv or [])
                return
            if name == "thumb":
                self._handle_show(argv or [], thumb=True)
                return
            assert argv is not None
            self._start_cli(name, argv)

        def _handle_show(self, argv: list[str], *, thumb: bool = False) -> None:
            log = self.query_one("#log", RichLog)
            if len(argv) < 2:
                log.write("[red]usage: show PATH | thumb PATH[/]")
                return
            path = Path(argv[1]).expanduser()
            if not path.is_file():
                log.write(f"[red]missing: {path}[/]")
                return
            kind = classify(path)
            if kind == "video":
                from tui.media import extract_video_thumb

                t = extract_video_thumb(path)
                if t:
                    path = t
                    log.write(f"[yellow]video thumb[/] {path.name}")
                else:
                    log.write("[yellow]no ffmpeg thumb — try: play PATH[/]")
                    return
            preview = render_image_preview(path, max_width=52 if not thumb else 28)
            log.write(f"[bold]SHOW[/] {path}")
            # RichLog markup: escape brackets from chafa/rich
            for line in preview.splitlines():
                safe = line.replace("[", "\\[")
                log.write(safe)
            log.write("[bold]READY.[/]")

        def _handle_play(self, argv: list[str]) -> None:
            log = self.query_one("#log", RichLog)
            if len(argv) < 2:
                log.write("[red]usage: play PATH[/]")
                return
            path = Path(argv[1]).expanduser()
            result = play_external(path)
            if result.get("ok"):
                log.write(f"[green]PLAY[/] {path} via {result.get('cmd')}")
            else:
                log.write(f"[red]play failed:[/] {result.get('error')}")
            log.write("[bold]READY.[/]")

        def _start_cli(self, name: str, argv: list[str]) -> None:
            log = self.query_one("#log", RichLog)
            log.write(f"[yellow]RUN {name.upper()}[/]  {' '.join(argv)}")
            self._busy = True
            self._set_ready("BUSY…")
            self.run_cli_worker(argv)

        @work(thread=True, exclusive=True)
        def run_cli_worker(self, argv: list[str]) -> None:
            rc, text = run_cli(argv)
            self.call_from_thread(self._show_cli_result, rc, text, argv)

        def _show_cli_result(self, rc: int, text: str, argv: list[str]) -> None:
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
            # try capture receipt caption if JSON-ish receipt in output
            if "caption_line" in text or "mok_tua_artifact_receipt" in text:
                for line in text.splitlines():
                    if "caption_line" in line or line.strip().startswith('"caption'):
                        self._last_receipt_line = line.strip()[:120]
                        break
            if argv and argv[0] == "receipt" and rc == 0:
                for line in text.splitlines():
                    if "caption_line" in line:
                        self._last_receipt_line = line.split(":", 1)[-1].strip().strip('",')
            log.write("")
            log.write("[bold]READY.[/]")
            self._refresh_stats()
            try:
                self.query_one("#cmd", Input).focus()
            except Exception:
                pass

    return MokTuaApp(skin_name=skin, seed_prompt=seed_prompt)


def run_textual(
    skin: str = DEFAULT_SKIN,
    *,
    seed_prompt: str | None = None,
) -> int:
    app = build_app(skin, seed_prompt=seed_prompt)
    result = app.run()
    return int(result) if result is not None else 0
