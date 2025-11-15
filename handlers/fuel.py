# -*- coding: utf-8 -*-
import telebot
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message

TANK_CAPACITY = 68  # литров

def calculate_fuel_liters(percentage):
    try:
        percentage = float(percentage)
        if percentage < 0 or percentage > 100:
            return None, "❌ Процент должен быть от 0 до 100"
        
        liters = (percentage / 100) * TANK_CAPACITY
        return round(liters, 1), None
    except ValueError:
        return None, "❌ Введите число"

def setup_fuel_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == '⛽ Расчет топлива')
    def handle_fuel_calc(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        response = f"""<b>⛽ РАСЧЕТ ТОПЛИВА</b>

━━━━━━━━━━━━━━━━━━━━
<b>📊 ИНФОРМАЦИЯ О БАКЕ</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Полный бак:</b> {TANK_CAPACITY} литров
• <b>100%</b> = {TANK_CAPACITY} литров
• <b>50%</b> = {TANK_CAPACITY/2} литров  
• <b>25%</b> = {TANK_CAPACITY/4} литров

━━━━━━━━━━━━━━━━━━━━
<b>💡 КАК ПОЛЬЗОВАТЬСЯ</b>
━━━━━━━━━━━━━━━━━━━━
Введите остаток топлива в процентах (от 0 до 100)

<b>Примеры:</b>
• <code>50</code> - для 50%
• <code>25.5</code> - для 25.5%
• <code>100</code> - для полного бака

⬇️ <b>Введите процент остатка топлива:</b>"""

        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            response,
            main_keyboard(user_id),
            log_action="fuel_calc",
            parse_mode="HTML"
        )
        bot.register_next_step_handler(message, process_fuel_percentage)
    
    def process_fuel_percentage(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        menu_buttons = ['🔍 Поиск водителей', '📞 Телефоны', '🚌 Маршруты', 
                       '🏥 Профосмотр', '🏢 Филиалы', '🌤️ Погода', 
                       '🔧 Текущий механик', '⛽ Расчет топлива', '📊 Статистика']
        
        if message.text in menu_buttons:
            return
        
        percentage = message.text.strip()
        liters, error = calculate_fuel_liters(percentage)
        
        if error:
            response = f"""❌ <b>Ошибка ввода</b>

{error}

━━━━━━━━━━━━━━━━━━━━
<b>💡 ПРАВИЛЬНЫЙ ФОРМАТ</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Целое число:</b> 50
• <b>Дробное число:</b> 25.5
• <b>Диапазон:</b> от 0 до 100

⬇️ <b>Попробуйте еще раз:</b>"""
            
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                parse_mode="HTML"
            )
            bot.register_next_step_handler(message, process_fuel_percentage)
        else:
            if liters == 0:
                fuel_emoji = "🪫"
                status = "БАК ПУСТОЙ"
            elif liters < TANK_CAPACITY * 0.25:
                fuel_emoji = "🟡"
                status = "МАЛО ТОПЛИВА"
            elif liters < TANK_CAPACITY * 0.5:
                fuel_emoji = "🟠" 
                status = "СРЕДНИЙ УРОВЕНЬ"
            elif liters < TANK_CAPACITY * 0.75:
                fuel_emoji = "🟢"
                status = "ДОСТАТОЧНО"
            else:
                fuel_emoji = "✅"
                status = "ПОЛНЫЙ БАК"
            
            response = f"""<b>⛽ РЕЗУЛЬТАТ РАСЧЕТА</b>

{fuel_emoji} <b>{status}</b>

━━━━━━━━━━━━━━━━━━━━
<b>📊 ДЕТАЛИ РАСЧЕТА</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Процент:</b> {percentage}%
• <b>Литры:</b> {liters} л
• <b>Полный бак:</b> {TANK_CAPACITY} л

━━━━━━━━━━━━━━━━━━━━
<b>💡 ПОЛЕЗНО ЗНАТЬ</b>
━━━━━━━━━━━━━━━━━━━━
• <b>100%</b> = {TANK_CAPACITY} л
• <b>50%</b> = {TANK_CAPACITY/2} л
• <b>25%</b> = {TANK_CAPACITY/4} л

🔄 <b>Новый расчет:</b> нажмите «⛽ Расчет топлива»"""

            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                log_action="fuel_calc_result",
                parse_mode="HTML"
            )