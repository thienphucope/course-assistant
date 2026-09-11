"""Natural-language rendering for grounded query results.

Answers are templates over ``SemanticFrame`` and ``QueryResult`` rather than
free-form generation.  Keep failure messages distinct for unparsed questions,
missing context, and facts absent from the KB.  Rendering must not perform new
lookups or invent details; provenance remains available in the query result.
Future multilingual or UI-specific renderers can replace this class while
retaining the same input contract.
"""

from __future__ import annotations

from .query import QueryResult
from .semantic import SemanticFrame


NOT_FOUND = "Xin lỗi, tôi không tìm thấy thông tin này trong dữ liệu môn học."
NOT_UNDERSTOOD = "Xin lỗi, câu hỏi nằm ngoài văn phạm hoặc phạm vi Course Assistant."
MISSING_CONTEXT = "Xin lỗi, tôi chưa có đủ ngữ cảnh để hiểu tham chiếu này."


class AnswerGenerator:
    """Render stable Vietnamese answers from structured, grounded data."""

    def generate(self, frame: SemanticFrame, result: QueryResult) -> str:
        """Select a result-kind template or a precise fallback response."""
        raise NotImplementedError("Implement answer templates for every QueryResult.kind")
