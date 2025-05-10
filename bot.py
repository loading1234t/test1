import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# --- Конфигурация
API_TOKEN = "7624021359:AAGoDzEYgnBcVjlTf_RBYatJxgdNH4D-pd4"
ADMIN_ID = 638679272  # Замените на свой Telegram ID

# --- Логирование
logging.basicConfig(level=logging.INFO)

# --- Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- Команда /start
@dp.message_handler(commands=['start'])
async def send_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    web_app = WebAppInfo(url="https://loading1234t.github.io/my-website/")  # Замените на свою ссылку
    keyboard.add(types.KeyboardButton(text="Открыть маркет", web_app=web_app))
    await message.answer("Нажмите кнопку ниже, чтобы открыть маркет:", reply_markup=keyboard)

# --- Обработка WebApp событий (чат или заказ)
@dp.message_handler(content_types=types.ContentType.WEB_APP_DATA)
async def handle_webapp_data(message: types.Message):
    data = message.web_app_data.data
    user = message.from_user

    if data == "chat":
        await bot.send_message(
            ADMIN_ID,
            f"💬 Новый запрос на ЧАТ!\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"🔗 @{user.username or 'Без username'}\n"
            f"🆔 ID: <code>{user.id}</code>",
            parse_mode="HTML"
        )
        await message.answer("✅ Мы отправили ваше сообщение продавцу.")

    elif data == "order":
        order_number = random.randint(10000, 99999)
        await bot.send_message(
            ADMIN_ID,
            f"📦 Новый заказ с сайта!\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"🔗 @{user.username or 'Без username'}\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"🔢 Номер заказа: #{order_number}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("Я выполнил(а)", callback_data=f"done:{order_number}")
            )
        )
        await message.answer(f"✅ Заказ #{order_number} отправлен продавцу.")

# --- Ручная покупка через команду
@dp.message_handler(Text(startswith="buy:"))
async def handle_buy(message: types.Message):
    game_title = message.text.replace("buy:", "")
    confirm_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Да", callback_data=f"confirm:{game_title}"),
        InlineKeyboardButton("Отмена", callback_data="cancel")
    )
    await message.answer(f"Вы хотите купить {game_title}?", reply_markup=confirm_keyboard)

# --- Подтверждение покупки
@dp.callback_query_handler(Text(startswith="confirm:"))
async def handle_confirm(call: types.CallbackQuery):
    game_title = call.data.replace("confirm:", "")
    order_number = random.randint(10000, 99999)
    await bot.send_message(
        ADMIN_ID,
        f"📦 Новый заказ: {game_title}\n🔢 Номер заказа: #{order_number}",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Я выполнил(а)", callback_data=f"done:{order_number}")
        )
    )
    await call.message.answer(f"Ваш заказ #{order_number} создан, продавец получил уведомление.")
    await call.answer()

# --- Отмена покупки
@dp.callback_query_handler(Text(equals="cancel"))
async def handle_cancel(call: types.CallbackQuery):
    await call.message.answer("❌ Покупка отменена.")
    await call.answer()

# --- Продавец завершил заказ
@dp.callback_query_handler(Text(startswith="done:"))
async def handle_done(call: types.CallbackQuery):
    order_number = call.data.replace("done:", "")
    await call.message.answer(f"✅ Заказ #{order_number} помечен как выполненный.\nОжидаем подтверждение от покупателя.")
    await bot.send_message(
        call.from_user.id,
        f"📦 Продавец сообщил, что заказ #{order_number} выполнен.\nПожалуйста, подтвердите выполнение.",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("Проверить заказ и подтвердить", callback_data=f"confirm_finish:{order_number}")
        )
    )
    await call.answer()

# --- Финальное подтверждение от покупателя
@dp.callback_query_handler(Text(startswith="confirm_finish:"))
async def confirm_finish(call: types.CallbackQuery):
    order_number = call.data.replace("confirm_finish:", "")
    await bot.send_message(ADMIN_ID, f"✅ Покупатель подтвердил выполнение заказа #{order_number}.\n💰 Средства переведены продавцу.")
    await call.message.answer(f"Спасибо! Заказ #{order_number} успешно завершён.")
    await call.answer()

# --- Ручной чат через команду /chat
@dp.message_handler(commands=['chat'])
async def handle_chat(message: types.Message):
    chat_keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Написать продавцу", callback_data="chat_with_seller")
    )
    await message.answer("Нажмите, чтобы связаться с продавцом:", reply_markup=chat_keyboard)

@dp.callback_query_handler(Text(equals="chat_with_seller"))
async def chat_with_seller(call: types.CallbackQuery):
    try:
        await bot.send_message(ADMIN_ID, f"💬 Пользователь {call.from_user.full_name} хочет пообщаться.")
        await call.answer("Ваш запрос отправлен продавцу.")
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения продавцу: {e}")
        await call.message.answer("❌ Произошла ошибка. Попробуйте позже.")

# --- Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
