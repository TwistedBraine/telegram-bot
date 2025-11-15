# -*- coding: utf-8 -*-
import sqlite3
import csv
import os
from datetime import datetime

class UserDatabase:
    def __init__(self, db_name='users.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_table()
        self.employee_db = None
    
    def set_employee_db(self, employee_db):
        self.employee_db = employee_db
    
    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone_number TEXT,
                username TEXT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bot_messages (
                user_id INTEGER PRIMARY KEY,
                last_message_id INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS user_messages (
                user_id INTEGER,
                message_id INTEGER,
                chat_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, message_id)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS usage_stats (
                user_id INTEGER,
                username TEXT,
                action TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def register_user(self, user_id, phone_number, username):
        query = "INSERT OR REPLACE INTO users (user_id, phone_number, username) VALUES (?, ?, ?)"
        self.conn.execute(query, (user_id, phone_number, username))
        self.conn.commit()
    
    def is_registered(self, user_id):
        query = "SELECT 1 FROM users WHERE user_id = ?"
        result = self.conn.execute(query, (user_id,)).fetchone()
        return result is not None
    
    def is_employee(self, phone_number):
        if not self.employee_db:
            return False
            
        normalized_phone = self.normalize_phone(phone_number)
        print(f"🔍 Проверка номера: {phone_number} -> {normalized_phone}")
        
        # ПРИНУДИТЕЛЬНО добавляем админа
        if normalized_phone == "+79265930123":
            print("✅ ПРИНУДИТЕЛЬНЫЙ ДОСТУП: АДМИНИСТРАТОР")
            return True
        
        for driver in self.employee_db.drivers:
            driver_phone = self.normalize_phone(driver.get('phone', ''))
            if normalized_phone == driver_phone:
                print(f"✅ Найден водитель: {driver.get('name')}")
                return True
        
        for manager in self.employee_db.managers:
            manager_phone = self.normalize_phone(manager.get('phone', ''))
            if normalized_phone == manager_phone:
                print(f"✅ Найден руководитель: {manager.get('name')}")
                return True
        
        for mechanic in self.employee_db.mechanics:
            mechanic_phone = self.normalize_phone(mechanic.get('phone', ''))
            if normalized_phone == mechanic_phone:
                print(f"✅ Найден механик: {mechanic.get('name')}")
                return True
        
        print(f"❌ Номер не найден в базе сотрудников")
        return False    
        
    def normalize_phone(self, phone):
        if not phone:
            return ""
        
        print(f"🔧 Нормализуем номер: {phone}")
        
        digits = ''.join(c for c in phone if c.isdigit())
        
        if digits.startswith('7') and len(digits) == 11:
            result = '+7' + digits[1:]
        elif digits.startswith('8') and len(digits) == 11:
            result = '+7' + digits[1:]
        elif len(digits) == 10:
            result = '+7' + digits
        else:
            result = '+' + digits if not digits.startswith('+') else digits
        
        print(f"🔧 Результат нормализации: {phone} -> {result}")
        return result
    
    def get_user_phone(self, user_id):
        query = "SELECT phone_number FROM users WHERE user_id = ?"
        result = self.conn.execute(query, (user_id,)).fetchone()
        return result[0] if result else None
    
    def can_search_drivers(self, user_id):
        if not self.is_registered(user_id):
            return False
        phone = self.get_user_phone(user_id)
        return phone and self.is_employee(phone)
    
    def save_last_bot_message(self, user_id, message_id):
        query = "INSERT OR REPLACE INTO bot_messages (user_id, last_message_id) VALUES (?, ?)"
        self.conn.execute(query, (user_id, message_id))
        self.conn.commit()
    
    def get_last_bot_message(self, user_id):
        query = "SELECT last_message_id FROM bot_messages WHERE user_id = ?"
        result = self.conn.execute(query, (user_id,)).fetchone()
        return result[0] if result else None
    
    def delete_last_bot_message(self, bot, user_id, chat_id):
        try:
            last_message_id = self.get_last_bot_message(user_id)
            if last_message_id:
                bot.delete_message(chat_id, last_message_id)
            self.conn.execute("DELETE FROM bot_messages WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return True
        except:
            self.conn.execute("DELETE FROM bot_messages WHERE user_id = ?", (user_id,))
            self.conn.commit()
            return False
    
    def save_user_message(self, user_id, message_id, chat_id):
        try:
            query = "INSERT OR REPLACE INTO user_messages (user_id, message_id, chat_id) VALUES (?, ?, ?)"
            self.conn.execute(query, (user_id, message_id, chat_id))
            self.conn.commit()
            return True
        except:
            return False
    
    def delete_user_messages(self, bot, user_id, chat_id):
        try:
            query = "SELECT message_id FROM user_messages WHERE user_id = ?"
            result = self.conn.execute(query, (user_id,)).fetchall()
            
            deleted_count = 0
            for row in result:
                try:
                    message_id = row[0]
                    bot.delete_message(chat_id, message_id)
                    deleted_count += 1
                    print(f"🗑️ Удалено сообщение пользователя {user_id}: {message_id}")
                except Exception as e:
                    print(f"⚠️ Не удалось удалить сообщение {row[0]}: {e}")
            
            self.conn.execute("DELETE FROM user_messages WHERE user_id = ?", (user_id,))
            self.conn.commit()
            
            print(f"✅ Удалено {deleted_count} сообщений пользователя {user_id}")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Ошибка удаления сообщений пользователя: {e}")
            return 0
    
    def log_usage(self, user_id, username, action):
        try:
            query = "INSERT INTO usage_stats (user_id, username, action) VALUES (?, ?, ?)"
            self.conn.execute(query, (user_id, username, action))
            self.conn.commit()
        except:
            pass

    def find_employee_name(self, phone_number):
        """Находит настоящее имя сотрудника по номеру телефона"""
        if not self.employee_db:
            return None
            
        normalized_phone = self.normalize_phone(phone_number)
        print(f"🔍 Поиск имени для номера: {normalized_phone}")
        
        # Ищем водителей
        for driver in self.employee_db.drivers:
            driver_phone = self.normalize_phone(driver.get('phone', ''))
            if normalized_phone == driver_phone:
                name = driver.get('name', '')
                surname = driver.get('surname', '')
                full_name = f"{name} {surname}".strip()
                print(f"✅ Найден водитель: {full_name}")
                return full_name
        
        # Ищем руководство
        for manager in self.employee_db.managers:
            manager_phone = self.normalize_phone(manager.get('phone', ''))
            if normalized_phone == manager_phone:
                name = manager.get('name', '')
                print(f"✅ Найден руководитель: {name}")
                return name
        
        # Ищем механиков
        for mechanic in self.employee_db.mechanics:
            mechanic_phone = self.normalize_phone(mechanic.get('phone', ''))
            if normalized_phone == mechanic_phone:
                name = mechanic.get('name', '')
                print(f"✅ Найден механик: {name}")
                return name
        
        print(f"❌ Имя не найдено для номера: {normalized_phone}")
        return None

    def get_stats(self):
        try:
            total_users = self.conn.execute("SELECT COUNT(DISTINCT user_id) FROM users").fetchone()[0]
            total_actions = self.conn.execute("SELECT COUNT(*) FROM usage_stats").fetchone()[0]
            
            popular_actions = self.conn.execute("""
                SELECT action, COUNT(*) as count FROM usage_stats 
                GROUP BY action ORDER BY count DESC LIMIT 10
            """).fetchall()
            
            # ИСПРАВЛЕННЫЙ ЗАПРОС - получаем phone_number
            active_users = self.conn.execute("""
                SELECT u.user_id, u.username, u.phone_number, COUNT(*) as action_count 
                FROM usage_stats us
                JOIN users u ON us.user_id = u.user_id
                GROUP BY us.user_id 
                ORDER BY action_count DESC 
                LIMIT 10
            """).fetchall()
            
            return {
                'total_users': total_users,
                'total_actions': total_actions,
                'popular_actions': popular_actions,
                'active_users': active_users
            }
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {'total_users': 0, 'total_actions': 0, 'popular_actions': [], 'active_users': []}

class EmployeeDatabase:
    def __init__(self):
        self.drivers = []
        self.managers = []
        self.mechanics = []
        self.load_all_data()
    
    def load_csv_data(self, filename):
        try:
            file_path = os.path.join('data', filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    return list(reader)
            return []
        except:
            return []
    
    def load_all_data(self):
        self.drivers = self.load_csv_data('drivers.csv')
        self.managers = self.load_csv_data('managers.csv')
        self.mechanics = self.load_csv_data('mechanics.csv')
    
    def search_drivers(self, query):
        if not query or not self.drivers:
            return []
        
        query = query.lower().strip()
        results = []
        
        for driver in self.drivers:
            if (query in driver.get('name', '').lower() or 
                query in driver.get('surname', '').lower() or
                query in driver.get('phone', '').lower() or
                query in driver.get('id', '').lower()):
                results.append(driver)
        
        return results

user_db = UserDatabase()
employee_db = EmployeeDatabase()
user_db.set_employee_db(employee_db)