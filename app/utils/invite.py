# 10/30 생성 신규 파일
import random, string

ALPHABET = string.ascii_uppercase + string.digits

def new_code(length: int = 8) -> str:
    return "".join(random.choice(ALPHABET) for _ in range(length))
