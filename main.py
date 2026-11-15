import asyncio
import logging
import os
import random
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sanewbot")

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required")

bot = Bot(token=TOKEN)
dp = Dispatcher()

JOKES = [
    "Почему программист не любит природу? Там слишком много багов 🌳",
    "— Бот, ты умный? — Я стараюсь, но иногда зависаю 🤖",
    "Что сказал ноль восьмёрке? Классный ремень! 😄",
]

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я Sanewbot — твой Telegram-бот. Напиши мне что-нибудь или используй /help."
    )

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Что я умею:\n"
        "/start — начать общение\n"
        "/help — список команд\n"
        "/joke — случайная шутка\n"
        "А ещё можешь просто написать мне сообщение."
    )

@dp.message(Command("joke"))
async def joke(message: Message):
    await message.answer(random.choice(JOKES))

@dp.message(F.text)
async def chat(message: Message):
    text = message.text.strip()
    lower = text.lower()
    if any(word in lower for word in ("привет", "здравствуй", "хай", "ку")):
        answer = "Привет! Рад тебя видеть 😊"
    elif "как дела" in lower:
        answer = "Отлично! Готов общаться 😎 А у тебя как?"
    elif "спасибо" in lower:
        answer = "Всегда пожалуйста! ❤️"
    elif "кто ты" in lower or "ты кто" in lower:
        answer = "Я Sanewbot — дружелюбный Telegram-бот 🤖"
    else:
        answer = "Я тебя услышал! Напиши /help, чтобы посмотреть мои команды 🙂"
    await message.answer(answer)

@asynccontextmanager
async def lifespan(app: FastAPI):
    polling_task = asyncio.create_task(dp.start_polling(bot))
    log.info("Sanewbot polling started")
    yield
    await dp.stop_polling()
    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass
    await bot.session.close()

app = FastAPI(title="Sanewbot", lifespan=lifespan)

@app.get("/")
async def health():
    return {"status": "ok", "bot": "Sanewbot"}
