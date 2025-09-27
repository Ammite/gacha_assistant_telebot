import requests
from bs4 import BeautifulSoup, NavigableString
import re
from datetime import datetime

url = "https://game8.co/games/Zenless-Zone-Zero/archives/435687"

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
current_banner_section = soup.find('h2', string='Current Banners in ZZZ')
current_tables = []
if current_banner_section:
    current_element = current_banner_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            current_tables.append(current_element)
        current_element = current_element.find_next()

# Находим секцию предстоящих баннеров
upcoming_banner_section = soup.find('h2', string='Upcoming Banners in ZZZ')
upcoming_tables = []
if upcoming_banner_section:
    current_element = upcoming_banner_section.find_next()
    while current_element and current_element.name != 'h2':
        if current_element.name == 'table':
            upcoming_tables.append(current_element)
        current_element = current_element.find_next()

print(f"Найдено таблиц в текущих баннерах: {len(current_tables)}")
print(f"Найдено таблиц в предстоящих баннерах: {len(upcoming_tables)}")

def parse_date_range(date_str):
    """Парсит диапазон дат для ZZZ"""
    date_str = date_str.strip()
    if "TBD" in date_str:
        return {"start": None, "end": None}

    # Формат: "September 24, 2025 - October 14, 2025"
    parts = date_str.split("-")
    if len(parts) == 1:
        return {"start": None, "end": None}

    start_raw = parts[0].strip()
    end_raw = parts[1].strip()

    def normalize(d):
        d = d.replace(",", "").strip()
        try:
            formats = [
                "%B %d %Y",   # September 24, 2025
                "%b %d %Y",   # Sep 24, 2025
                "%b. %d %Y",  # Jun. 13, 2023
                "%B %d",      # September 24
                "%b %d",      # Sep 24
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

def parse_banner_table(table, version, phase, is_weapon_banner=False):
    """Парсит таблицу баннера ZZZ"""
    banner_data = {
        "version": version,
        "phase": phase,
        "dates": {"start": None, "end": None},
        "featured_5": [],  # S-Rank agents
        "featured_4": []   # A-Rank agents
    }

    rows = table.find_all("tr")

    # Извлекаем даты из заголовка таблицы
    if rows:
        header_row = rows[0]
        cells = header_row.find_all(["th", "td"])
        if len(cells) >= 2:
            # Ищем ячейку с Duration
            for cell in cells:
                if "Duration" in cell.get_text(strip=True):
                    # Следующая ячейка должна содержать даты
                    cell_index = cells.index(cell)
                    if cell_index + 1 < len(cells):
                        date_cell = cells[cell_index + 1]
                        date_text = date_cell.get_text(strip=True)
                        if date_text and "-" in date_text:
                            banner_data["dates"] = parse_date_range(date_text)
                    break

    # Извлекаем агентов из строки Rate-Up Agents
    for row in rows[1:]:  # Пропускаем заголовок
        cells = row.find_all(["th", "td"])
        if len(cells) >= 2:
            header_cell = cells[0]
            content_cell = cells[1]

            header_text = header_cell.get_text(strip=True)

            if "Rate-Up Agents" in header_text:
                # Извлекаем агентов
                agents = extract_agents(content_cell)
                # Разделяем на S-Rank и A-Rank
                for agent in agents:
                    if "(S-Rank" in agent.get("name", "") or "S-Rank" in agent.get("name", ""):
                        banner_data["featured_5"].append(agent)
                    elif "(A-Rank" in agent.get("name", "") or "A-Rank" in agent.get("name", ""):
                        banner_data["featured_4"].append(agent)
                    else:
                        # Если ранг не указан в имени, добавляем в featured_5 по умолчанию
                        banner_data["featured_5"].append(agent)

    return banner_data

def extract_agents(cell):
    """Извлекает агентов из ячейки с изображениями"""
    agents = []
    if not cell:
        return agents

    # Ищем все ссылки с изображениями
    links = cell.find_all("a", class_="a-link")
    for link in links:
        img = link.find("img")
        if img:
            name = img.get("alt", "").replace("ZZZ - ", "").strip()
            image_url = img.get("data-src") or img.get("src")
            agent_url = link.get("href")

            if name and image_url:
                agents.append({
                    "name": name,
                    "url": image_url,
                    "character_url": agent_url
                })

    # Если нет ссылок, пробуем найти просто изображения
    if not agents:
        imgs = cell.find_all("img")
        for img in imgs:
            name = img.get("alt", "").replace("ZZZ - ", "").strip()
            image_url = img.get("data-src") or img.get("src")

            if name and image_url:
                agents.append({
                    "name": name,
                    "url": image_url,
                    "character_url": None
                })

    return agents

# Парсим текущие баннеры
print("\nПарсим текущие баннеры ZZZ...")
banner_count = 0
for i, table in enumerate(current_tables):
    # Пропускаем таблицы с pity системой (они имеют другую структуру)
    rows = table.find_all("tr")
    if rows and len(rows) > 0:
        first_cell = rows[0].find(["th", "td"])
        if first_cell and "Times" in first_cell.get_text(strip=True):
            continue  # Это таблица pity системы

    print(f"Парсим таблицу {i+1} из текущих баннеров")
    banner = parse_banner_table(table, "Current", f"Banner {banner_count + 1}")
    if banner["dates"]["start"]:  # Добавляем только если есть даты
        banners.append(banner)
        banner_count += 1
        print(f"Добавлен баннер: версия {banner['version']}, фаза {banner['phase']}, даты {banner['dates']}")

# Парсим предстоящие баннеры
print("\nПарсим предстоящие баннеры ZZZ...")
for i, table in enumerate(upcoming_tables):
    print(f"Парсим таблицу {i+1} из предстоящих баннеров")
    banner = parse_banner_table(table, "Upcoming", f"Banner {banner_count + 1}")
    if banner["dates"]["start"]:  # Добавляем только если есть даты
        banners.append(banner)
        banner_count += 1
        print(f"Добавлен баннер: версия {banner['version']}, фаза {banner['phase']}, даты {banner['dates']}")

# Вывод результата
import json
print(json.dumps(banners, indent=2, ensure_ascii=False))

# Сохраняем данные в JSON-файл
with open('data_parsing/zzz/banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=4)