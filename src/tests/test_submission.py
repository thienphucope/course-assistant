"""The final archive stays small, complete, and rooted at project/."""

import shutil
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from package_submission import build_archive, validate_project


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class SubmissionTests(unittest.TestCase):
    def test_current_project_structure_and_outputs_are_valid(self) -> None:
        report = validate_project(SOURCE_ROOT)
        self.assertEqual(report.errors, ())
        self.assertTrue(any("MSSV" in warning for warning in report.warnings))

    def test_archive_has_one_project_root_and_excludes_cache(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace) / "runtime"
            destination = Path(workspace) / "submission"
            shutil.copytree(SOURCE_ROOT, root)
            readme = root / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace("CHƯA CUNG CẤP", "ĐÃ ĐIỀN"),
                encoding="utf-8",
            )
            archive = build_archive(root, destination, ["2210001", "2210002"])
            self.assertLess(archive.stat().st_size, 10 * 1024 * 1024)
            with ZipFile(archive) as package:
                names = package.namelist()
            self.assertTrue(names)
            self.assertTrue(all(name.startswith("project/") for name in names))
            self.assertIn("project/Dockerfile", names)
            self.assertIn("project/output/evaluation.txt", names)
            self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))


if __name__ == "__main__":
    unittest.main()
