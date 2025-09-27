import requests
from bs4 import BeautifulSoup, NavigableString
import re
from datetime import datetime

url = "https://game8.co/games/Honkai-Star-Rail/archives/474951"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/137.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.raise_for_status()
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.select("table.a-table")

banners = []

# парсим даты в ISO
def parse_date_range(date_str):
    date_str = date_str.strip()
    if "TBD" in date_str:
        return {"start": None, "end": None}

    # пример: "Oct. 15, 2025 - Nov. 04, 2025"
    # пример: "Dec. 25 - Jan. 14, 2025"
    # пример: "Jul. 11, 2025 - TBD"
    parts = date_str.split("-")

    if len(parts) == 1:
        return {"start": None, "end": None}

    start_raw = parts[0].strip()
    end_raw = parts[1].strip()

    # ищем год в конце
    year_match = re.search(r"(\d{4})", end_raw)
    year = int(year_match.group(1)) if year_match else None

    def normalize(d, fallback_year):
        d = d.replace(",", "").strip()
        if re.match(r"^[A-Za-z]{3}\.\s+\d{1,2}$", d):  # без года
            return datetime.strptime(f"{d} {fallback_year}", "%b. %d %Y").date()
        elif re.match(r"^[A-Za-z]{3}\.\s+\d{1,2}\s+\d{4}$", d):  # с годом
            return datetime.strptime(d, "%b. %d %Y").date()
        else:
            return None

    start_date = normalize(start_raw, year)
    end_date = normalize(end_raw, year)

    # случай "Dec. 25 - Jan. 14, 2025"
    if start_date and end_date and start_date > end_date:
        start_date = normalize(start_raw, year - 1)

    return {
        "start": start_date.isoformat() if start_date else None,
        "end": end_date.isoformat() if end_date else None
    }

# Функция для извлечения персонажей из блока
def extract_characters(block):
    """Извлекает персонажей из блока Featured 5★ или 4★"""
    characters = []
    if not block:
        return characters
    
    # Ищем все ссылки с персонажами
    links = block.find_all("a", class_="a-link")
    for link in links:
        img = link.find("img")
        if img:
            name = img.get("alt", "").replace("HSR - ", "").strip()
            image_url = img.get("data-src") or img.get("src")
            character_url = link.get("href")
            
            if name and image_url:
                characters.append({
                    "name": name,
                    "url": image_url,
                    "character_url": character_url
                })
    
    return characters

# Функция для извлечения версии и фазы из текста
def extract_version_phase(text):
    """Извлекает версию и фазу из текста типа 'Version 3.0 Phase 2'"""
    if not text:
        return None, None

    # Ищем "Version X.X" или "Version X.XPhase Y"
    version_match = re.search(r"Version\s+(\d+\.\d+)", text)
    phase_match = re.search(r"Phase\s*(\d+)", text)

    version = version_match.group(1) if version_match else None
    phase = f"Phase {phase_match.group(1)}" if phase_match else None

    return version, phase

for table in tables:
    rows = table.find_all("tr")

    i = 0
    while i < len(rows):
        row = rows[i]

        # Извлекаем заголовок версии
        th = row.find("th", colspan="3")
        if th:
            version_text = th.get_text(strip=True)
            current_version, current_phase = extract_version_phase(version_text)

            # Обрабатываем все следующие строки до следующего заголовка версии
            i += 1
            while i < len(rows):
                next_row = rows[i]

                # Если нашли следующий заголовок версии, выходим из внутреннего цикла
                if next_row.find("th", colspan="3"):
                    break

                # Обрабатываем строку с данными баннера
                cells = next_row.find_all("td")
                if len(cells) >= 2:
                    # Извлекаем даты из второй ячейки
                    info_cell = cells[1]
                    date_tag = info_cell.find("b", string="Banner Dates:")
                    if not date_tag:
                        date_tag = info_cell.find("b", string="Banner Dates")

                    date_text = None
                    if date_tag:
                        for sibling in date_tag.next_siblings:
                            if isinstance(sibling, NavigableString):
                                text = sibling.strip()
                                if text:
                                    date_text = text
                                    break

                    # Парсим даты
                    current_dates = parse_date_range(date_text) if date_text else {"start": None, "end": None}

                    # Ищем все блоки "Featured 5★:" и создаем отдельный баннер для каждого
                    five_star_blocks = info_cell.find_all("b", string=lambda text: text and ("Featured 5★:" in text or "Featured 5-Star:" in text))

                    # Для каждого блока 5★ создаем отдельный баннер
                    for five_star_block in five_star_blocks:
                        # Извлекаем 5★ персонажей для этого блока
                        five_star_characters = []
                        next_div = five_star_block.find_next("div", class_="align")
                        if next_div:
                            five_star_characters = extract_characters(next_div)

                        # Ищем соответствующий блок 4★ для этого баннера
                        four_star_characters = []

                        # Ищем следующий hr после блока 5★
                        hr_after_five = five_star_block.find_next("hr", class_="a-table__line")
                        if hr_after_five:
                            # Ищем следующий блок 4★ после hr
                            four_star_block = hr_after_five.find_next("b", string=lambda text: text and ("Featured 4★:" in text or "Featured 4-Star:" in text))
                            if four_star_block:
                                next_four_div = four_star_block.find_next("div", class_="align")
                                if next_four_div:
                                    four_star_characters = extract_characters(next_four_div)

                        # Добавляем баннер только если есть персонажи
                        if five_star_characters or four_star_characters:
                            banners.append({
                                "version": current_version,
                                "phase": current_phase,
                                "dates": current_dates,
                                "featured_5": five_star_characters,
                                "featured_4": four_star_characters
                            })

                i += 1
        else:
            i += 1

# вывод json-подобного результата
import json
print(json.dumps(banners, indent=2, ensure_ascii=False))

# Сохраните данные в JSON-файл в текущей папке
with open('data_parsing/hsr/banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=4)