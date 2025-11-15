# -*- coding: utf-8 -*-
import telebot
from datetime import datetime, timedelta
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message

MECHANICS = [
    # ЦИКЛ 1: Барсуков (ночь) -> Калион (день)
    {
        "name": "Барсуков Антон",
        "phone": "+7(926)675-81-99", 
        "shift": "Ночная смена (20:00-08:00)"
    },
    {
        "name": "Калион Михаил Евдокимович",
        "phone": "+7(977)675-19-67",
        "shift": "Дневная смена (08:00-20:00)"
    },
    # ЦИКЛ 2: Фокин (ночь) -> Алексеенко (день)
    {
        "name": "Фокин Василий Михайлович",
        "phone": "+7(967)085-48-15",
        "shift": "Ночная смена (20:00-08:00)"
    },
    {
        "name": "Алексеенко Алексей Алексеевич", 
        "phone": "+7(926)040-34-69",
        "phone_extra": "+7(916)234-84-04",
        "shift": "Дневная смена (08:00-20:00)"
    }
]

def calculate_current_mechanic():
    now = datetime.now()
    current_time = now.time()
    
    # КОРРЕКЦИЯ ВРЕМЕНИ: UTC+3 (Москва)
    moscow_time = (now + timedelta(hours=3)).time()
    
    # Определяем базовый день (меняется в 08:00 МСК, а не в 00:00)
    base_date = now.date()
    if moscow_time < datetime.strptime("08:00", "%H:%M").time():
        # Если время до 08:00 МСК, считаем что это еще предыдущий день
        base_date = base_date - timedelta(days=1)
    
    # Простой цикл на основе даты
    day_number = base_date.toordinal()
    
    # Чередуем циклы каждые 2 дня
    cycle = (day_number // 2) % 2  # 0 или 1
    
    # Определяем смену по МОСКОВСКОМУ времени
    if moscow_time >= datetime.strptime("08:00", "%H:%M").time() and moscow_time < datetime.strptime("20:00", "%H:%M").time():
        # ДНЕВНАЯ СМЕНА (08:00-20:00 МСК)
        mechanic_index = 1 + (cycle * 2)  # Калион или Алексеенко
    else:
        # НОЧНАЯ СМЕНА (20:00-08:00 МСК)
        mechanic_index = 0 + (cycle * 2)  # Барсуков или Фокин
    
    return MECHANICS[mechanic_index]

def setup_mechanics_handlers(bot):
    @bot.message_handler(func=lambda m: m.text == '🔧 Текущий механик')
    def handle_current_mechanic(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        try:
            mechanic = calculate_current_mechanic()
            current_time = (datetime.now() + timedelta(hours=3)).strftime("%d.%m.%Y %H:%M")  # МСК время
            
            response = f"""<b>🔧 ТЕКУЩИЙ МЕХАНИК</b>

━━━━━━━━━━━━━━━━━━━━
<b>👨‍🔧 СЕЙЧАС РАБОТАЕТ</b>
━━━━━━━━━━━━━━━━━━━━

<b>👤 {mechanic['name']}</b>
📞 {mechanic['phone']}"""

            if 'phone_extra' in mechanic:
                response += f"\n📞 {mechanic['phone_extra']}"
            
            response += f"\n⏰ {mechanic['shift']}"

            response += f"""

━━━━━━━━━━━━━━━━━━━━
<b>⚙️ ИНФОРМАЦИЯ О ГРАФИКЕ</b>
━━━━━━━━━━━━━━━━━━━━

• <b>График работы:</b> 2/2
• <b>Смены:</b> дневная (08:00-20:00), ночная (20:00-08:00)
• <b>Количество механиков:</b> 4 в ротации
• <b>Ночные смены:</b> Барсуков Антон, Фокин Василий
• <b>Дневные смены:</b> Калион Михаил, Алексеенко Алексей

━━━━━━━━━━━━━━━━━━━━
<b>⚠️ ВАЖНАЯ ИНФОРМАЦИЯ</b>
━━━━━━━━━━━━━━━━━━━━

‼️ <b>ВНИМАНИЕ:</b> Данные предоставляются по штатному расписанию.
   Не учитываются:
   • Отпуска
   • Больничные листы  
   • Внеплановые замены
   • Командировки

━━━━━━━━━━━━━━━━━━━━
<b>📞 ДЛЯ УТОЧНЕНИЯ</b>
━━━━━━━━━━━━━━━━━━━━

💡 Для актуальной информации звоните:
   📞 +7(495)950-40-00 доб. 17058

🕐 <i>Обновлено: {current_time} МСК</i>"""

            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                log_action="current_mechanic",
                parse_mode="HTML"
            )
            
        except Exception as e:
            print(f"❌ Ошибка определения механика: {e}")
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ <b>Не удалось определить текущего механика</b>\nПопробуйте позже",
                main_keyboard(user_id),
                parse_mode="HTML"
            )