import random
import string

ALPHABET = string.ascii_letters + string.digits  # Base62-ish

def generate_code(length: int = 6) -> str:
    return "".join(random.choices(ALPHABET, k=length))