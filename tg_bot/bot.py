import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import logging
import config  # Импортируем конфигурацию

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для отправки запроса к бэкенду
def send_to_backend(imei):
    payload = {"imei": imei, "token": config.API_TOKEN}
    response = requests.post(config.BACKEND_URL, json=payload)
    return response.json()

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Введите IMEI для проверки.")

# Обработчик текстовых сообщений (IMEI)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"User  ID: {user_id}")  # Логируем ID пользователя в консоли

    # Проверяем, есть ли пользователь в белом списке
    if user_id not in config.WHITELIST:
        await update.message.reply_text("У вас нет доступа. Ваш ID не в белом списке.")
        return

    imei = update.message.text
    if not imei.isdigit() or len(imei) != 15:
        await update.message.reply_text("Некорректный IMEI. IMEI должен состоять из 15 цифр.")
        return

    # Отправляем IMEI на бэкенд
    result = send_to_backend(imei)
    logger.info(f"Response from backend: {result}")

    # Проверка результата
    if "error" in result:
        await update.message.reply_text(f"Ошибка: {result['error']}")
    else:
        # Формируем ответ с информацией о IMEI
        properties = result.get('properties', {})
        imei_info = f"IMEI: {properties.get('imei', 'Не указано')}\n"
        imei_info += f"Статус: {result.get('status', 'Не указано')}\n"
        imei_info += f"Модель: {properties.get('deviceName', 'Не указана')}\n"
        imei_info += f"Регион: {properties.get('apple/region', 'Не указана')}\n"
        await update.message.reply_text(imei_info)

# Основная функция для запуска бота
def main():
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
