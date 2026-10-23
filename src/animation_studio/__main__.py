"""CLI: python -m animation_studio {import-story,import-assets,animatic,render,check}."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .assets import import_assets
from .animatic import build_animatic
from .config import resolve_workspace
from .render import build_render
from .qc import check_render
from .story import import_story
from .workspace import UserError, project_dir, read_json, validate_project_id


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="animation_studio")
    p.add_argument("--workspace", help="workspace root (overrides config.toml)")
    p.add_argument("--config", default="config.toml", help="config file (default: ./config.toml)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("import-story", help="store a story text with provenance")
    s.add_argument("project")
    s.add_argument("file", type=Path)
    s.add_argument("--title")
    s.add_argument("--source", required=True)
    s.add_argument("--rights", required=True)
    s.add_argument("--author")
    s.add_argument("--translator")
    s.add_argument("--genre")

    a = sub.add_parser("import-assets", help="copy image/audio assets into the workspace")
    a.add_argument("project")
    a.add_argument("files", nargs="+", type=Path)
    a.add_argument("--kind", required=True, choices=["image", "audio"])
    a.add_argument("--license", required=True)
    a.add_argument("--source-tool", required=True)
    a.add_argument("--model")
    a.add_argument("--declared-cost-usd", type=float, default=0)
    sub.add_parser("animatic", help="build a static animatic from shots.json").add_argument("project")
    sub.add_parser("render", help="render camera motion, transitions and mixed audio").add_argument("project")
    sub.add_parser("check", help="check the existing film and write render/qc.json").add_argument("project")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        validate_project_id(args.project)
        workspace = resolve_workspace(args.workspace, Path(args.config))
        if args.command == "import-story":
            meta = {k: getattr(args, k) for k in ("title", "source", "rights", "author", "translator", "genre")}
            print(f"story {import_story(workspace, args.project, args.file, meta)}")
        elif args.command == "import-assets":
            meta = {"license": args.license, "source_tool": args.source_tool, "model": args.model,
                    "declared_cost_usd": args.declared_cost_usd}
            added, skipped = import_assets(workspace, args.project, args.kind, args.files, meta)
            print(f"assets added={added} skipped={skipped}")
        elif args.command in ("animatic", "render"):
            previous = read_json(project_dir(workspace, args.project) / "render/qc.json") if args.command == "render" else None
            builder = build_render if args.command == "render" else build_animatic
            built, reused, path = builder(workspace, args.project)
            print(f"{args.command} built={built} reused={reused} -> {path}")
        if args.command in ("render", "check"):
            report = check_render(workspace, args.project, previous if args.command == "render" else None,
                                  compare=args.command == "render")
            print(f"qc {report['overall']} -> {project_dir(workspace, args.project).resolve() / 'render/qc.json'}")
            for item in report["checks"]:
                if item["status"] in ("FAIL", "WARN"):
                    print(f"{item['status']} {item['name']}: {item['detail'] or item['measured']}")
            if args.command == "check" and report["overall"] == "FAIL":
                return 2
    except UserError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
