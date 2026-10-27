"""Shared test paths (importable as ``support`` via pytest ``pythonpath``)."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALID_FIXTURE = REPO_ROOT / "data" / "fixtures" / "minimal_state.json"
INVALID_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "invalid"
SCHEMA_PATH = REPO_ROOT / "data" / "manifests" / "game_state.schema.json"
