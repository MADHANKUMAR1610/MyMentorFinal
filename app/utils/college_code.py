import random
import re


def generate_college_code(
    college_name: str,
) -> str:

    # Remove special characters
    cleaned = re.sub(
        r"[^A-Za-z0-9\s]",
        "",
        college_name,
    )

    words = cleaned.upper().split()

    # --------------------------------------------------------
    # Generate prefix
    # --------------------------------------------------------

    if len(words) == 1:

        prefix = words[0][:3]

    elif len(words) == 2:

        prefix = (
            words[0][:2]
            + words[1][:1]
        )

    else:

        prefix = "".join(
            word[0]
            for word in words[:3]
        )

    # Make sure prefix is at least 3 characters
    prefix = prefix[:3].ljust(
        3,
        "X",
    )

    # --------------------------------------------------------
    # Generate 4 digit number
    # --------------------------------------------------------

    number = random.randint(
        1000,
        9999,
    )

    return f"{prefix}{number}"