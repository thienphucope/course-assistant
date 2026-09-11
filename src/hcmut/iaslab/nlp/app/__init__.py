"""Public API of the grammar-driven Course Assistant template.

The package is split into small stages with explicit data contracts:
tokenization -> CFG parsing -> semantic interpretation -> context resolution ->
knowledge query -> answer rendering.  ``CourseAssistant`` is the facade that
wires those stages together; individual stages remain replaceable for tests or
future implementations.
"""

from .pipeline import CourseAssistant, PipelineComponents, PipelineResult

__all__ = ["CourseAssistant", "PipelineComponents", "PipelineResult"]
