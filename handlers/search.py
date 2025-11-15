# -*- coding: utf-8 -*-
import telebot
from database import user_db, employee_db
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message, get_cached_data, set_cached_data

def setup_search_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == '🔍 Поиск водителей')
    def handle_driver_search(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        if not user_db.is_registered(user_id):
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ <b>Для доступа к поиску необходима регистрация</b>",
                main_keyboard(user_id),
                log_action="search_denied",
                parse_mode="HTML"
            )
            return
        
        if not user_db.can_search_drivers(user_id):
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ <b>Доступ запрещен</b>\nПоиск доступен только сотрудникам компании",
                main_keyboard(user_id),
                log_action="search_denied_not_employee",
                parse_mode="HTML"
            )
            return
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            "🔍 <b>Введите данные для поиска:</b>\n\n💡 <i>Можно искать по имени, фамилии, телефону или табельному номеру</i>",
            main_keyboard(user_id),
            log_action="search_started",
            parse_mode="HTML"
        )
        bot.register_next_step_handler(message, process_driver_search)
    
    def process_driver_search(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        if message.text in ['🔍 Поиск водителей', '📞 Телефоны', '🚌 Маршруты', '🏥 Профосмотр', '🏢 Филиалы', '🌤️ Погода', '🔧 Текущий механик', '⛽ Расчет топлива', '📊 Статистика']:
            return
        
        # ВСЕГДА получаем свежие данные из базы (без кэширования поиска)
        drivers_data = employee_db.search_drivers(message.text)
        
        if not drivers_data:
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ <b>Водители не найдены</b>\n\n💡 <i>Попробуйте изменить запрос</i>",
                main_keyboard(user_id),
                log_action="search_no_results",
                parse_mode="HTML"
            )
        else:
            response = f"<b>🔍 Найдено водителей:</b> {len(drivers_data)}\n\n"
            for i, driver in enumerate(drivers_data[:10], 1):
                response += f"<b>👤 {driver.get('name', '')} {driver.get('surname', '')}</b>\n"
                response += f"📞 <a href='tel:{driver.get('phone', '')}'>{driver.get('phone', '')}</a>\n"
                response += f"🔢 Таб. <code>{driver.get('id', '')}</code>\n"
                if driver.get('route'):
                    response += f"🚍 Маршрут <b>{driver.get('route', '')}</b>\n"
                response += "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if len(drivers_data) > 10:
                response += f"💡 <i>Показано 10 из {len(drivers_data)} результатов</i>"
            
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                log_action="search_results",
                parse_mode="HTML"
            )