import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import openai

# ==== КОНФИГ ====
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAID_USERS = os.getenv("PAID_USERS", "").split(",")

# ==== НАСТРОЙКА ====
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
openai.api_key = OPENAI_API_KEY

# ==== КНОПКИ ====
def get_main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Отправить тест", callback_data="send_test")],
        [InlineKeyboardButton(text="💳 Оплатить подписку", url="https://send.monobank.ua/jar/KXTxqn73Y")]
    ])

# ==== ОБРАБОТЧИКИ ====
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    if user_id in PAID_USERS:
        await message.answer("Привет! Отправь мне тест текстом или файлом, и я помогу с ответами ✍️")
    else:
        await message.answer(
            "👋 Привет! Я бот, который помогает решать тесты.\n\n"
            "💵 Стоимость — 250 грн навсегда. После оплаты тебе будет открыт доступ.\n\n"
            "👇 Кнопки ниже", reply_markup=get_main_kb()
        )

@dp.message()
async def handle_message(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in PAID_USERS:
        await message.answer("🚫 Сначала оплатите подписку, чтобы использовать бота.")
        return

    text = message.text
    if not text:
        await message.answer("Пожалуйста, отправь тест текстом.")
        return

    await message.answer("🔍 Обрабатываю тест, подожди секунду...")

    prompt = f"Ответь на тест, объясни если нужно. Вот тест:\n{text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ты помощник по тестам. Отвечай точно и кратко."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        await message.answer(reply, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await message.answer(f"❌ Ошибка при обращении к ИИ: {str(e)}")

# ==== ЗАПУСК ====
if __name__ == '__main__':
    import asyncio
    asyncio.run(dp.start_polling(bot))
