"""
Менеджер whitelist пользователей бота
"""

import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class WhitelistManager:
    """Класс для управления whitelist пользователей"""

    def __init__(self, whitelist_file: str = "whitelist.txt"):
        self.whitelist_file = whitelist_file
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Создает файл whitelist.txt если он не существует"""
        if not os.path.exists(self.whitelist_file):
            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                pass  # Создаем пустой файл
            logger.info(f"Создан файл whitelist: {self.whitelist_file}")

    def load_whitelist(self) -> List[str]:
        """Загружает whitelist из файла"""
        try:
            with open(self.whitelist_file, 'r', encoding='utf-8') as f:
                # Читаем строки, убираем пробелы и пустые строки
                users = [line.strip() for line in f if line.strip()]
            logger.debug(f"Загружен whitelist: {users}")
            return users
        except FileNotFoundError:
            logger.warning(f"Файл whitelist не найден: {self.whitelist_file}")
            self._ensure_file_exists()
            return []
        except Exception as e:
            logger.error(f"Ошибка при загрузке whitelist: {e}")
            return []

    def save_whitelist(self, users: List[str]) -> bool:
        """Сохраняет whitelist в файл"""
        try:
            # Убираем дубликаты и пустые строки
            unique_users = list(set(user.strip() for user in users if user.strip()))

            with open(self.whitelist_file, 'w', encoding='utf-8') as f:
                for user in sorted(unique_users):  # Сортируем для удобства чтения
                    f.write(f"{user}\n")

            logger.info(f"Whitelist сохранен: {unique_users}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении whitelist: {e}")
            return False

    def add_user(self, user_id: str) -> bool:
        """Добавляет пользователя в whitelist"""
        if not user_id or not user_id.strip():
            logger.warning("Попытка добавить пустой user_id")
            return False

        user_id = user_id.strip()
        users = self.load_whitelist()

        if user_id in users:
            logger.info(f"Пользователь {user_id} уже в whitelist")
            return True  # Уже есть, считаем успехом

        users.append(user_id)
        success = self.save_whitelist(users)

        if success:
            logger.info(f"Пользователь {user_id} добавлен в whitelist")
        else:
            logger.error(f"Не удалось добавить пользователя {user_id} в whitelist")

        return success

    def remove_user(self, user_id: str) -> bool:
        """Удаляет пользователя из whitelist"""
        if not user_id or not user_id.strip():
            logger.warning("Попытка удалить пустой user_id")
            return False

        user_id = user_id.strip()
        users = self.load_whitelist()

        if user_id not in users:
            logger.info(f"Пользователь {user_id} не найден в whitelist")
            return True  # Уже нет, считаем успехом

        users.remove(user_id)
        success = self.save_whitelist(users)

        if success:
            logger.info(f"Пользователь {user_id} удален из whitelist")
        else:
            logger.error(f"Не удалось удалить пользователя {user_id} из whitelist")

        return success

    def is_user_allowed(self, user_id: str) -> bool:
        """Проверяет, разрешен ли доступ пользователю"""
        if not user_id:
            return False

        user_id = str(user_id).strip()
        users = self.load_whitelist()
        return user_id in users

    def get_all_users(self) -> List[str]:
        """Возвращает список всех пользователей в whitelist"""
        return self.load_whitelist()

# Глобальный экземпляр менеджера whitelist
whitelist_manager = WhitelistManager()
