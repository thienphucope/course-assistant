"""Build and verify a submission archive in the layout required by spec §7.4.

Without --student-ids this creates a review archive, not the final named upload.
Use --verify-docker on a machine with Docker to perform the container checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from zipfile import ZipFile, ZIP_DEFLATED

REPO = Path(__file__).resolve().parents[1]
OUTPUTS = {"grammar.txt", "samples.txt", "parse-results.txt", "semantic.txt", "intent-entity.txt",
           "query.txt", "answer.txt", "dialogue.txt", "evaluation.txt"}


def run(*command, cwd=None):
    subprocess.run(command, cwd=cwd, check=True)


def verify_outputs(project: Path):
    output = project / "output"
    missing = [name for name in sorted(OUTPUTS) if not (output / name).is_file() or not (output / name).stat().st_size]
    if missing:
        raise RuntimeError(f"Missing/empty outputs: {missing}")
    questions = [line for line in (project / "input/sentences.txt").read_text(encoding="utf-8").splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
    for name in ("parse-results.txt", "semantic.txt", "intent-entity.txt", "query.txt"):
        if len((output / name).read_text(encoding="utf-8").splitlines()) != len(questions):
            raise RuntimeError(f"Record count differs from input: {name}")
    if len((output / "samples.txt").read_text(encoding="utf-8").splitlines()) > 10000:
        raise RuntimeError("samples.txt exceeds 10000 sentences")
    if (output / "grammar.txt").read_text(encoding="utf-8") != (project / "data/grammar.cfg").read_text(encoding="utf-8"):
        raise RuntimeError("grammar.txt differs from the runtime grammar")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--student-ids", nargs="+", help="3 or 4 MSSV values in final filename order")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-docker", action="store_true")
    video_source = parser.add_mutually_exclusive_group()
    video_source.add_argument("--video", type=Path, help="include a demo video; defaults to dist/course-assistant-demo.mp4 if present")
    video_source.add_argument("--video-url", help="include an external demo video link in the README and demo-video.txt")
    args = parser.parse_args(argv)
    if args.student_ids and (len(args.student_ids) not in (3, 4) or
                             any(not re.fullmatch(r"[0-9]+", value) for value in args.student_ids)):
        parser.error("provide 3 or 4 numeric student IDs")
    if args.video_url is not None:
        try:
            parsed_url = urlsplit(args.video_url)
            valid_url = (parsed_url.scheme in {"https", "http"} and parsed_url.hostname
                         and not any(char.isspace() or char in "<>" for char in args.video_url))
        except ValueError:
            valid_url = False
        if not valid_url:
            parser.error("--video-url requires a valid HTTP or HTTPS link")
    filename = "-".join(args.student_ids) if args.student_ids else "course-assistant-review"
    destination = (args.output or REPO / "dist" / f"{filename}.zip").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    source = REPO / "src"
    run(sys.executable, str(source / "run.py"), "--root", str(source), "all")
    verify_outputs(source)
    with tempfile.TemporaryDirectory(prefix="course-assistant-package-") as temporary:
        workspace = Path(temporary)
        project = workspace / "project"
        project.mkdir()
        for directory in ("data", "input", "output", "models"):
            shutil.copytree(source / directory, project / directory,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copytree(source / "hcmut", project / "src/hcmut",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("run.py", "README.md", "Dockerfile", ".dockerignore", "requirements.txt"):
            shutil.copy2(source / name, project / name)
        demo_tools = project / "tools"
        shutil.copytree(REPO / "tools/demo_web", demo_tools / "demo_web",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in ("demo.py", "demo_web.py"):
            shutil.copy2(REPO / "tools" / name, demo_tools / name)
        # The compiled LaTeX report (report/) is the submitted report; the Markdown
        # draft in docs/ is only a fallback when the PDF has not been built.
        report_pdf = REPO / "report" / "report.pdf"
        if report_pdf.is_file():
            shutil.copy2(report_pdf, project / "report.pdf")
        elif (REPO / "docs/report.md").is_file():
            shutil.copy2(REPO / "docs/report.md", project / "report.md")
        if args.video_url:
            (project / "demo-video.txt").write_text(args.video_url + "\n", encoding="utf-8")
            with (project / "README.md").open("a", encoding="utf-8") as readme:
                readme.write(f"\n[Xem video demo](<{args.video_url}>)\n")
        else:
            video = args.video or REPO / "dist/course-assistant-demo.mp4"
            if args.video and not video.is_file():
                parser.error(f"video does not exist: {video}")
            if video.is_file():
                shutil.copy2(video, project / "demo.mp4")
        with ZipFile(destination, "w", ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(project.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(workspace).as_posix())
        if destination.stat().st_size >= 10_000_000:
            raise RuntimeError("archive must be less than 10 MB")
        extracted = workspace / "verify"
        with ZipFile(destination) as archive:
            archive.extractall(extracted)
        unpacked = extracted / "project"
        expected_outputs = {name: (unpacked / "output" / name).read_bytes() for name in OUTPUTS}
        # Run from a different cwd, without installing the repository package.
        run(sys.executable, str(unpacked / "run.py"), "all", cwd=workspace)
        verify_outputs(unpacked)
        for name, expected in expected_outputs.items():
            if (unpacked / "output" / name).read_bytes() != expected:
                raise RuntimeError(f"Extracted run differs from source run: {name}")
        if args.verify_docker:
            if not shutil.which("docker"):
                raise RuntimeError("--verify-docker requires Docker in PATH")
            run("docker", "build", "-t", "course-assistant-submission-check", str(unpacked))
            docker_output = workspace / "docker-output"
            docker_output.mkdir()
            run("docker", "run", "--rm", "--mount", f"type=bind,source={docker_output},target=/app/output",
                "course-assistant-submission-check")
            if set(path.name for path in docker_output.glob("*.txt")) != OUTPUTS:
                raise RuntimeError("Docker did not produce all nine output files")
            for name, expected in expected_outputs.items():
                if (docker_output / name).read_bytes() != expected:
                    raise RuntimeError(f"Docker run differs from source run: {name}")
    metadata = {"archive": destination.name, "bytes": destination.stat().st_size,
                "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "extracted_run": "passed; all nine outputs match source byte-for-byte",
                "docker": "passed" if args.verify_docker else "not checked",
                "final_student_filename": bool(args.student_ids)}
    destination.with_suffix(".validation.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
