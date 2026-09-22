import random
import re


def generate_college_code(college_name: str) -> str:
    cleaned = re.sub(
        r"[^A-Za-z0-9\s]",
        "",
        college_name,
    )

    words = cleaned.upper().split()

    if len(words) == 1:
        prefix = words[0][:3]

    elif len(words) == 2:
        prefix = words[0][:2] + words[1][:1]

    else:
        prefix = "".join(
            word[0]
            for word in words[:3]
        )

    # Always exactly 3 letters
    prefix = re.sub(
        r"[^A-Z]",
        "",
        prefix,
    )

    prefix = prefix[:3].ljust(3, "X")

    # Exactly 3 digits
    number = random.randint(100, 999)

    return f"{prefix}{number}"