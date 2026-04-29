"""Tests for the pm-dev workflow profile and ccb-profile-apply."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROFILE_DIR = REPO_ROOT / "config" / "profiles" / "pm-dev"
APPLIER = REPO_ROOT / "bin" / "ccb-profile-apply"


def _run_applier(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(APPLIER), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def test_pm_dev_bundle_exists():
    expected = {"ccb.config", "CLAUDE.md", "AGENTS.md", "gitignore.fragment", "README.md"}
    assert PROFILE_DIR.is_dir()
    assert {p.name for p in PROFILE_DIR.iterdir()} >= expected


def test_applier_output_loads_via_public_loader(tmp_path):
    """The applier's actual output (not a hand-crafted layout) must satisfy load_project_config."""
    proc = _run_applier(["--name", "pm-dev", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    sys.path.insert(0, str(REPO_ROOT / "lib"))
    try:
        from agents.config_loader_runtime import load_project_config  # noqa: WPS433
    finally:
        sys.path.pop(0)
    result = load_project_config(tmp_path)
    assert result is not None
    text = (tmp_path / ".ccb" / "ccb.config").read_text(encoding="utf-8")
    assert "planner" in text and "critic" in text and "executor" in text


def test_pm_dev_profile_files_have_no_local_paths_or_secrets():
    forbidden = [
        "/Users/",
        "/opt/homebrew",
        "claude_code_bridge/ccb",
        "train1_8",
        "http_proxy",
        "ANTHROPIC_BASE_URL",
        "/mnt/world_foundational_model",
        "sheyangsuzhiyuan",
    ]
    for path in PROFILE_DIR.iterdir():
        if path.is_dir():
            continue
        text = path.read_text(encoding="utf-8")
        for needle in forbidden:
            assert needle not in text, f"{needle!r} leaked into {path.name}"


def test_pm_dev_profile_embeds_remote_server_safety_rules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROFILE_DIR / "AGENTS.md", PROFILE_DIR / "CLAUDE.md")
    )
    assert "Remote server targets" in combined
    assert "Never run local commands that touch `/mnt/...`" in combined
    assert 'ssh <server> "cd /mnt/... && ..."' in combined
    assert "delete local temp copies immediately after successful upload" in combined


def test_pm_dev_profile_embeds_verification_and_commit_hygiene_rules():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (PROFILE_DIR / "AGENTS.md", PROFILE_DIR / "CLAUDE.md")
    )
    assert "Verify against actual files" in combined
    assert "`git log` / `git show`" in combined
    assert "do it only after final verification" in combined
    assert "Co-Authored-By" in combined
    assert "AI attribution" in combined


def test_pm_dev_profile_requires_planner_time_estimate():
    text = (PROFILE_DIR / "CLAUDE.md").read_text(encoding="utf-8")
    assert "elapsed-time estimate" in text
    assert "suggested status-check interval" in text


def test_pm_dev_profile_requires_synchronous_child_handoffs():
    text = (PROFILE_DIR / "CLAUDE.md").read_text(encoding="utf-8")
    assert "ccb ask --wait --timeout 300 critic" in text
    assert "ccb ask --wait --timeout 300 executor" in text
    assert "processing/submitted notice" in text


def test_applier_dry_run_writes_nothing(tmp_path):
    target = tmp_path / "target"
    proc = _run_applier(["--name", "pm-dev", "--dry-run", "--target", str(target)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "would write" in proc.stdout
    assert target.exists()
    assert not list(target.iterdir())


def test_applier_first_apply_writes_expected_files(tmp_path):
    proc = _run_applier(["--name", "pm-dev", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    written = {p.name for p in tmp_path.iterdir() if p.is_file()}
    assert {"CLAUDE.md", "AGENTS.md", ".gitignore"} <= written
    # ccb.config goes under .ccb/, not root
    assert (tmp_path / ".ccb" / "ccb.config").is_file()
    assert not (tmp_path / "ccb.config").exists()
    # README.md and gitignore.fragment are never copied
    assert "README.md" not in written
    assert "gitignore.fragment" not in written
    gi = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "# >>> ccb-profile pm-dev" in gi
    assert ".ccb/*" in gi
    assert "!.ccb/ccb.config" in gi


def test_applier_second_apply_is_idempotent(tmp_path):
    _run_applier(["--name", "pm-dev", "--target", str(tmp_path)], cwd=tmp_path)
    first_gi = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    first_cfg = (tmp_path / ".ccb" / "ccb.config").read_text(encoding="utf-8")
    proc2 = _run_applier(["--name", "pm-dev", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc2.returncode == 0, proc2.stderr
    assert "skipped (exists" in proc2.stdout
    assert "skipped (gitignore block already present)" in proc2.stdout
    # ccb.config explicitly skipped
    assert "ccb.config" in proc2.stdout
    second_gi = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    second_cfg = (tmp_path / ".ccb" / "ccb.config").read_text(encoding="utf-8")
    assert first_gi == second_gi
    assert first_cfg == second_cfg


def test_applier_force_overwrites(tmp_path):
    _run_applier(["--name", "pm-dev", "--target", str(tmp_path)], cwd=tmp_path)
    (tmp_path / "CLAUDE.md").write_text("REPLACED\n", encoding="utf-8")
    proc = _run_applier(["--name", "pm-dev", "--force", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "REPLACED" not in (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")


def test_applier_list_mentions_pm_dev():
    proc = _run_applier(["--list"], cwd=REPO_ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "pm-dev" in proc.stdout.split()


def test_applier_missing_profile_returns_error(tmp_path):
    proc = _run_applier(["--name", "no-such-profile", "--target", str(tmp_path)], cwd=tmp_path)
    assert proc.returncode == 1
    assert "profile not found" in proc.stderr or "profile not found" in proc.stdout
