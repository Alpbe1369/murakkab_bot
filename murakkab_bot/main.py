import asyncio, json, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from app.config import BOT_TOKEN
from app.languages import texts

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Foydalanuvchi tilini saqlash ---
def save_user_language(user_id, lang_code):
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        data = json.load(f)
    data[str(user_id)] = lang_code
    with open("users.json", "w") as f:
        json.dump(data, f)

def get_user_language(user_id):
    if not os.path.exists("users.json"):
        return None
    with open("users.json", "r") as f:
        data = json.load(f)
    return data.get(str(user_id))

# --- Til tanlash tugmalari (inline) ---
def language_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O‘zbekcha", callback_data="lang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        ]
    ])

# --- Asosiy menyu (reply keyboard) ---
def get_main_menu(lang):
    buttons = texts[lang]["buttons"]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=buttons[0])],
            [KeyboardButton(text=buttons[1])],
            [KeyboardButton(text=buttons[2])],
        ],
        resize_keyboard=True
    )

# --- /start komandasi ---
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    lang = get_user_language(message.from_user.id)
    if lang:
        await message.answer(texts[lang]["start"], reply_markup=get_main_menu(lang))
    else:
        await message.answer(
            texts["uz"]["choose_language"],
            reply_markup=language_keyboard()
        )

# --- Til tanlanganda ---
@dp.callback_query(F.data.startswith("lang_"))
async def lang_selected(callback: CallbackQuery):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    save_user_language(user_id, lang_code)

    await callback.message.edit_text(texts[lang_code]["welcome"])
    await bot.send_message(
        chat_id=user_id,
        text=texts[lang_code]["menu"],
        reply_markup=get_main_menu(lang_code)
    )

# --- Tugmalar ishlov berish ---
@dp.message(F.text.in_(["📄 Ma’lumot", "📄 Информация"]))
async def info_handler(message: Message):
    await message.answer("🧪 Bot beta versiyada ishlayapti va kelajakda kengaytiriladi.")

@dp.message(F.text.in_(["📞 Aloqa", "📞 Контакт"]))
async def contact_handler(message: Message):
    await message.answer("📱 +998 XX XXX-XX-XX")

@dp.message(F.text.in_(["⚙️ Sozlamalar", "⚙️ Настройки"]))
async def settings_handler(message: Message):
    await message.answer("🔧 Iltimos, tilni tanlang:", reply_markup=language_keyboard())

# --- Noma'lum xabarlar ---
@dp.message()
async def fallback(message: Message):
    lang = get_user_language(message.from_user.id) or "uz"
    await message.answer("⚠️ Iltimos, menyudan foydalaning.")

# --- Botni ishga tushurish ---
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
