"""Tests for the brainstorm workflow profile."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = REPO_ROOT / "config" / "profiles" / "brainstorm"
APPLIER = REPO_ROOT / "bin" / "ccb-profile-apply"


def _run_applier(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(APPLIER), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def test_brainstorm_bundle_exists():
    expected = {"ccb.config", "CLAUDE.md", "AGENTS.md", "gitignore.fragment", "README.md"}
    assert PROFILE_DIR.is_dir()
    assert {p.name for p in PROFILE_DIR.iterdir()} >= expected


def test_brainstorm_applier_output_loads_via_public_loader(tmp_path):
    proc = _run_applier(["--name", "brainstorm", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    sys.path.insert(0, str(REPO_ROOT / "lib"))
    try:
        from agents.config_loader_runtime import load_project_config  # noqa: WPS433
    finally:
        sys.path.pop(0)
    result = load_project_config(tmp_path)
    assert result is not None
    text = (tmp_path / ".ccb" / "ccb.config").read_text(encoding="utf-8")
    assert text.strip() == "claude:claude; codex:codex"


def test_brainstorm_profile_rules_are_non_implementation():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROFILE_DIR / "AGENTS.md", PROFILE_DIR / "CLAUDE.md")
    )
    assert "Do not edit files" in combined
    assert "commit" in combined
    assert "feasibility" in combined
    assert "synthesis" in combined
    assert "pm-dev" in combined


def test_brainstorm_profile_embeds_remote_evidence_rules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROFILE_DIR / "AGENTS.md", PROFILE_DIR / "CLAUDE.md")
    )
    assert "Remote server targets" in combined
    assert "evidence/context only" in combined
    assert "Never run local commands that touch `/mnt/...`" in combined
    assert "Do not edit remote files" in combined


def test_brainstorm_profile_requires_time_estimate_when_needed():
    text = (PROFILE_DIR / "CLAUDE.md").read_text(encoding="utf-8")
    assert "debate-time estimate" in text


def test_applier_list_mentions_brainstorm():
    proc = _run_applier(["--list"], cwd=REPO_ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "brainstorm" in proc.stdout.split()
