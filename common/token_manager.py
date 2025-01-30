import os
import secrets

TOKEN_FILE = 'backend_api_token.txt'

def generate_token():
    """Генерирует новый токен и сохраняет его в файл."""
    token = secrets.token_hex(16)  # Генерирует 32-значный шестнадцатеричный токен
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)
    return token

def get_token():
    """Получает токен из файла, если он существует, или генерирует новый."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            token = f.read().strip()
            print(f"Читаем токен из файла: {token}")  # Логируем считанный токен
            return token
    else:
        return generate_token()  # Генерируем новый токен, если файл не существует
