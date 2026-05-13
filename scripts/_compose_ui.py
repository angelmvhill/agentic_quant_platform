from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_ui_service(*, service: str, label: str, url: str, build: bool, logs: bool) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    command = ["docker", "compose", "up", "-d"]
    if build:
        command.append("--build")
    command.append(service)

    print(f"Starting {label} with Docker compose...")
    try:
        subprocess.run(command, cwd=repo_root, check=True)
    except FileNotFoundError:
        print("Docker was not found on PATH. Install or start Docker Desktop first.", file=sys.stderr)
        return 127
    except subprocess.CalledProcessError as exc:
        print(f"docker compose failed with exit code {exc.returncode}.", file=sys.stderr)
        return exc.returncode

    print(f"{label}: {url}")
    print(f"Logs: python scripts/run_{service}.py --logs")

    if logs:
        try:
            subprocess.run(
                ["docker", "compose", "logs", "-f", "--tail=200", service],
                cwd=repo_root,
                check=False,
            )
        except KeyboardInterrupt:
            return 130

    return 0


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--build",
        action="store_true",
        help="Rebuild the Docker image before starting the service.",
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Tail the service logs after starting it.",
    )
