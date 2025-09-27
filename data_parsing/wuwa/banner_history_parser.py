import requests
from bs4 import BeautifulSoup, NavigableString
import re
from datetime import datetime

url = "https://game8.co/games/Wuthering-Waves/archives/453303"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/137.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

banners = []

# Находим секцию текущих баннеров
available_section = soup.find('h2', string='Available Convene Banners in Wuthering Waves')
available_tables = []
if available_section:
    current_element = available_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            available_tables.append(current_element)
        current_element = current_element.find_next()

# Находим секцию предстоящих баннеров
upcoming_section = soup.find('h2', string='Upcoming Banners in Wuthering Waves')
upcoming_tables = []
if upcoming_section:
    current_element = upcoming_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            upcoming_tables.append(current_element)
        current_element = current_element.find_next()

print(f"Найдено таблиц в текущих баннерах: {len(available_tables)}")
print(f"Найдено таблиц в предстоящих баннерах: {len(upcoming_tables)}")

def parse_date_range(date_str):
    """Парсит диапазон дат для WuWa"""
    date_str = date_str.strip()
    if "TBD" in date_str:
        return {"start": None, "end": None}

    # Формат: "September 17, 2025 - October 8, 2025"
    parts = date_str.split("-")
    if len(parts) == 1:
        return {"start": None, "end": None}

    start_raw = parts[0].strip()
    end_raw = parts[1].strip()

    def normalize(d):
        d = d.replace(",", "").strip()
        try:
            formats = [
                "%B %d %Y",   # September 17, 2025
                "%b %d %Y",   # Sep 17, 2025
                "%b. %d %Y",  # Jun. 13, 2023
                "%B %d",      # September 17
                "%b %d",      # Sep 17
                "%b. %d"      # Jun. 13
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(d, fmt).date()
                except ValueError:
                    continue
            return None
        except:
            return None

    start_date = normalize(start_raw)
    end_date = normalize(end_raw)

    # Если год не указан, используем текущий
    if start_date and not start_date.year:
        start_date = start_date.replace(year=2025)
    if end_date and not end_date.year:
        end_date = end_date.replace(year=2025)

    return {
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None
    }

def parse_banner_table(table, version, is_available=True):
    """Парсит таблицу баннера WuWa"""
    banner_data = {
        "version": version,
        "phase": "Current" if is_available else "Upcoming",
        "dates": {"start": None, "end": None},
        "featured_5": [],  # 5★ characters/weapons
        "featured_4": []   # 4★ characters/weapons
    }

    rows = table.find_all("tr")

    # Извлекаем даты
    if is_available:
        # Для доступных баннеров даты в последней строке
        if rows:
            last_row = rows[-1]
            cells = last_row.find_all(["th", "td"])
            for cell in cells:
                date_text = cell.get_text(strip=True)
                if "-" in date_text and any(month in date_text.lower() for month in
                                          ['january', 'february', 'march', 'april', 'may', 'june',
                                           'july', 'august', 'september', 'october', 'november', 'december']):
                    banner_data["dates"] = parse_date_range(date_text)
                    break
    else:
        # Для предстоящих баннеров ищем даты в последней строке или рядом с таблицей
        if rows:
            last_row = rows[-1]
            cells = last_row.find_all(["th", "td"])
            for cell in cells:
                date_text = cell.get_text(strip=True)
                if any(month in date_text.lower() for month in
                      ['january', 'february', 'march', 'april', 'may', 'june',
                       'july', 'august', 'september', 'october', 'november', 'december']):
                    # Парсим одиночную дату как start
                    def parse_single_date(d):
                        d = d.replace(",", "").strip()
                        try:
                            formats = ["%B %d %Y", "%b %d %Y", "%B %d", "%b %d"]
                            for fmt in formats:
                                try:
                                    return datetime.strptime(d, fmt).date()
                                except ValueError:
                                    continue
                            return None
                        except:
                            return None

                    single_date = parse_single_date(date_text)
                    if single_date:
                        banner_data["dates"] = {
                            "start": single_date.isoformat(),
                            "end": None
                        }
                    break

    # Извлекаем персонажей из строк с данными
    for row in rows[1:-1]:  # Пропускаем заголовок и последнюю строку с датами
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            banner_cell = cells[0]
            characters_cell = cells[1]

            # Получаем название баннера
            banner_name = banner_cell.get_text(strip=True)

            # Извлекаем персонажей
            characters = extract_characters(characters_cell, banner_name)
            for char in characters:
                if char.get("rarity") == "5★":
                    banner_data["featured_5"].append(char)
                elif char.get("rarity") == "4★":
                    banner_data["featured_4"].append(char)
                # Персонажи без ранга (оружие) игнорируем для совместимости с форматом

    return banner_data

def extract_characters(cell, banner_name=""):
    """Извлекает персонажей и оружие из ячейки"""
    characters = []
    if not cell:
        return characters

    cell_text = cell.get_text()
    cell_html = str(cell)

    # Разделяем текст на секции для определения рангов
    sections = []
    if "Limited 5★" in cell_text:
        # Это предстоящий баннер с секциями
        limited_5star_start = cell_text.find("Limited 5★")
        rate_up_4star_start = cell_text.find("Rate-up 4★")
        featured_weapon_start = cell_text.find("Featured Weapon(s):")

        # 5★ секция
        star5_end = rate_up_4star_start if rate_up_4star_start != -1 else featured_weapon_start if featured_weapon_start != -1 else len(cell_text)
        star5_text = cell_text[limited_5star_start:star5_end]
        sections.append(("5★", star5_text))

        # 4★ секция
        if rate_up_4star_start != -1:
            star4_end = featured_weapon_start if featured_weapon_start != -1 else len(cell_text)
            star4_text = cell_text[rate_up_4star_start:star4_end]
            sections.append(("4★", star4_text))

        # Оружие
        if featured_weapon_start != -1:
            weapon_text = cell_text[featured_weapon_start:]
            sections.append(("weapon", weapon_text))
    else:
        # Это текущий баннер, используем старую логику
        sections = [("unknown", cell_text)]

    # Ищем все ссылки с изображениями
    links = cell.find_all("a", class_="a-link")
    for link in links:
        img = link.find("img")
        if img:
            name = img.get("alt", "").replace("WuWa - ", "").replace("Wuthering Waves - ", "").strip()
            image_url = img.get("data-src") or img.get("src")
            char_url = link.get("href")

            # Определяем ранг на основе секций
            rarity = None
            for section_rarity, section_text in sections:
                if name in section_text:
                    if section_rarity == "5★":
                        rarity = "5★"
                    elif section_rarity == "4★":
                        rarity = "4★"
                    elif section_rarity == "weapon":
                        # Оружие не имеет ранга, оставляем как есть
                        rarity = None
                    break

            # Если ранг не определен, пробуем старую логику
            if not rarity:
                # Ищем паттерн: Имя(ранг, тип) в тексте ячейки
                pattern = rf'{re.escape(name)}\s*\((\d★),\s*([^)]+)\)'
                match = re.search(pattern, cell_text)
                if match:
                    rarity = match.group(1)
                    char_type = match.group(2).strip()
                else:
                    # Альтернативный поиск
                    if f"{name}(5★" in cell_text or ("5★" in cell_text and name in cell_text and "Limited 5★" in cell_text):
                        rarity = "5★"
                    elif f"{name}(4★" in cell_text or ("4★" in cell_text and name in cell_text and "Rate-up 4★" in cell_text):
                        rarity = "4★"

            # Определяем тип персонажа
            char_type = None
            if rarity:
                type_pattern = rf'{re.escape(name)}\s*\(\d★,\s*([^)]+)\)'
                type_match = re.search(type_pattern, cell_text)
                if type_match:
                    char_type = type_match.group(1).strip()

            if name and image_url:
                characters.append({
                    "name": name,
                    "url": image_url,
                    "character_url": char_url,
                    "rarity": rarity,
                    "type": char_type,
                    "banner": banner_name
                })

    # Если нет ссылок, пробуем найти просто изображения
    if not characters:
        imgs = cell.find_all("img")
        for img in imgs:
            name = img.get("alt", "").replace("WuWa - ", "").replace("Wuthering Waves - ", "").strip()
            image_url = img.get("data-src") or img.get("src")

            if name and image_url:
                characters.append({
                    "name": name,
                    "url": image_url,
                    "character_url": None,
                    "rarity": None,
                    "type": None,
                    "banner": banner_name
                })

    return characters

# Парсим текущие баннеры - агрегируем все суб-баннеры в один большой баннер
print("\nПарсим текущие баннеры WuWa...")
if available_tables:
    # Создаем один агрегированный баннер для всех текущих
    current_banner = {
        "version": "Current",
        "phase": "Available Convene Banners",
        "dates": {"start": None, "end": None},
        "featured_5": [],
        "featured_4": []
    }

    # Собираем все уникальные персонажи из всех таблиц
    all_5star = []
    all_4star = []
    banner_dates = None

    for i, table in enumerate(available_tables):
        print(f"Парсим таблицу {i+1} из текущих баннеров")
        temp_banner = parse_banner_table(table, "Current", is_available=True)

        # Берем даты из первой таблицы
        if not banner_dates and temp_banner["dates"]["start"]:
            banner_dates = temp_banner["dates"]

        # Агрегируем персонажей
        all_5star.extend(temp_banner["featured_5"])
        all_4star.extend(temp_banner["featured_4"])

    # Убираем дубликаты по имени персонажа
    unique_5star = []
    seen_5star = set()
    for char in all_5star:
        if char["name"] not in seen_5star:
            unique_5star.append(char)
            seen_5star.add(char["name"])

    unique_4star = []
    seen_4star = set()
    for char in all_4star:
        if char["name"] not in seen_4star:
            unique_4star.append(char)
            seen_4star.add(char["name"])

    current_banner["dates"] = banner_dates or {"start": None, "end": None}
    current_banner["featured_5"] = unique_5star
    current_banner["featured_4"] = unique_4star

    if current_banner["dates"]["start"]:
        banners.append(current_banner)
        print(f"Добавлен агрегированный текущий баннер: {len(unique_5star)} 5★, {len(unique_4star)} 4★ персонажей")

# Парсим предстоящие баннеры
print("\nПарсим предстоящие баннеры WuWa...")
for i, table in enumerate(upcoming_tables):
    print(f"Парсим таблицу {i+1} из предстоящих баннеров")
    banner = parse_banner_table(table, "Upcoming", is_available=False)
    if banner["dates"]["start"]:  # Добавляем только если есть даты
        banners.append(banner)
        print(f"Добавлен предстоящий баннер: версия {banner['version']}, даты {banner['dates']}")

# Вывод результата
import json
print(json.dumps(banners, indent=2, ensure_ascii=False))

# Сохраняем данные в JSON-файл
with open('data_parsing/wuwa/banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=4)