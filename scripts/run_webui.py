from __future__ import annotations

import argparse

from _compose_ui import add_common_args, run_ui_service


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start the legacy Next.js webui Docker service on http://localhost:3000.",
    )
    add_common_args(parser)
    args = parser.parse_args()

    return run_ui_service(
        service="webui",
        label="WebUI",
        url="http://localhost:3000",
        build=args.build,
        logs=args.logs,
    )


if __name__ == "__main__":
    raise SystemExit(main())
