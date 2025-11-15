# -*- coding: utf-8 -*-
import telebot
from keyboards import phones_keyboard, main_keyboard
from utils import send_message_with_cleanup, save_user_message

def setup_phones_handlers(bot):
    
    @bot.message_handler(func=lambda m: m.text == '📞 Телефоны')
    def handle_phones(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            "<b>📞 Выберите раздел:</b>",
            phones_keyboard(),
            parse_mode="HTML"
        )
    
    @bot.message_handler(func=lambda m: m.text == '📞 Телефоны парка')
    def handle_park_phones(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        text = """<b>🏢 ТЕЛЕФОНЫ ПАРКА</b>

📞 <b>Главный номер:</b>
+7(495)950-40-00

━━━━━━━━━━━━━━━━━━━━
<b>Диспетчерские:</b>
━━━━━━━━━━━━━━━━━━━━
• 16900, 6752 - Диспетчер выпуска
• 17063 - ЦУП
• 14154 - Расчетная часть 6АЭД

━━━━━━━━━━━━━━━━━━━━
<b>Мобильные:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Диспетчер выпуска:</b>
  +7(919)784-00-70
• <b>Диспетчер ЦУП:</b>
  +7(985)169-90-15
• <b>Начальник смены:</b>
  +7(985)169-90-14
• <b>АСДУ:</b>
  +7(985)169-90-13
• <b>КАМАЗ:</b>
  +7(985)400-36-02

━━━━━━━━━━━━━━━━━━━━
<b>Ситуационный центр:</b>
━━━━━━━━━━━━━━━━━━━━
+7(495)951-20-23

⏰ <b>Круглосуточно</b>"""
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            text,
            main_keyboard(user_id),
            parse_mode="HTML"
        )
    
    @bot.message_handler(func=lambda m: m.text == '👔 Телефоны руководства')
    def handle_management_phones(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        text = """<b>👔 РУКОВОДСТВО КОЛОННЫ</b>

━━━━━━━━━━━━━━━━━━━━
<b>Начальник колонны:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Величкин Сергей Дмитриевич</b>
• +7(999)991-24-21

━━━━━━━━━━━━━━━━━━━━
<b>Зам. по эксплуатации:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Карпов Виктор Сергеевич</b>
• +7(985)834-97-57

━━━━━━━━━━━━━━━━━━━━
<b>Зам. по технической части:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Яковлев Алексей Вячеславович</b>
• +7(903)523-38-21

━━━━━━━━━━━━━━━━━━━━
<b>Старший механик:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Татарников Андрей Анатольевич</b>
• +7(925)874-09-11

━━━━━━━━━━━━━━━━━━━━
<b>Ведущий инженер:</b>
━━━━━━━━━━━━━━━━━━━━
• <b>Федотова Тамара Арменовна</b>
• +7(977)340-72-13

━━━━━━━━━━━━━━━━━━━━
<b>Механик колонны:</b>
━━━━━━━━━━━━━━━━━━━━
+7(495)950-40-00 доб. 17058

⏰ <b>Пн-Пт: 08:00-17:00</b>"""
        
        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            text,
            main_keyboard(user_id),
            parse_mode="HTML"
        )
    
    @bot.message_handler(func=lambda m: m.text == '🛰️ Телефоны ГЛОНАСС')
    def handle_glonass_phones(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)
        
        text = """<b>🛰️ ТЕЛЕФОНЫ ГЛОНАСС</b>

📞 <b>Главный номер:</b>
+7(495)787-43-30

━━━━━━━━━━━━━━━━━━━━
<b>📞 ВСЕ ОПЕРАТОРЫ</b>
━━━━━━━━━━━━━━━━━━━━
4254 - 72
4264 - 167, 563, 76  
4265 - 76, 149
4275 - <b>H6</b>, <b>E59</b>, <b>353</b>
4276 - 447, 763
4277 - T36, 170, 604
4278 - 154
4263 - H9, M44K, 136, 586
4279 - M54

4121 - <b>Старший диспетчер</b>

⏰ <b>Круглосуточно</b>"""

        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            text,
            main_keyboard(user_id),
            parse_mode="HTML"
        )