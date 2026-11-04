"""Entity lexicon and canonical-ID normalization boundary.

Surface forms such as ``tuần 3``, ``week 03``, or future synonyms should resolve
to one stable ID such as ``WEEK_03``.  Grammar decides where an entity may occur;
this module decides what that mention means.  Keep aliases data-driven and keep
IDs stable because semantics, dialogue state, query routing, tests, and output
all exchange them.  New entity families can be added without changing parsing.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

VALID_SECTIONS: frozenset[str] = frozenset({
    "COURSE",
    "PART",
    "CHAPTERS",
    "TOPICS",
    "ASSIGNMENT",
    "INTENTS",
})

TOPIC_IDS: dict[str, str] = {
    "cfg": "CFG",
    "context-free grammar": "CFG",
    "văn phạm phi ngữ cảnh": "CFG",
    "pcfg": "PCFG",
    "probabilistic context-free grammar": "PCFG",
    "dependency grammar": "DEPENDENCY_GRAMMAR",
    "văn phạm phụ thuộc": "DEPENDENCY_GRAMMAR",
    "features": "FEATURES",
    "nét": "FEATURES",
    "augmented grammar": "AUGMENTED_GRAMMAR",
    "văn phạm gia tố": "AUGMENTED_GRAMMAR",
    "unification": "UNIFICATION",
    "hợp nhất": "UNIFICATION",
    "pos tagging": "POS_TAGGING",
    "gán nhãn từ loại": "POS_TAGGING",
    "logical form": "LOGICAL_FORM",
    "dạng luận lý": "LOGICAL_FORM",
    "thematic roles": "THEMATIC_ROLES",
    "vai trò chủ đề": "THEMATIC_ROLES",
    "selectional restriction": "SELECTIONAL_RESTRICTION",
    "giới hạn lựa chọn": "SELECTIONAL_RESTRICTION",
    "semantic network": "SEMANTIC_NETWORK",
    "mạng ngữ nghĩa": "SEMANTIC_NETWORK",
    "wsd": "WSD",
    "word sense disambiguation": "WSD",
    "semantic grammar": "SEMANTIC_GRAMMAR",
    "văn phạm ngữ nghĩa": "SEMANTIC_GRAMMAR",
    "knowledge representation": "KNOWLEDGE_REPRESENTATION",
    "biểu diễn tri thức": "KNOWLEDGE_REPRESENTATION",
    "question answering": "QUESTION_ANSWERING",
    "hỏi đáp": "QUESTION_ANSWERING",
    "local discourse context": "LOCAL_DISCOURSE_CONTEXT",
    "ngữ cảnh diễn ngôn cục bộ": "LOCAL_DISCOURSE_CONTEXT",
    "reference": "REFERENCE",
    "tham chiếu": "REFERENCE",
    "anaphora": "ANAPHORA",
    "đồng tham chiếu": "ANAPHORA",
    "centering": "CENTERING",
    "parsing": "PARSING",
    "phân tích cú pháp": "PARSING",
}

RESOURCE_IDS: dict[str, str] = {
    "statistical nlp": "STATISTICAL_NLP",
    "nlp thống kê": "STATISTICAL_NLP",
    "python nlp": "PYTHON_NLP",
    "nlp với python": "PYTHON_NLP",
    "cfg": "CFG",
    "parsing": "PARSING",
    "ngữ nghĩa": "SEMANTICS",
    "semantic": "SEMANTICS",
    "tri thức thế giới": "WORLD_KNOWLEDGE",
    "world knowledge": "WORLD_KNOWLEDGE",
    "machine translation": "MACHINE_TRANSLATION",
    "dịch máy": "MACHINE_TRANSLATION",
}

RULE_IDS: dict[str, str] = {
    "llm/rag": "LLM_RAG",
    "llm": "LLM_RAG",
    "rag": "LLM_RAG",
    "công cụ ai": "AI_USAGE",
    "ai": "AI_USAGE",
    "sử dụng ai": "AI_USAGE",
    "thư viện ngoài": "EXTERNAL_LIBRARIES",
    "thư viện có sẵn": "EXTERNAL_LIBRARIES",
    "mã nguồn": "SOURCE_CODE",
    "source code": "SOURCE_CODE",
    "liêm chính học thuật": "ACADEMIC_INTEGRITY",
    "chia sẻ bài làm": "ASSIGNMENT_SHARING",
}


class EntityLexicon:
    """Load alias tables and expose deterministic canonicalization methods."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.sections: dict[str, dict[str, str]] = self._load(self.path)

    @classmethod
    def from_file(cls, path: str | Path) -> "EntityLexicon":
        """Load and validate a UTF-8 entity-alias file."""
        return cls(path)

    @staticmethod
    def _load(path: Path) -> dict[str, dict[str, str]]:
        """Parse structured sections and key-value alias pairs from entities.txt."""
        if not path.is_file():
            raise FileNotFoundError(f"Entity lexicon file not found: {path}")

        sections: dict[str, dict[str, str]] = {}
        current_section: str | None = None

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or set(line) == {"="} or line.startswith("COURSE ASSISTANT"):
                continue

            if line in VALID_SECTIONS:
                current_section = line
                sections.setdefault(current_section, {})
                continue

            if current_section and "=" in line:
                alias, canonical = (part.strip() for part in line.split("=", 1))
                sections[current_section][_normalize_phrase(alias)] = canonical
            elif current_section == "INTENTS":
                sections[current_section][_normalize_phrase(line)] = line

        return sections

    def resolve(self, family: str, phrase: str) -> str | None:
        """Resolve ``phrase`` within an entity family to a canonical ID."""
        if not family or not phrase:
            return None

        fam = family.upper().strip()
        if fam in {"WEEK", "WEEK_ENTITY"}:
            return self.resolve_week(phrase)
        if fam in {"CHAPTER", "CHAPTER_ENTITY", "CHAPTERS"}:
            return self.resolve_chapter(phrase)
        if fam in {"LO", "LO_ENTITY", "LEARNING_OUTCOME"}:
            return self.resolve_lo(phrase)
        if fam in {"PART", "ASSIGNMENT_PART"}:
            return self.resolve_assignment_part(phrase)
        if fam in {"TOPIC", "TOPIC_ENTITY", "TOPICS"}:
            return self.resolve_topic(phrase)
        if fam in {"RESOURCE", "RESOURCE_TOPIC"}:
            return self.resolve_resource_topic(phrase)
        if fam in {"RULE", "RULE_TOPIC"}:
            return self.resolve_rule(phrase)

        normalized = _normalize_phrase(phrase)
        return self.sections.get(fam, {}).get(normalized)

    @staticmethod
    def resolve_week(phrase: str) -> str | None:
        """Normalize week mentions to canonical WEEK_NN (e.g. 'tuần 3' -> 'WEEK_03')."""
        if not phrase:
            return None
        match = re.search(r"\d+", phrase)
        return f"WEEK_{int(match.group()):02d}" if match else None

    @staticmethod
    def resolve_chapter(phrase: str) -> str | None:
        """Normalize chapter mentions to canonical CHNN (e.g. 'chương 4' -> 'CH04')."""
        if not phrase:
            return None
        match = re.search(r"\d+", phrase)
        return f"CH{int(match.group()):02d}" if match else None

    @staticmethod
    def resolve_lo(phrase: str) -> str | None:
        """Normalize learning outcome mentions to canonical LOx.y (e.g. 'lo2.5' -> 'LO2.5')."""
        if not phrase:
            return None
        normalized = _normalize_phrase(phrase)
        clean = re.sub(r"\bl\s*\.\s*o\s*\.\s*", "lo", normalized)
        match = re.search(r"\blo\s*(\d+(?:\.\d+)?)\b", clean)
        return f"LO{match.group(1)}" if match else None

    @staticmethod
    def resolve_assignment_part(phrase: str) -> str | None:
        """Normalize assignment sections to canonical PART_I..PART_IV."""
        if not phrase:
            return None
        normalized = _normalize_phrase(phrase)
        roman_match = re.search(r"\b(i{1,3}|iv)\b", normalized)
        if roman_match:
            return f"PART_{roman_match.group(1).upper()}"
        digit_match = re.search(r"\b([1-4])\b", normalized)
        if digit_match:
            mapping = {"1": "PART_I", "2": "PART_II", "3": "PART_III", "4": "PART_IV"}
            return mapping[digit_match.group(1)]
        return None

    def resolve_topic(self, phrase: str) -> str | None:
        """Normalize topic aliases to canonical topic IDs."""
        if not phrase:
            return None
        normalized = _normalize_phrase(phrase)
        canonical = TOPIC_IDS.get(normalized)
        if canonical is not None:
            return canonical
        topics_section = self.sections.get("TOPICS", {})
        if normalized in topics_section:
            return TOPIC_IDS.get(topics_section[normalized], topics_section[normalized])
        return None

    def resolve_resource_topic(self, phrase: str) -> str | None:
        """Normalize requested resource topics to canonical IDs."""
        if not phrase:
            return None
        normalized = _normalize_phrase(phrase)
        return RESOURCE_IDS.get(normalized)

    def resolve_rule(self, phrase: str) -> str | None:
        """Normalize regulation and policy topics to canonical rule IDs."""
        if not phrase:
            return None
        normalized = _normalize_phrase(phrase)
        return RULE_IDS.get(normalized)


def _normalize_phrase(text: str) -> str:
    """Normalize casing, Unicode NFC, quotes and whitespace for lexicon matching.

    This internal helper ensures entity normalization is fully self-contained
    and resilient, even if other pipeline stages are tested in isolation.
    """
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text).strip().lower()
    normalized = (
        normalized.replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("–", "-")
        .replace("—", "-")
    )
    tokens = re.findall(r"[^\W_]+(?:[./-][^\W_]+)*", normalized, re.UNICODE)
    return " ".join(tokens)