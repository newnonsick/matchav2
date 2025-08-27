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


def random_text(length=6):
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))
