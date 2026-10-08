#!/usr/bin/env python3
"""Codex-only selection, argv, stdin, JSONL, and provenance perimeter for the campaign driver."""
from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

BACKENDS = ("auto", "claude", "codex", "custom")
CODEX_EFFORTS = ("minimal", "low", "medium", "high", "xhigh")
CLAUDE_EFFORTS = ("low", "medium", "high", "xhigh", "max")
class BackendError(RuntimeError): pass
@dataclass(frozen=True)
class Selection:
    name: str
    executable: str = ""
    version: str = ""
@dataclass(frozen=True)
class SpawnSpec:
    argv: list[str]
    prompt: str
def _choice(value, source: str) -> str | None:
    if value is None or not str(value).strip():
        return None
    choice = str(value).strip().lower()
    if choice not in BACKENDS:
        raise BackendError(f"{source} is {value!r}; expected one of: {', '.join(BACKENDS)}")
    return choice

def _configured_choice(loop_cfg: Path) -> tuple[str | None, bool]:
    try:
        src = json.loads(loop_cfg.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None, False
    if not isinstance(src, dict):
        return None, False
    driver = src.get("driver") or {}
    if not isinstance(driver, dict) or "backend" not in driver:
        return None, False
    return _choice(driver.get("backend"), "configs/loop.json driver.backend"), True

def _probe(executable: str) -> tuple[str | None, str]:
    try:
        proc = subprocess.run([executable, "--version"], capture_output=True, text=True,
                              timeout=30, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, str(exc)
    output = "\n".join(part.strip() for part in (proc.stdout, proc.stderr) if part and part.strip())
    if proc.returncode != 0:
        return None, output or f"exit {proc.returncode}"
    return (output.splitlines()[0] if output else "responds"), ""

def _codex_executable() -> tuple[str | None, str]:
    requested = os.environ.get("AUTORESEARCH_CODEX_EXE")
    candidate = requested or shutil.which("codex")
    if not candidate:
        return None, "not found on PATH"
    path = Path(candidate).expanduser()
    if not path.is_absolute():
        resolved = shutil.which(str(path))
        if not resolved:
            return None, f"could not resolve {candidate!r}"
        path = Path(resolved)
    try:
        absolute = str(path.resolve(strict=True))
    except OSError as exc:
        return None, str(exc)
    version, error = _probe(absolute)
    if version is None:
        hint = (" Set AUTORESEARCH_CODEX_EXE to the absolute codex executable; WindowsApps aliases "
                "may be inaccessible to a supervised process.")
        return None, error + hint
    return absolute, version

def _auto_selection() -> Selection:
    available = []
    claude = shutil.which("claude")
    if claude:
        version, _ = _probe(claude)
        if version:
            available.append(Selection("claude"))
    codex, version = _codex_executable()
    if codex:
        available.append(Selection("codex", codex, version))
    if len(available) == 1:
        return available[0]
    names = ", ".join(item.name for item in available) or "none"
    raise BackendError("backend=auto requires exactly one working supported CLI, but found " + names
                       + ". Select --backend claude|codex (or set driver.backend).")

def configure(loop_cfg: Path, cli_choice: str | None = None) -> Selection:
    """Resolve CLI -> config -> environment; a loop.json without a driver.backend field selects Claude."""
    cli = _choice(cli_choice, "--backend")
    configured, field_present = _configured_choice(loop_cfg)
    environment = _choice(os.environ.get("AUTORESEARCH_BACKEND"), "AUTORESEARCH_BACKEND")
    if cli is not None:
        selected = cli
    elif configured not in (None, "auto"):
        selected = configured
    elif environment is not None:
        selected = environment
    elif os.environ.get("AUTORESEARCH_AGENT_CMD"):
        selected = "custom"
    elif not field_present:
        selected = "claude"  # a loop.json with no driver.backend field means claude
    else:
        selected = configured or "auto"
    if selected == "auto":
        return _auto_selection()
    if selected == "custom":
        if not os.environ.get("AUTORESEARCH_AGENT_CMD"):
            raise BackendError("backend=custom requires AUTORESEARCH_AGENT_CMD")
        return Selection("custom")
    if selected == "codex":
        executable, version = _codex_executable()
        if not executable:
            raise BackendError("Codex CLI is unavailable: " + version)
        return Selection("codex", executable, version)
    return Selection("claude")

def configure_or_exit(loop_cfg: Path, cli_choice: str | None = None) -> Selection:
    try:
        return configure(loop_cfg, cli_choice)
    except BackendError as exc:
        raise SystemExit(f"backend selection: {exc}") from exc

def model_for(section: dict, selection: Selection) -> str:
    if selection.name != "codex":
        return section.get("model", "")
    if not isinstance(section, dict):
        raise BackendError(f"model section must be an object, got {type(section).__name__}")
    value = section.get("codex_model", "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise BackendError(f"{selection.name} model must be a string, got {type(value).__name__}")
    value = value.strip()
    if any(mark in value.lower() for mark in ("claude", "opus", "sonnet", "haiku")):
        raise BackendError(f"Codex cannot use Claude model {value!r}; set the role's codex_model or leave it blank")
    return value

def model_errors(loop_cfg: dict, selection: Selection) -> list[str]:
    errors = []
    for role in ("worker", "verifier"):
        try:
            section = loop_cfg.get(role) or {}
            model_for(section, selection)
            effort_for(section, selection)
        except BackendError as exc:
            errors.append(f"configs/loop.json {role} {selection.name} launch setting is unusable ({exc}).")
    return errors

def effort_for(section: dict, selection: Selection) -> str:
    if not isinstance(section, dict):
        raise BackendError(f"effort section must be an object, got {type(section).__name__}")
    if selection.name == "codex":
        key, allowed = "codex_reasoning_effort", CODEX_EFFORTS
    elif selection.name == "claude":
        key, allowed = "claude_effort", CLAUDE_EFFORTS
    else:
        return ""
    value = section.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise BackendError(f"{selection.name} effort must be a string, got {type(value).__name__}")
    value = value.strip().lower()
    if value and value not in allowed:
        raise BackendError(f"{selection.name} effort is {value!r}; expected blank or one of: "
                           + ", ".join(allowed))
    return value

def _in_git_tree(root: Path) -> bool:
    return any((parent / ".git").exists() for parent in (root, *root.parents))

def adapt_prompt(prompt: str) -> str:
    prefix, marker, delivered = prompt.partition("\n\n== STANDING CONSTRAINTS")
    prefix = prefix.replace("CLAUDE.md auto-loads", "AGENTS.md auto-loads").replace("/physkit:", "physkit:")
    return prefix + marker + delivered

def is_codex(selection: Selection | None) -> bool:
    return bool(selection and selection.name == "codex")

def spawn_spec(root: Path, selection: Selection, model: str, prompt: str, effort: str = "") -> SpawnSpec:
    if selection.name != "codex" or not selection.executable:
        raise BackendError("Codex spawn requested without a configured Codex backend")
    argv = [selection.executable, "exec", "--sandbox", "workspace-write"]
    if not _in_git_tree(root):
        argv.append("--skip-git-repo-check")
    argv.append("--json")
    if model:
        argv.extend(("--model", model))
    if effort:
        argv.extend(("-c", f'model_reasoning_effort={json.dumps(effort)}'))
    argv.append("-")
    return SpawnSpec(argv, adapt_prompt(prompt))

def prepare_spawn(root: Path, selection: Selection, model: str, prompt: str, label: str, max_chars: int,
                  effort: str = ""):
    spec = spawn_spec(root, selection, model, prompt, effort)
    return spec, EventObserver(root, label, model, max_chars)

def start(spec: SpawnSpec, root: Path, env: dict) -> subprocess.Popen:
    proc = subprocess.Popen(spec.argv, cwd=root, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace", bufsize=1, shell=False)
    proc.stdin.write(spec.prompt)
    proc.stdin.close()
    return proc

def spawn_env(source: dict, codex: bool) -> dict:
    env = dict(source, AUTORESEARCH_SUPERVISED="1")
    if codex:
        env["AUTORESEARCH_ACTIVE_BACKEND"] = "codex"
    else:
        env.pop("AUTORESEARCH_ACTIVE_BACKEND", None)
    return env

class EventObserver:
    def __init__(self, root: Path, label: str, model: str, max_chars: int):
        self.root, self.label, self.model, self.max_chars = root, label, model, max_chars
        self.thread_id = None
        self.completed = False
        self.failed = False
        self.malformed = False
        self.reader_eof = False
        self.provenance_error = ""

    def _clip(self, text: str) -> str:
        return f"[{self.label}] {text}"[:self.max_chars]

    def _record_thread(self) -> None:
        path = self.root / "results" / "diagnostics" / "agent_sessions.jsonl"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            row = {"utc": _dt.datetime.now(_dt.timezone.utc).isoformat(), "backend": "codex",
                   "label": self.label, "thread_id": self.thread_id, "model": self.model or "default"}
            with path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        except OSError as exc:
            self.provenance_error = str(exc)

    def observe(self, raw_line: str, display: bool = True) -> str | None:
        text = raw_line.rstrip("\r\n")
        if not text.strip():
            return None
        try:
            event = json.loads(text)
        except json.JSONDecodeError:
            # Codex stdout and stderr share one pipe.  Multi-line CLI/tool diagnostics can therefore
            # begin with a PowerShell ``{``/``[`` fragment even though they are not protocol events.
            # Fail closed only when a broken line actually presents the canonical event discriminator.
            head = text.lstrip()
            event_head = head[1:].lstrip() if head.startswith("{") else ""
            self.malformed = event_head.startswith('"type"') or self.malformed
            return self._clip("diagnostic: " + text)
        if not isinstance(event, dict):
            # Merged stderr may also contain quoted PowerShell lines or JSON-shaped diagnostics.
            # Codex protocol events are objects carrying ``type``; scalars/arrays cannot advance state.
            return self._clip("diagnostic: " + text)
        kind = event.get("type")
        if kind == "thread.started":
            value = event.get("thread_id")
            if isinstance(value, str) and value and self.thread_id is None:
                self.thread_id = value
                self._record_thread()
            warning = f" provenance-write-error={self.provenance_error}" if self.provenance_error else ""
            return self._clip(f"thread start (thread_id={self.thread_id or '?'}){warning}")
        if kind == "turn.completed":
            self.completed = True
            usage = event.get("usage") if isinstance(event.get("usage"), dict) else {}
            return self._clip(f"RESULT ok=True tokens_in={usage.get('input_tokens', '?')} "
                              f"tokens_out={usage.get('output_tokens', '?')}")
        if kind == "turn.failed":
            self.failed = True
            error = event.get("error")
            detail = error.get("message", "turn failed") if isinstance(error, dict) else (error or "turn failed")
            return self._clip("RESULT ok=False " + str(detail))
        if kind == "error":
            return self._clip("error: " + str(event.get("message", "Codex error")))
        if kind in ("item.started", "item.updated", "item.completed") and display:
            item = event.get("item") if isinstance(event.get("item"), dict) else {}
            item_type = item.get("type")
            if item_type == "agent_message" and str(item.get("text", "")).strip():
                return self._clip("text: " + " ".join(str(item["text"]).split()))
            if item_type == "command_execution":
                return self._clip(f"command: {item.get('command', '?')} status={item.get('status', '?')}")
            if item_type == "file_change":
                return self._clip(f"file change: {item.get('status', kind)}")
        return None

    def successful(self, returncode: int) -> bool:
        return (returncode == 0 and bool(self.thread_id) and self.completed
                and not self.failed and not self.malformed)

def smoke(root: Path, selection: Selection, env: dict) -> tuple[subprocess.CompletedProcess, list[str], bool]:
    spec = spawn_spec(root, selection, "", "Reply with exactly OK and end the turn.")
    proc = subprocess.run(spec.argv, cwd=root, input=spec.prompt, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=300, env=env, shell=False)
    observer = EventObserver(root, "smoke", "", 500)
    rendered = []
    for line in ((proc.stdout or "") + "\n" + (proc.stderr or "")).splitlines():
        output = observer.observe(line)
        if output:
            rendered.append(output)
    return proc, rendered, observer.successful(proc.returncode)

def stamp_worker_snapshot(root: Path, config_path: Path, observer: EventObserver | None) -> str:
    if observer is None or not observer.thread_id:
        return "missing Codex thread ID"
    try:
        stem = json.loads((root / config_path).read_text(encoding="utf-8"))["exp_name"]
        manifest = root / "results" / "snapshots" / stem / "manifest.txt"
        with manifest.open("a", encoding="utf-8") as stream:
            stream.write(f"agent_backend: codex\nagent_thread_id: {observer.thread_id}\n")
    except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        return str(exc)
    return ""
