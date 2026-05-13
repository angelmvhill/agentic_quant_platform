"""Local dbt/DuckDB project helpers used by the dbt API routes."""
from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from aqp.config import settings


@dataclass
class DbtStatus:
    project_dir: str
    profiles_dir: str
    target: str
    exists: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DbtCommandResult:
    command: str
    ok: bool
    returncode: int
    stdout: str = ""
    stderr: str = ""
    models: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DbtExportResult:
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DbtExportOptions:
    include_dataset_models: bool = True
    include_platform_tables: bool = True
    force_project: bool = False
    selected_tables: list[str] = field(default_factory=list)


class DbtProjectManager:
    def __init__(self, project_dir: Path, profiles_dir: Path, target: str) -> None:
        self.project_dir = project_dir
        self.profiles_dir = profiles_dir
        self.target = target
        self.duckdb_path = settings.dbt_duckdb_path
        self.generated_schema = settings.dbt_generated_schema
        self.generated_tag = settings.dbt_generated_tag
        self.export_dir = settings.dbt_export_dir

    @classmethod
    def from_settings(cls) -> DbtProjectManager:
        return cls(settings.dbt_project_dir, settings.dbt_profiles_dir, settings.dbt_target)

    def status(self) -> DbtStatus:
        return DbtStatus(
            project_dir=str(self.project_dir),
            profiles_dir=str(self.profiles_dir),
            target=self.target,
            exists=self.project_dir.exists(),
        )

    def ensure_project(self, *, force: bool = False) -> dict[str, Any]:
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        project = self.project_dir / "dbt_project.yml"
        if force or not project.exists():
            project.write_text(
                "name: aqp\nversion: '1.0'\nprofile: aqp\nmodel-paths: ['models']\n",
                encoding="utf-8",
            )
        (self.project_dir / "models").mkdir(exist_ok=True)
        return {"created": True, **self.status().to_dict()}

    def list_files(self) -> list[dict[str, Any]]:
        if not self.project_dir.exists():
            return []
        return [
            {"path": str(path.relative_to(self.project_dir)), "size": path.stat().st_size}
            for path in self.project_dir.rglob("*")
            if path.is_file()
        ]

    def read_file(self, path: str | None) -> dict[str, Any]:
        if not path:
            raise FileNotFoundError(path)
        target = (self.project_dir / path).resolve()
        if self.project_dir.resolve() not in target.parents and target != self.project_dir.resolve():
            raise ValueError("path escapes dbt project")
        return {"path": path, "content": target.read_text(encoding="utf-8")}

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        target = (self.project_dir / path).resolve()
        if self.project_dir.resolve() not in target.parents and target != self.project_dir.resolve():
            raise ValueError("path escapes dbt project")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"path": path, "bytes": len(content.encode("utf-8"))}


class DbtExporter:
    def __init__(self, manager: DbtProjectManager) -> None:
        self.manager = manager

    def export(self, _options: DbtExportOptions) -> DbtExportResult:
        self.manager.ensure_project()
        return DbtExportResult(files=[item["path"] for item in self.manager.list_files()])


class DbtRunnerService:
    def __init__(self, manager: DbtProjectManager) -> None:
        self.manager = manager

    def _run(self, command: str, args: list[str] | None = None) -> DbtCommandResult:
        self.manager.ensure_project()
        cmd = ["dbt", command, "--project-dir", str(self.manager.project_dir)]
        cmd.extend(args or [])
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=settings.dbt_command_timeout_seconds)
            return DbtCommandResult(command=command, ok=proc.returncode == 0, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        except FileNotFoundError:
            return DbtCommandResult(command=command, ok=False, returncode=127, stderr="dbt executable not installed")

    def parse(self) -> DbtCommandResult:
        return self._run("parse")

    def build(self, *, select: list[str]) -> DbtCommandResult:
        return self._run("build", ["--select", *select] if select else [])

    def test(self, *, select: list[str]) -> DbtCommandResult:
        return self._run("test", ["--select", *select] if select else [])

    def compile(self, *, select: list[str]) -> DbtCommandResult:
        return self._run("compile", ["--select", *select] if select else [])

    def show(self, *, select: list[str], inline: str | None, limit: int) -> DbtCommandResult:
        args = ["--limit", str(limit)]
        if select:
            args.extend(["--select", *select])
        if inline:
            args.extend(["--inline", inline])
        return self._run("show", args)


def artifact_paths(project_dir: Path) -> dict[str, str]:
    return {
        "manifest": str(project_dir / "target" / "manifest.json"),
        "run_results": str(project_dir / "target" / "run_results.json"),
    }


def load_manifest_models(project_dir: Path) -> list[dict[str, Any]]:
    manifest = project_dir / "target" / "manifest.json"
    if not manifest.exists():
        return []
    data = json.loads(manifest.read_text(encoding="utf-8"))
    nodes = data.get("nodes", {})
    return [value for value in nodes.values() if value.get("resource_type") == "model"]


def load_model_detail(unique_id: str, project_dir: Path) -> dict[str, Any] | None:
    for model in load_manifest_models(project_dir):
        if model.get("unique_id") == unique_id:
            return model
    return None


def load_run_results(project_dir: Path) -> dict[str, Any]:
    path = project_dir / "target" / "run_results.json"
    if not path.exists():
        return {"results": []}
    return json.loads(path.read_text(encoding="utf-8"))
