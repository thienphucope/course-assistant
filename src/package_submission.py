"""Validate and package the assignment as ``project/`` inside a small ZIP.

This script is intentionally independent of the NLP package.  It can inspect a
freshly extracted submission even when the application itself cannot import.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import ZIP_DEFLATED, ZipFile


MAX_ZIP_BYTES = 10 * 1024 * 1024
MEMBER_MARKER = "CHƯA CUNG CẤP"
REQUIRED_FILES = (
    "README.md",
    "Dockerfile",
    "requirements.txt",
    "run.py",
    "data/grammar.cfg",
    "data/kb/assignments.txt",
    "data/kb/course_info.txt",
    "data/kb/regulations.txt",
    "data/kb/resources.txt",
    "data/kb/schedule.txt",
    "data/kb/topics.txt",
    "data/scaffolding/gold_queries.txt",
    "data/scaffolding/challenge_queries.txt",
    "input/sentences.txt",
    "output/grammar.txt",
    "output/samples.txt",
    "output/parse-results.txt",
    "output/semantic.txt",
    "output/intent-entity.txt",
    "output/query.txt",
    "output/answer.txt",
    "output/evaluation.txt",
    "hcmut/iaslab/nlp/app/pipeline.py",
)
ALIGNED_OUTPUTS = (
    "parse-results.txt",
    "semantic.txt",
    "intent-entity.txt",
    "query.txt",
    "answer.txt",
)
JSONL_OUTPUTS = ("intent-entity.txt", "query.txt", "answer.txt")
EXCLUDED_DIRECTORIES = {
    ".git",
    ".idea",
    ".pytest_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class ValidationReport:
    """Human-readable submission checks without changing the project."""

    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    facts: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.errors


def validate_project(root: Path) -> ValidationReport:
    """Check required layout, output alignment, encoding, and known placeholders."""
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    facts: list[str] = []

    missing = [relative for relative in REQUIRED_FILES if not (root / relative).is_file()]
    if missing:
        errors.append("Thiếu file bắt buộc: " + ", ".join(missing))

    readme = root / "README.md"
    if readme.is_file():
        readme_text = readme.read_text(encoding="utf-8-sig")
        if MEMBER_MARKER in readme_text:
            warnings.append("README chưa có họ tên/MSSV thật của thành viên.")

    input_path = root / "input" / "sentences.txt"
    question_count: int | None = None
    if input_path.is_file():
        questions = [
            line.strip()
            for line in input_path.read_text(encoding="utf-8-sig").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        question_count = len(questions)
        facts.append(f"Input có {question_count} câu được xử lý.")

    output_dir = root / "output"
    if question_count is not None:
        for name in ALIGNED_OUTPUTS:
            path = output_dir / name
            if path.is_file():
                count = len(path.read_text(encoding="utf-8-sig").splitlines())
                if count != question_count:
                    errors.append(
                        f"output/{name} có {count} dòng, cần {question_count} dòng."
                    )

    samples = output_dir / "samples.txt"
    if samples.is_file():
        sample_count = len(samples.read_text(encoding="utf-8-sig").splitlines())
        if not 1 <= sample_count <= 10_000:
            errors.append(f"output/samples.txt có {sample_count} dòng; giới hạn là 1–10000.")
        else:
            facts.append(f"Output có {sample_count} câu sinh từ grammar.")

    source_grammar = root / "data" / "grammar.cfg"
    output_grammar = output_dir / "grammar.txt"
    if source_grammar.is_file() and output_grammar.is_file():
        if source_grammar.read_text(encoding="utf-8-sig") != output_grammar.read_text(
            encoding="utf-8-sig"
        ):
            errors.append("output/grammar.txt không khớp data/grammar.cfg; hãy chạy lại batch.")

    for name in JSONL_OUTPUTS:
        path = output_dir / name
        if not path.is_file():
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"output/{name}:{line_number} không phải JSON hợp lệ: {exc.msg}.")
                break

    evaluation = output_dir / "evaluation.txt"
    if evaluation.is_file():
        text = evaluation.read_text(encoding="utf-8-sig")
        if "Combined declared-label pass:" not in text or "Failures:" not in text:
            errors.append("output/evaluation.txt thiếu số liệu tổng hợp hoặc danh sách ca sai.")

    unexpected_placeholder = output_dir / "dialogue.txt"
    if unexpected_placeholder.exists():
        warnings.append("output/dialogue.txt là file tùy chọn; bỏ khỏi ZIP nếu chưa làm hội thoại.")

    candidate_size = sum(path.stat().st_size for path in submission_files(root))
    facts.append(f"Dung lượng file trước khi nén: {candidate_size / 1024:.1f} KiB.")
    facts.append("Docker cần được build/run trên máy có Docker trước khi nộp.")
    return ValidationReport(tuple(errors), tuple(warnings), tuple(facts))


def submission_files(root: Path) -> list[Path]:
    """Return sorted files safe to include in the final project folder."""
    root = root.resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRECTORIES for part in relative.parts):
            continue
        if path.suffix.lower() in EXCLUDED_SUFFIXES:
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build_archive(root: Path, destination: Path, student_ids: list[str]) -> Path:
    """Create ``MSSV1-MSSV2-....zip`` with exactly one ``project/`` root."""
    report = validate_project(root)
    if report.errors:
        raise ValueError("Không thể đóng gói:\n- " + "\n- ".join(report.errors))
    readme_text = (root / "README.md").read_text(encoding="utf-8-sig")
    if MEMBER_MARKER in readme_text:
        raise ValueError("Hãy điền họ tên và MSSV thật trong README trước khi đóng gói.")

    normalized_ids = [_validate_student_id(value) for value in student_ids]
    if not 1 <= len(normalized_ids) <= 4:
        raise ValueError("Cần cung cấp từ 1 đến 4 MSSV theo đúng số thành viên của nhóm.")

    destination = destination.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / ("-".join(normalized_ids) + ".zip")
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as package:
        for path in submission_files(root):
            relative = path.relative_to(root)
            archive_name = PurePosixPath("project", *relative.parts).as_posix()
            package.write(path, archive_name)

    if archive.stat().st_size >= MAX_ZIP_BYTES:
        archive.unlink()
        raise ValueError("ZIP từ 10 MB trở lên; đã xóa file không đạt giới hạn của đề.")
    return archive


def render_report(report: ValidationReport) -> str:
    lines = ["KIỂM TRA BẢN NỘP COURSE ASSISTANT"]
    lines.extend(f"[OK] {fact}" for fact in report.facts)
    lines.extend(f"[CẢNH BÁO] {warning}" for warning in report.warnings)
    lines.extend(f"[LỖI] {error}" for error in report.errors)
    lines.append("Kết quả cấu trúc: " + ("ĐẠT" if report.valid else "CHƯA ĐẠT"))
    return "\n".join(lines)


def _validate_student_id(value: str) -> str:
    candidate = value.strip().upper()
    if not re.fullmatch(r"[A-Z0-9]{4,20}", candidate):
        raise ValueError(f"MSSV không hợp lệ: {value!r}")
    return candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", help="kiểm tra cấu trúc và output, không sửa file")
    build = commands.add_parser("build", help="tạo ZIP có thư mục gốc project/")
    build.add_argument("--student-ids", nargs="+", required=True)
    build.add_argument("--destination", type=Path, default=None)
    args = parser.parse_args(argv)

    report = validate_project(args.root)
    print(render_report(report))
    if args.command == "check":
        return 0 if report.valid else 1
    try:
        destination = args.destination or args.root.resolve().parent / "submission"
        archive = build_archive(args.root, destination, args.student_ids)
    except ValueError as exc:
        print(f"[LỖI] {exc}", file=sys.stderr)
        return 2
    print(f"[OK] Đã tạo {archive} ({archive.stat().st_size / 1024:.1f} KiB).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
