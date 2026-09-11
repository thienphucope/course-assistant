"""Entity lexicon loader and canonicalization rules."""

from __future__ import annotations

import re
from pathlib import Path

from .tokenizer import normalized_phrase


TOPIC_IDS = {
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

RESOURCE_IDS = {
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
}

RULE_IDS = {
    "llm/rag": "LLM_RAG",
    "llm": "LLM_RAG",
    "rag": "LLM_RAG",
    "công cụ ai": "AI_USAGE",
    "ai": "AI_USAGE",
    "sử dụng ai": "AI_USAGE",
    "thư viện ngoài": "EXTERNAL_LIBRARIES",
    "mã nguồn": "SOURCE_CODE",
    "source code": "SOURCE_CODE",
    "liêm chính học thuật": "ACADEMIC_INTEGRITY",
    "chia sẻ bài làm": "ASSIGNMENT_SHARING",
}


class EntityLexicon:
    """Loads the supplied lexicon and exposes deterministic canonical IDs."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.sections = self._load(self.path)

    @staticmethod
    def _load(path: Path) -> dict[str, dict[str, str]]:
        sections: dict[str, dict[str, str]] = {}
        current: str | None = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or set(line) == {"="} or line.startswith("COURSE ASSISTANT"):
                continue
            if line.isupper() and "=" not in line:
                current = line
                sections.setdefault(current, {})
                continue
            if current and "=" in line:
                alias, canonical = (part.strip() for part in line.split("=", 1))
                sections[current][normalized_phrase(alias)] = canonical
            elif current == "INTENTS":
                sections[current][normalized_phrase(line)] = line
        return sections

    def resolve_course(self, phrase: str) -> str | None:
        value = normalized_phrase(phrase)
        aliases = self.sections.get("COURSE", {})
        return "CO3085" if value in aliases else None

    def resolve_topic(self, phrase: str) -> str | None:
        return TOPIC_IDS.get(normalized_phrase(phrase))

    def resolve_resource_topic(self, phrase: str) -> str | None:
        return RESOURCE_IDS.get(normalized_phrase(phrase))

    def resolve_rule(self, phrase: str) -> str | None:
        return RULE_IDS.get(normalized_phrase(phrase))

    @staticmethod
    def resolve_week(phrase: str) -> str | None:
        match = re.search(r"\d+", phrase)
        return f"WEEK_{int(match.group()):02d}" if match else None

    @staticmethod
    def resolve_chapter(phrase: str) -> str | None:
        match = re.search(r"\d+", phrase)
        return f"CH{int(match.group()):02d}" if match else None

    @staticmethod
    def resolve_lo(phrase: str) -> str | None:
        match = re.search(r"lo\s*(\d+(?:\.\d+)?)", normalized_phrase(phrase))
        return f"LO{match.group(1)}" if match else None

    @staticmethod
    def resolve_assignment_part(phrase: str) -> str | None:
        roman_match = re.search(r"\b(i{1,3}|iv)\b", normalized_phrase(phrase))
        return f"PART_{roman_match.group(1).upper()}" if roman_match else None

