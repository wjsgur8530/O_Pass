import re

def is_valid_password(password):
    if len(password) < 8:
        return False
    
    # 최소 3종류 이상 포함하는지 검사
    categories = 0
    if re.search(r'[A-Z]', password):
        categories += 1
    if re.search(r'[a-z]', password):
        categories += 1
    if re.search(r'\d', password):
        categories += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        categories += 1
    if categories < 3:
        return False
    
    # 연속된 문자 사용 금지
    if re.search(r'(.)\1{3,}', password.lower()):
        return False
    
    return True

# 테스트
passwords = [
    "Abcdefgh",
    "12345678",
    "abcd1234",
    "Ab!2345",
    "aabbccdd",
    "Aaaa9672@@",
    "Jh119672@@"
]

for password in passwords:
    if is_valid_password(password):
        print(f"{password}: 유효한 비밀번호")
    else:
        print(f"{password}: 유효하지 않은 비밀번호")
