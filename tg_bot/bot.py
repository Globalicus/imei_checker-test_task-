import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import logging
from database import init_db, add_user, is_user_in_whitelist  # Импортируем функции работы с БД
import config  # Импортируем конфигурацию

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация базы данных
init_db()

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

    imei = update.message.text
    if not imei.isdigit() or len(imei) != 15:
        await update.message.reply_text("Некорректный IMEI. IMEI должен состоять из 15 цифр.")
        return

    # Проверяем, есть ли пользователь в белом списке
    if not is_user_in_whitelist(user_id):
        keyboard = [
            [InlineKeyboardButton("ДОБАВИТЬ", callback_data='add_user')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Вы не можете использовать бота, так как не находитесь в белом списке. Если вы хотите добавить свой номер в белый список, нажмите кнопку ниже:", reply_markup=reply_markup)
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

# Обработчик нажатия кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Отвечаем на нажатие кнопки

    if query.data == 'add_user':
        user_id = query.from_user.id
        if not is_user_in_whitelist(user_id):
            add_user(user_id)  # Добавляем ID пользователя в белый список в базе данных
            await query.edit_message_text(text="Вы добавлены в белый список! Теперь вы можете использовать бота. Введите IMEI для проверки.")
        else:
            await query.edit_message_text(text="Вы уже в белом списке!")

# Основная функция для запуска бота
def main():
    application = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button))  # Добавляем обработчик кнопок

    application.run_polling()

if __name__ == "__main__":
    main()
