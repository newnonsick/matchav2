import re

from config import ENTRY_OFFICE_KEYWORDS


def isStandUpMessageEntryOffice(text: str) -> bool:
    text_lower = text.lower()
    tasks = re.findall(r"-\s*(.*)", text_lower)

    return any(keyword in tasks for keyword in ENTRY_OFFICE_KEYWORDS)
