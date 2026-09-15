import sys
import os
import requests
import json
from datetime import datetime

from waveshare_epd import epd7in5b_V2
from PIL import Image, ImageDraw, ImageFont, ImageOps

sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

project_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(project_dir, 'assets', 'fonts', 'Sansation-Regular.ttf')
bold_font_path = os.path.join(project_dir, 'assets', 'fonts', 'Sansation-Regular.ttf')
icons_path = os.path.join(project_dir, 'assets', 'weather')

WEATHER_ICONS = {
    "day": {
        "Mostly Sunny": "day_clear.png",
    },
    "night": {
        "Partly Cloudy": "night_partial_cloud.png",
    },
}

def center_justified_x(draw_image, mid_x, text, font):
    return mid_x - draw_image.textlength(text, font) / 2

def get_coordinates():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data['lat'], data['lon']
    except Exception as e:
        print(f"Error: {e}")

def get_weather_icon(condition, isDaytime) -> Image.Image:
    daytime = "day" if isDaytime else "night"
    filename = WEATHER_ICONS[daytime].get(condition)
    return Image.open(f"{icons_path}/{filename}")

def main():
    print("Initializing display...")
    epd = epd7in5b_V2.EPD()
    epd.init()

    print("Clearing screen...")
    epd.Clear()

    lat, lon = get_coordinates()

    try:
        response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
        data = response.json()
        city = data['properties']['relativeLocation']['properties']['city']
        url = data['properties']['forecastHourly']
        response = requests.get(url)
        data = response.json()
        periods = data['properties']['periods'][:5]
        print(json.dumps(periods, indent = 4))
    except Exception as e:
        print(f"Error fetching weather data: {e}")

    image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    red_image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw_image = ImageDraw.Draw(image)
    draw_red = ImageDraw.Draw(red_image)

    # Fonts
    font24 = ImageFont.truetype(font_path, 24)
    font48 = ImageFont.truetype(font_path, 48)
    bold24 = ImageFont.truetype(bold_font_path, 24)
    bold36 = ImageFont.truetype(bold_font_path, 36)
    bold48 = ImageFont.truetype(bold_font_path, 48)

    # Title
    title = f"{city} Forecast"
    draw_image.text((10, 10), title, font = bold48, fill = 0)
    line_end_x = 10 + draw_image.textlength(title, font = bold48)
    draw_image.line((10, 60, line_end_x, 60), fill = 0)

    # Current
    font_current = bold36
    current_period = periods[0]
    x1 = 10
    y1 = 130
    x2 = 260
    y2 = 410
    mid_x = (x1 + x2) / 2
    padding = 10
    draw_image.rectangle((x1, y1, x2, y2))

    time = datetime.fromisoformat(current_period["startTime"]).strftime("%-I %p")
    draw_image.text((center_justified_x(draw_image, mid_x, time, font_current), y1 + padding), time, font = font_current, fill = 0)

    icon = get_weather_icon(current_period["shortForecast"], current_period["isDaytime"])
    r, g, b, a = icon.split()
    black = Image.new("L", icon.size, 0)
    icon = Image.merge("RGBA", (black, black, black, a))
    icon = icon.resize((96, 96), Image.Resampling.LANCZOS)
    image.paste(icon, (135 - 48, 200), icon)

    temp = f"{current_period["temperature"]}°"
    draw_image.text((center_justified_x(draw_image, mid_x, temp, font_current), 310), temp, font = font_current, fill = 0)

    conditions = current_period["shortForecast"]
    draw_image.text((center_justified_x(draw_image, mid_x, conditions, font_current), 360), conditions, font = font_current, fill = 0)

    # Future Days
    future_days = []
    for period in periods[1:]:
        if period["isDaytime"] == True:
            future_days.append(period)

    epd.display(epd.getbuffer(image), epd.getbuffer(red_image))

    # epd.sleep()

if __name__ == "__main__":
    main()
