"""Packaging metadata for the Course Assistant implementation template.

The assignment intentionally uses the Python standard library for the classical
NLP core.  Keep package discovery and the console entry point here; optional
future adapters should declare their dependencies explicitly instead of making
the core pipeline depend on them.
"""

from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
REQUIREMENTS = [
    line.strip()
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.lstrip().startswith("#")
]


setup(
    name="co3085-course-assistant-template",
    version="0.1.0",
    description="Extensible classical-NLP Course Assistant template",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=REQUIREMENTS,
    python_requires=">=3.10",
    entry_points={"console_scripts": ["course-assistant=hcmut.iaslab.nlp.app.cli:main"]},
)
