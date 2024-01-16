import math
import random

MAX_INT_32: int = 2**31 - 1

def random_id() -> int:
    return random.randint(0, MAX_INT_32)