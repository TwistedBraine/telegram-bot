# -*- coding: utf-8 -*-
import telebot
from database import user_db
from keyboards import main_keyboard
from utils import send_message_with_cleanup, save_user_message, get_cached_data, set_cached_data

def is_admin(user_id):
    return user_id == 130123754

def find_employee_name(phone):
    """Находит имя сотрудника по номеру"""
    from database import user_db
    return user_db.find_employee_name(phone)

def setup_admin_handlers(bot):

    @bot.message_handler(commands=['myid'])
    def handle_myid(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)

        response = f"""<b>🆔 ВАШ TELEGRAM ID</b>

👤 <b>Ваше имя:</b> {message.from_user.first_name}
🔢 <b>Ваш ID:</b> <code>{user_id}</code>
{"👑 <b>Статус:</b> АДМИНИСТРАТОР" if is_admin(user_id) else "👤 <b>Статус:</b> пользователь"}"""

        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            response,
            main_keyboard(user_id),
            parse_mode="HTML"
        )

    @bot.message_handler(commands=['testphone'])
    def test_phone(message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            return

        from database import user_db

        test_numbers = [
            "89161234567",
            "+79161234567", 
            "9161234567",
            "8(916)123-45-67",
            "1234567890"
        ]

        result = "<b>🧪 Тест нормализации номеров:</b>\n\n"
        for phone in test_numbers:
            normalized = user_db.normalize_phone(phone)
            result += f"📱 {phone} → {normalized}\n"

        bot.send_message(message.chat.id, result, parse_mode="HTML")

    @bot.message_handler(commands=['myphone'])
    def my_phone(message):
        user_id = message.from_user.id
        from database import user_db

        phone = user_db.get_user_phone(user_id)
        if phone:
            normalized = user_db.normalize_phone(phone)
            is_emp = user_db.is_employee(phone)

            response = f"""<b>📱 Ваш номер в базе</b>

• <b>Исходный:</b> {phone}
• <b>Нормализованный:</b> {normalized}
• <b>Сотрудник:</b> {'✅ Да' if is_emp else '❌ Нет'}"""
        else:
            response = "❌ <b>Вы не зарегистрированы</b>"

        bot.send_message(message.chat.id, response, parse_mode="HTML")

    @bot.message_handler(commands=['checkdb'])
    def check_db(message):
        user_id = message.from_user.id
        if user_id != 130123754:
            return

        from database import employee_db

        result = "<b>📊 ПРОВЕРКА БАЗЫ:</b>\n\n"
        result += f"👥 <b>Водителей:</b> {len(employee_db.drivers)}\n"
        result += f"👔 <b>Руководителей:</b> {len(employee_db.managers)}\n" 
        result += f"🔧 <b>Механиков:</b> {len(employee_db.mechanics)}\n\n"

        # Покажем первые 3 номера из каждой базы
        result += "<b>📱 Номера водителей:</b>\n"
        for driver in employee_db.drivers[:3]:
            result += f"• {driver.get('phone')}\n"

        result += "\n<b>📱 Номера руководителей:</b>\n"
        for manager in employee_db.managers[:3]:
            result += f"• {manager.get('phone')}\n"

        bot.send_message(message.chat.id, result, parse_mode="HTML")

    @bot.message_handler(commands=['changelog'])
    def handle_changelog(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)

        changelog_text = """<b>📋 ИСТОРИЯ ИЗМЕНЕНИЙ БОТА</b>
<b>Версия 2.2</b> • Октябрь 2025

━━━━━━━━━━━━━━━━━━━━
<b>🕐 ХРОНОЛОГИЯ ОБНОВЛЕНИЙ</b>
━━━━━━━━━━━━━━━━━━━━

<u>Октябрь 2025</u>
• <b>v2.2.0</b> - Стабильная версия с исправлениями
  └─ Исправлено время смен механиков
  └─ Решена проблема вылетов на Android
  └─ Номера телефонов стали кликабельными
  └─ Отключен предпросмотр ссылок

• <b>v2.1.0</b> - Добавлена система ежедневных штрафов ПДД
  └─ Полная база штрафов ГИБДД (45 статей)
  └─ Автоматическая рассылка в 10:00
  └─ Кнопка "🚨 Штраф дня" для ручного просмотра
  └─ Автоудаление предыдущих сообщений

• <b>v2.0.1</b> - Добавлен changelog системы
• <b>v2.0.0</b> - Стабильная версия бота
  └─ Полная база водителей (127 сотрудников)
  └─ Система ротации механиков
  └─ Расчет топлива с визуализацией
  └─ Погода с рекомендациями для водителей
  └─ Телефонные справочники парка
  └─ Статистика использования
  └─ Система кэширования данных

━━━━━━━━━━━━━━━━━━━━
<b>⚙️ ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ</b>
━━━━━━━━━━━━━━━━━━━━

• <b>База данных:</b> SQLite + CSV
• <b>Пользователей:</b> 31+
• <b>Записей в базе:</b> 127 водителей + 45 штрафов
• <b>Функций:</b> 9 основных модулей
• <b>Кэширование:</b> погода, поиск, статистика
• <b>Стабильность:</b> исправлены критические баги

━━━━━━━━━━━━━━━━━━━━
<b>👨‍💻 РАЗРАБОТЧИК</b>
━━━━━━━━━━━━━━━━━━━━

• <b>Семенов Александр</b> (таб. 2586)
• Водитель 6-й автоколонны
• Маршрут 604

💡 <i>Бот создан водителем для водителей</i>"""

        send_message_with_cleanup(
            bot, user_id, message.chat.id,
            changelog_text,
            main_keyboard(user_id),
            parse_mode="HTML"
        )

    @bot.message_handler(func=lambda m: m.text == '📊 Статистика' and is_admin(m.from_user.id))
    def handle_stats(message):
        user_id = message.from_user.id
        save_user_message(user_id, message.message_id, message.chat.id)

        # Проверяем кэш
        cache_key = f"stats_{user_id}"
        cached_response = get_cached_data(cache_key)
        
        if cached_response:
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                cached_response,
                main_keyboard(user_id),
                parse_mode="HTML"
            )
            return

        try:
            stats = user_db.get_stats()

            response = f"""<b>📊 СТАТИСТИКА БОТА</b>
Управление: Семенов Александр (таб. 2586)

━━━━━━━━━━━━━━━━━━━━
<b>📈 ОБЩАЯ СТАТИСТИКА</b>
━━━━━━━━━━━━━━━━━━━━

👥 <b>Всего пользователей:</b> {stats['total_users']}
🔢 <b>Всего действий:</b> {stats['total_actions']}

━━━━━━━━━━━━━━━━━━━━
<b>🏆 ПОПУЛЯРНЫЕ ДЕЙСТВИЯ</b>
━━━━━━━━━━━━━━━━━━━━"""

            for action, count in stats['popular_actions']:
                action_name = {
                    'admin_stats': '📊 Просмотр статистики',
                    'start': '🚀 Запуск бота',
                    'start_unregistered': '🚀 Запуск (незарегистрирован)',
                    'fuel_calc': '⛽️ Расчёт топлива',
                    'search_started': '🔍 Поиск (начало)',
                    'search_results': '🔍 Поиск (результаты)',
                    'search_drivers': '🔍 Поиск водителей',
                    'search_denied': '🔍 Поиск водителей (отклонено)',
                    'current_mechanic': '🔧 Текущий механик',
                    'phones_menu': '📞 Меню телефонов',
                    'phones_park': '🏢 Телефоны парка',
                    'phones_management': '👔 Телефоны руководства',
                    'phones_glonass': '🛰️ Телефоны ГЛОНАСС',
                    'routes': '🚌 Маршруты',
                    'medical': '🏥 Профосмотр',
                    'branches': '🏢 Филиалы',
                    'weather': '🌤️ Погода',
                    'registration_success': '✅ Успешная регистрация'
                }.get(action, action)

                response += f"\n• {action_name}: <b>{count}</b>"

            response += "\n\n━━━━━━━━━━━━━━━━━━━━\n<b>👤 АКТИВНЫЕ ПОЛЬЗОВАТЕЛИ</b>\n━━━━━━━━━━━━━━━━━━━━"

            # Показываем всех пользователей, ИСКЛЮЧАЯ админа (тебя)
            active_users_displayed = 0
            for row in stats['active_users']:
                active_user_id = row[0]
                username = row[1] 
                phone = row[2]
                count = row[3]
                
                # ПРОПУСКАЕМ админа (тебя) - ID 130123754
                if active_user_id == 130123754:
                    continue
                    
                # Ограничиваем топ-10
                if active_users_displayed >= 10:
                    break
                    
                real_name = find_employee_name(phone)
                
                if real_name:
                    display_name = real_name
                elif username and username != "User":
                    display_name = username
                else:
                    display_name = f"ID_{active_user_id}"
                
                response += f"\n• {display_name}: <b>{count}</b> действий"
                active_users_displayed += 1

            response += "\n\n💡 <i>Статистика обновляется в реальном времени</i>"

            # Сохраняем в кэш
            set_cached_data(cache_key, response)

            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                response,
                main_keyboard(user_id),
                parse_mode="HTML"
            )

        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            send_message_with_cleanup(
                bot, user_id, message.chat.id,
                "❌ <b>Не удалось получить статистику</b>\nПопробуйте позже",
                main_keyboard(user_id),
                parse_mode="HTML"
            )

        @bot.message_handler(commands=['getchatid'])
        def handle_get_chat_id(message):
            user_id = message.from_user.id
            chat_id = message.chat.id
            chat_type = message.chat.type
        
            response = f"""🆔 <b>ИНФОРМАЦИЯ О ЧАТЕ</b>

👤 <b>Ваш User ID:</b> <code>{user_id}</code>
💬 <b>Chat ID:</b> <code>{chat_id}</code>
📋 <b>Тип чата:</b> {chat_type}
👥 <b>Название:</b> {message.chat.title or 'Личные сообщения'}"""

        bot.send_message(
            chat_id, 
            response, 
            parse_mode="HTML",
            disable_web_page_preview=True
        )