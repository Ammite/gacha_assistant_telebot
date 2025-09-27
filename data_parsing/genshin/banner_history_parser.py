import requests
from bs4 import BeautifulSoup, NavigableString
import re
from datetime import datetime

url = "https://game8.co/games/Genshin-Impact/archives/297500"

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
current_banner_section = soup.find('h2', string='Banners in Version 6.0 Luna I Phase 1')
current_tables = []
if current_banner_section:
    current_element = current_banner_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            current_tables.append(current_element)
        current_element = current_element.find_next()

# Находим секцию предстоящих баннеров
upcoming_banner_section = soup.find('h2', string='Upcoming Wish Banners')
upcoming_tables = []
if upcoming_banner_section:
    current_element = upcoming_banner_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            upcoming_tables.append(current_element)
        current_element = current_element.find_next()

print(f"Найдено таблиц в текущих баннерах: {len(current_tables)}")
print(f"Найдено таблиц в предстоящих баннерах: {len(upcoming_tables)}")

def parse_banner_table(table, version, phase, is_weapon_banner=False):
    """Парсит таблицу баннера нового формата"""
    banner_data = {
        "version": version,
        "phase": phase,
        "dates": {"start": None, "end": None},
        "featured_5": [],
        "featured_4": []
    }

    rows = table.find_all("tr")

    # Извлекаем даты из заголовка таблицы
    if rows:
        header_row = rows[0]
        cells = header_row.find_all(["th", "td"])
        if len(cells) >= 2:
            date_cell = cells[1]  # Вторая ячейка содержит даты
            date_text = date_cell.get_text(strip=True)
            if date_text and "-" in date_text:
                banner_data["dates"] = parse_date_range(date_text)

    # Извлекаем персонажей из строк 5-star и 4-star
    for row in rows[1:]:  # Пропускаем заголовок
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            header_cell = cells[0]
            content_cell = cells[1]

            header_text = header_cell.get_text(strip=True)

            if "5-star Rate Up" in header_text:
                # Извлекаем 5-star персонажей
                banner_data["featured_5"] = extract_characters(content_cell)
            elif "4-star Rate Up" in header_text:
                # Извлекаем 4-star персонажей
                banner_data["featured_4"] = extract_characters(content_cell)

    return banner_data

def extract_characters(cell):
    """Извлекает персонажей из ячейки с изображениями"""
    characters = []
    if not cell:
        return characters

    # Ищем все ссылки с изображениями
    links = cell.find_all("a", class_="a-link")
    for link in links:
        img = link.find("img")
        if img:
            name = img.get("alt", "").replace("Genshin - ", "").strip()
            image_url = img.get("data-src") or img.get("src")
            character_url = link.get("href")

            if name and image_url:
                characters.append({
                    "name": name,
                    "url": image_url,
                    "character_url": character_url
                })

    return characters

# парсим даты в ISO
def parse_date_range(date_str):
    date_str = date_str.strip()
    if "TBD" in date_str:
        return {"start": None, "end": None}

    # пример: "January 1, 2025 - January 21, 2025"
    # пример: "December 25, 2024 - January 14, 2025"
    parts = date_str.split("-")

    if len(parts) == 1:
        return {"start": None, "end": None}

    start_raw = parts[0].strip()
    end_raw = parts[1].strip()

    def normalize(d):
        d = d.replace(",", "").strip()
        try:
            # пробуем разные форматы дат
            formats = [
                "%B %d %Y",   # January 1, 2025
                "%b %d %Y",   # Jan 1, 2025
                "%b. %d %Y",  # Jun. 13, 2023
                "%B %d",      # January 1
                "%b %d",      # Jan 1
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

    # если год не указан, используем текущий
    if start_date and not start_date.year:
        start_date = start_date.replace(year=2025)
    if end_date and not end_date.year:
        end_date = end_date.replace(year=2025)

    return {
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None
    }


# Парсим текущие баннеры (Phase 1)
print("\nПарсим текущие баннеры...")
for i, table in enumerate(current_tables):
    print(f"Парсим таблицу {i+1} из текущих баннеров")
    if i == 0:  # Первая таблица - персонажи
        banner = parse_banner_table(table, "6.0", "Phase 1")
        banners.append(banner)
        print(f"Добавлен баннер: версия {banner['version']}, фаза {banner['phase']}, даты {banner['dates']}")
    # Пропускаем таблицу с оружием и таблицу с Beginner's Wish

# Парсим предстоящие баннеры (Phase 2)
print("\nПарсим предстоящие баннеры...")
for i, table in enumerate(upcoming_tables):
    print(f"Парсим таблицу {i+1} из предстоящих баннеров")
    banner = parse_banner_table(table, "6.0", "Phase 2")
    banners.append(banner)
    print(f"Добавлен баннер: версия {banner['version']}, фаза {banner['phase']}, даты {banner['dates']}")

# вывод json-подобного результата
import json
print(json.dumps(banners, indent=2, ensure_ascii=False))

# Сохраните данные в JSON-файл в текущей папке
with open('data_parsing/genshin/banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=4)