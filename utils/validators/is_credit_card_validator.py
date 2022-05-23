import re


def is_credit_card(text) -> bool:
    if not re.match(r'^(?:[0-9]{12,19})$', text):
        return False

    text = text or ''

    double = 0
    total = 0

    for i in range(len(text) - 1, -1, -1):
        for c in str((double + 1) * int(text[i])):
            total += int(c)
        double = (double + 1) % 2

    return (total % 10) == 0


