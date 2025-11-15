# -*- coding: utf-8 -*-
import telebot
import time
from config import BOT_TOKEN

if not BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не найден")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

print("🔄 Настройка обработчиков...")

try:
    from handlers.start import setup_start_handlers
    from handlers.register import setup_register_handlers
    from handlers.search import setup_search_handlers
    from handlers.phones import setup_phones_handlers
    from handlers.weather import setup_weather_handlers
    from handlers.other import setup_other_handlers
    from handlers.mechanics import setup_mechanics_handlers
    from handlers.fuel import setup_fuel_handlers
    from handlers.admin import setup_admin_handlers
    from handlers.daily_fines import setup_daily_fines_handlers  # Новый обработчик

    setup_start_handlers(bot)
    setup_register_handlers(bot)
    setup_search_handlers(bot)
    setup_phones_handlers(bot)
    setup_weather_handlers(bot)
    setup_other_handlers(bot)
    setup_mechanics_handlers(bot)
    setup_fuel_handlers(bot)
    setup_admin_handlers(bot)
    setup_daily_fines_handlers(bot)  # Добавляем новый обработчик

    print("✅ Обработчики настроены")

    # Запускаем планировщик ежедневных штрафов
    from fines_scheduler import schedule_daily_fine  # ← ИЗМЕНИТЬ
    schedule_daily_fine(bot)
    print("✅ Планировщик штрафов запущен")

except Exception as e:
    print(f"❌ Ошибка настройки обработчиков: {e}")
    exit(1)

print("✅ Бот запущен!")

while True:
    try:
        bot.polling(none_stop=True, interval=1)
    except Exception as e:
        print(f"❌ Ошибка: {e}. Перезапуск через 5 секунд...")
        time.sleep(5)