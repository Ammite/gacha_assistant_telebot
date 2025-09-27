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

    # пример: "Aug. 12 - Sep. 02, 2025"
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


for table in tables:
    rows = table.find_all("tr")

    version_text = None

    for row in rows:
        th = row.find("th", colspan="3")
        if th:
            version_text = th.get_text(strip=True)

        if "Banner Dates:" in row.get_text():
            date_tag = row.find("b", string="Banner Dates:")
            date_text = None
            if date_tag:
                for sibling in date_tag.next_siblings:
                    if isinstance(sibling, NavigableString):
                        text = sibling.strip()
                        if text:
                            date_text = text
                            break

            # вытаскиваем версию и фазу
            version, phase = None, None
            if version_text:
                m = re.search(r"Version\s+(\d+\.\d+)", version_text)
                if m:
                    version = m.group(1)
                m2 = re.search(r"Phase\s+(\d+)", version_text)
                if m2:
                    phase = m2.group(1)

                if not version:
                    version = version_text

            # парсим даты
            dates = parse_date_range(date_text) if date_text else {"start": None, "end": None}

            # ищем 5★
            five_star_block = row.find("b", string="Featured 5★:")
            five_star_names = []
            if five_star_block:
                imgs = five_star_block.find_next("div").find_all("img")
                five_star_names = [{"name": img["alt"].replace("HSR - ", "").strip(), "url": img.get("data-src")} for img in imgs]

            banners.append({
                "version": version,
                "phase": phase,
                "dates": dates,
                "featured_5": five_star_names
            })

# вывод json-подобного результата
import json
print(json.dumps(banners, indent=2, ensure_ascii=False))

# Сохраните данные в JSON-файл
with open('banners.json', 'w', encoding='utf-8') as f:
    json.dump(banners, f, ensure_ascii=False, indent=4)