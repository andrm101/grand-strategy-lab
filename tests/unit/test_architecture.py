"""Architecture boundaries (PROJECT_CHARTER.md Milestone 1; ADR-0004)."""

import ast
import sys
from pathlib import Path

from support import REPO_ROOT

PACKAGE = REPO_ROOT / "src" / "grand_strategy_lab"
DOMAIN_ALLOWED_THIRD_PARTY = {"pydantic", "pydantic_core"}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            modules.add(node.module)
    return modules


def test_domain_depends_only_on_stdlib_pydantic_and_itself() -> None:
    violations: list[str] = []
    for path in sorted((PACKAGE / "domain").rglob("*.py")):
        for module in _imports(path):
            top = module.split(".")[0]
            if top in sys.stdlib_module_names or top in DOMAIN_ALLOWED_THIRD_PARTY:
                continue
            if module.startswith("grand_strategy_lab.domain"):
                continue
            violations.append(f"{path.relative_to(REPO_ROOT).as_posix()}: {module}")
    assert violations == []


def test_no_module_shadows_stdlib() -> None:
    shadowing = [
        path.relative_to(REPO_ROOT).as_posix()
        for path in PACKAGE.rglob("*.py")
        if path.stem in sys.stdlib_module_names
    ]
    assert shadowing == []
