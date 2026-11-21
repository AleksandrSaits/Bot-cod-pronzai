import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
WEBAPP_URL = os.getenv("WEBAPP_URL", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в .env или переменных окружения")

if not WEBAPP_URL.startswith("https://"):
    raise RuntimeError("WEBAPP_URL должен начинаться с https:// (например, ссылка GitHub Pages)")


def main_menu_keyboard(webapp_url: str) -> InlineKeyboardMarkup:
    """Клавиатура под сообщением с кнопкой запуска Mini App."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚔️ Открыть «Пронзающие Мир»",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ],
            [
                InlineKeyboardButton(text="📜 О фракциях и боях", callback_data="info_rules"),
                InlineKeyboardButton(text="🔗 Помощь с запуском", callback_data="info_setup"),
            ],
        ]
    )


def quick_launch_reply_keyboard(webapp_url: str) -> ReplyKeyboardMarkup:
    """Постоянная кнопка запуска внизу экрана чата."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⚔️ Войти в игру", web_app=WebAppInfo(url=webapp_url))]
        ],
        resize_keyboard=True,
    )


async def handle_start(message: Message) -> None:
    user_name = message.from_user.first_name if message.from_user else "Владыка"
    text = (
        f"Приветствую, <b>{user_name}</b>!\n\n"
        "Ты вступаешь в мир <b>«Пронзающие Мир»</b> — собирай отряд 5v5 из "
        "<i>Небесных</i>, <i>Падших</i> и <i>Смертных</i>, повышай редкость героев "
        "каждые 50 уровней, открывай паки и поднимай свой MMR.\n\n"
        "Жми кнопку ниже, чтобы открыть игру:"
    )
    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(WEBAPP_URL),
    )
    await message.answer(
        "Кнопка быстрого входа закреплена в меню ввода.",
        reply_markup=quick_launch_reply_keyboard(WEBAPP_URL),
    )


async def handle_play_command(message: Message) -> None:
    await message.answer(
        "Запускай арену и собирай отряд:",
        reply_markup=main_menu_keyboard(WEBAPP_URL),
    )


async def handle_rules_callback(callback: CallbackQuery) -> None:
    text = (
        "<b>Как устроена игра:</b>\n"
        "• <b>3 фракции:</b> Небесные, Падшие, Смертные.\n"
        "• <b>5 редкостей:</b> от Смертного до Запретного, эволюция каждые 50 уровней.\n"
        "• <b>Бои 5v5:</b> скорость хода (SPD), криты, ультимейты и эффекты статусов.\n"
        "• <b>Дубликаты и Души:</b> повторки дают пробуждение звёзд (★) и Души для магазина."
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


async def handle_setup_callback(callback: CallbackQuery) -> None:
    text = (
        "<b>Подключение Mini App в @BotFather:</b>\n"
        "1. Открой <code>@BotFather</code> → выбери бота.\n"
        "2. Перейди в <b>Bot Settings → Menu Button</b> (или <b>Configure Mini App</b>).\n"
        f"3. Укажи URL: <code>{WEBAPP_URL}</code>\n"
        "4. Убедись, что на GitHub Pages включён HTTPS."
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


async def handle_webapp_data(message: Message) -> None:
    """Обработка данных, если фронт когда-нибудь отправит их через tg.sendData(...)."""
    raw = message.web_app_data.data if message.web_app_data else ""
    await message.answer(f"Получены данные из игры: <code>{raw}</code>", parse_mode="HTML")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(handle_start, CommandStart())
    dp.message.register(handle_play_command, Command("play"))
    dp.message.register(handle_webapp_data, F.web_app_data)
    dp.callback_query.register(handle_rules_callback, F.data == "info_rules")
    dp.callback_query.register(handle_setup_callback, F.data == "info_setup")

    await dp.start_polling(bot)


if __
