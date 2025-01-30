import requests
import os
import json
from flask import Flask, request, jsonify

from backend.config import IMEI_CHECK_API_TOKEN
from database import init_db, is_user_in_whitelist

app = Flask(__name__)

# Токены
# SANDBOX_TOKEN = 'e4oEaZY1Kom5OXzybETkMlwjOCy3i8GSCGTHzWrhd4dc563b'

# Пример функции для получения токена (замените на вашу реализацию)
def get_token():
    # Укажите правильный путь к файлу с токеном
    file_path = r'D:\IT Python Project`s\flaskProject\tg_bot\backend_api_token.txt'
    print(f"Проверяем наличие файла: {file_path}")

    if not os.path.exists(file_path):
        print("Файл не найден.")
        return None

    with open(file_path, 'r') as file:
        token = file.read().strip()
        print("Токен успешно прочитан.")
        return token

@app.route('/api/check-imei', methods=['POST'])
def check_imei():
    data = request.json
    imei = data.get('imei')
    token = data.get('token')

    # Проверка токена
    if token != get_token():
        return jsonify({'error': 'Unauthorized'}), 401

    # Заголовки для запроса
    headers = {
        'Authorization': f'Bearer {IMEI_CHECK_API_TOKEN}',  # Используем токен для аутентификации
        'Content-Type': 'application/json'
    }

    # Данные для отправки
    body = json.dumps({
        "deviceId": "356735111052198",
        "serviceId": 12
    })

    # Логируем информацию о запросе
    print(f"Отправка POST-запроса на API IMEI Check:")
    print(f"URL: https://api.imeicheck.net/api/check")
    print(f"Заголовки: {headers}")
    print(f"Данные: {body}")

    url = 'https://api.imeicheck.net/v1/checks'
    # Проверка IMEI
    response = requests.post(url, headers=headers, data=body)

    # Отладочная информация
    print(f"Response status code: {response.status_code}")
    print(f"Response text: {response.text}")

    # Проверяем, был ли ответ успешным
    if response.status_code != 201:
        return jsonify({'error': 'Failed to check IMEI', 'status_code': response.status_code, 'response_text': response.text}), response.status_code

    # Обработка ответа от внешнего API
    try:
        return jsonify(response.json())
    except ValueError:
        return jsonify({'error': 'Invalid JSON response', 'response_text': response.text}), 500

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
