import re


def extract_bullet_points(text: str) -> list[str]:
    results = re.findall(r"-\s*(.+)", text)

    # if results:
    #     return "\n".join(f"- {x}" for x in results)

    return results
