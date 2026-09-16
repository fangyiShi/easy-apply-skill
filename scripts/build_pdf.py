"""Compile an Easy Apply LaTeX material into PDF."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


def latex_environment(workspace: str | Path | None = None) -> dict[str, str]:
    """Return a LaTeX environment that can resolve the workspace layout.

    A trailing path separator preserves the TeX engine's normal built-in search
    paths after the workspace profile directory.
    """

    env = os.environ.copy()
    if workspace is None:
        return env

    root = Path(workspace).expanduser().resolve()
    profile_dir = root / "profile"
    if not profile_dir.is_dir():
        raise FileNotFoundError(f"Missing workspace profile directory: {profile_dir}")
    layout = profile_dir / "resume-layout.tex"
    if not layout.is_file():
        raise FileNotFoundError(f"Missing canonical resume layout: {layout}")

    existing = env.get("TEXINPUTS", "")
    entries = [str(profile_dir)]
    if existing:
        entries.append(existing)
    env["TEXINPUTS"] = os.pathsep.join(entries) + os.pathsep
    return env


def build_pdf(
    tex_file: str | Path,
    *,
    output_dir: str | Path | None = None,
    workspace: str | Path | None = None,
    engine: str = "pdflatex",
    passes: int = 2,
) -> Path:
    tex_path = Path(tex_file).expanduser().resolve()
    if not tex_path.is_file():
        raise FileNotFoundError(f"Missing TeX file: {tex_path}")
    if tex_path.suffix.lower() != ".tex":
        raise ValueError(f"Expected a .tex file: {tex_path}")
    if passes < 1 or passes > 5:
        raise ValueError("passes must be between 1 and 5")

    executable = shutil.which(engine)
    if not executable:
        raise RuntimeError(f"LaTeX engine not found on PATH: {engine}")

    target_dir = Path(output_dir).expanduser().resolve() if output_dir else tex_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    environment = latex_environment(workspace)

    command = [
        executable,
        "-interaction=nonstopmode",
        "-halt-on-error",
        f"-output-directory={target_dir}",
        tex_path.name,
    ]

    for run_index in range(1, passes + 1):
        result = subprocess.run(
            command,
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            check=False,
        )
        if result.returncode != 0:
            tail = "\n".join((result.stdout + "\n" + result.stderr).splitlines()[-40:])
            raise RuntimeError(
                f"LaTeX build failed on pass {run_index} for {tex_path.name}:\n{tail}"
            )

    pdf_path = target_dir / f"{tex_path.stem}.pdf"
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Build completed without a usable PDF: {pdf_path}")
    return pdf_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compile an Easy Apply .tex file to PDF")
    parser.add_argument("tex_file")
    parser.add_argument("--output-dir")
    parser.add_argument("--workspace", help="Workspace root containing profile/resume-layout.tex")
    parser.add_argument("--engine", default="pdflatex")
    parser.add_argument("--passes", type=int, default=2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        pdf = build_pdf(
            args.tex_file,
            output_dir=args.output_dir,
            workspace=args.workspace,
            engine=args.engine,
            passes=args.passes,
        )
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"ok": True, "pdf": str(pdf)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
