import random
import re
import string


def convert_string_to_snake_case(string: str) -> str:
    string = re.sub(r"[\s\-]+", "_", string.strip())

    if string.isupper():
        return string.lower()

    string = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", string)

    return string.lower()


def remove_special_characters(string: str, allowed: str = "_") -> str:
    pattern = rf"[^\w{re.escape(allowed)}]"
    return re.sub(pattern, "", string, flags=re.UNICODE)


def make_name_safe(name: str) -> str:
    return convert_string_to_snake_case(remove_special_characters(name))

def random_text(length: int = 5, include_chars: list[str] | None = None) -> str:
    characters = string.ascii_uppercase + string.digits

    if include_chars:
        char_pool = list(set(characters + "".join(include_chars)))

        result_list = random.choices(char_pool, k=length)

        included_char_present = any(c in include_chars for c in result_list)
        if not included_char_present:
            result_list[random.randint(0, length - 1)] = random.choice(include_chars)

        return "".join(result_list)
    else:
        return "".join(random.choice(characters) for _ in range(length))

