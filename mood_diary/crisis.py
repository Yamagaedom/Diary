"""Conservative crisis signal detection and fixed safety copy (FR-006)."""

from __future__ import annotations

import re

CRISIS_GUIDANCE = (
    "지금 혼자 감당하지 않아도 괜찮아요. 당장 위험하거나 스스로를 해칠 가능성이 있다면 "
    "즉시 112 또는 119에 연락하거나 가까운 응급실로 가세요. 가능하다면 지금 믿을 수 있는 "
    "사람에게 곁에 있어 달라고 말하고, 자살예방상담전화 109 같은 전문기관에 연락해 주세요."
)

_PATTERNS = (
    r"죽고\s*싶", r"자살", r"극단적\s*선택", r"목숨을\s*끊", r"사라지고\s*싶",
    r"나를\s*해치", r"자해", r"살고\s*싶지\s*않",
)


def has_crisis_signal(content: str) -> bool:
    normalized = content.casefold()
    return any(re.search(pattern, normalized) for pattern in _PATTERNS)

