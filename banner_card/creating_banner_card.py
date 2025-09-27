import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
from typing import Dict, List, Optional

def make_banner_card_base64(data: dict, game_name: str = "genshin") -> str:
    """
    Создаёт карточку баннера и возвращает её как base64-строку.
    
    Args:
        data (dict): Данные баннера
        game_name (str): Название игры (genshin, hsr, zzz, wuwa)
    """
    width, height = 800, 600  # Увеличиваем высоту для большего пространства
    bg_color = (30, 30, 30)

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Настройки шрифтов
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
    except OSError:
        # Fallback на стандартный шрифт
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # Настройки игры
    game_settings = {
        "genshin": {
            "name": "Genshin Impact",
            "title_color": (255, 255, 0),  # Желтый
            "star_5_color": (255, 215, 0),  # Золотой
            "star_4_color": (135, 206, 250)  # Голубой
        },
        "hsr": {
            "name": "Honkai: Star Rail",
            "title_color": (255, 100, 100),  # Красный
            "star_5_color": (255, 215, 0),  # Золотой
            "star_4_color": (135, 206, 250)  # Голубой
        },
        "zzz": {
            "name": "Zenless Zone Zero",
            "title_color": (100, 255, 100),  # Зеленый
            "star_5_color": (255, 215, 0),  # Золотой
            "star_4_color": (135, 206, 250)  # Голубой
        },
        "wuwa": {
            "name": "Wuthering Waves",
            "title_color": (100, 100, 255),  # Синий
            "star_5_color": (255, 215, 0),  # Золотой
            "star_4_color": (135, 206, 250)  # Голубой
        }
    }
    
    settings = game_settings.get(game_name, game_settings["genshin"])

    # Функция для переноса длинного текста
    def wrap_text(text, font, max_width):
        """Переносит текст на новую строку если он слишком длинный"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Если одно слово длиннее max_width, оставляем как есть
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    # Заголовок
    title = f"{settings['name']} {data['version']} – {data['phase']}"
    draw.text((20, 20), title, font=font_title, fill=settings['title_color'])

    # Даты
    dates = f"{data['dates']['start']} → {data['dates']['end']}"
    draw.text((20, 70), dates, font=font_text, fill=(200, 200, 200))

    # Блок 5★
    stars_5 = "★★★★★"
    draw.text((20, 110), f"{stars_5}  Featured 5★", font=font_text, fill=settings['star_5_color'])
    x = 20
    y = 150
    for char in data.get("featured_5", []):
        try:
            r = requests.get(char["url"], timeout=10)
            icon = Image.open(BytesIO(r.content)).convert("RGBA")
            icon = icon.resize((128, 128))
            img.paste(icon, (x, y), icon)
            
            # Переносим имя персонажа если оно длинное
            char_name = char["name"]
            wrapped_lines = wrap_text(char_name, font_text, 120)  # Максимальная ширина для имени
            
            # Рисуем каждую строку имени
            text_y = y + 135
            for line in wrapped_lines:
                draw.text((x, text_y), line, font=font_text, fill=(255, 255, 255))
                text_y += 25  # Отступ между строками
            
            x += 150
        except Exception as e:
            print(f"Ошибка загрузки {char['name']}: {e}")

    # Блок 4★ (только для Genshin, у HSR может не быть)
    if data.get("featured_4"):
        stars_4 = "★★★★"
        draw.text((20, 380), f"{stars_4}  Featured 4★", font=font_text, fill=settings['star_4_color'])
        x = 20
        y = 420
        for char in data["featured_4"]:
            try:
                r = requests.get(char["url"], timeout=10)
                icon = Image.open(BytesIO(r.content)).convert("RGBA")
                icon = icon.resize((96, 96))
                img.paste(icon, (x, y), icon)
                
                # Переносим имя персонажа если оно длинное
                char_name = char["name"]
                wrapped_lines = wrap_text(char_name, font_text, 100)  # Максимальная ширина для имени
                
                # Рисуем каждую строку имени
                text_y = y + 100
                for line in wrapped_lines:
                    draw.text((x, text_y), line, font=font_text, fill=(255, 255, 255))
                    text_y += 25  # Отступ между строками
                
                x += 120
            except Exception as e:
                print(f"Ошибка загрузки {char['name']}: {e}")

    # сохраняем в память
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_base64


if __name__ == "__main__":
    banner = {
        "version": "3.8",
        "phase": "Phase 1",
        "dates": {
            "start": "2023-07-05",
            "end": "2023-07-25"
        },
        "featured_5": [
            {
                "name": "Eula",
                "url": "https://img.game8.co/3357399/0681a143deeb28601cffa5fee727dd3d.png/show"
            },
            {
                "name": "Klee",
                "url": "https://img.game8.co/3294978/e0194d396700c3add4ec1b95ddce41f0.png/show"
            }
        ],
        "featured_4": [
            {
                "name": "Razor",
                "url": "https://img.game8.co/3294976/698d06f42b22301950f6eeda34cc9a37.png/show"
            },
            {
                "name": "Thoma",
                "url": "https://img.game8.co/3441106/99ed64ada8d15708869cd60643a8044f.png/show"
            },
            {
                "name": "Mika",
                "url": "https://img.game8.co/3662046/34c5273e49bbcc42fcd0c2e29522bd3b.png/show"
            }
        ]
    }

    img_b64 = make_banner_card_base64(banner)
    img_bytes = BytesIO(base64.b64decode(img_b64))
    