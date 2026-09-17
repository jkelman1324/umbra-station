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
        "Cloudy": "cloud.fill@3x.png",
        "Mostly Sunny": "sun.max.fill@3x.png",
        "Partly Sunny": "cloud.sun.fill@3x.png",
        "Sunny": "sun.max.fill@3x.png",
    },
    "night": {
        "Partly Cloudy": "cloud.moon@3x.png",
    },
}

# Fonts
font24 = ImageFont.truetype(font_path, 24)
font48 = ImageFont.truetype(font_path, 48)
bold24 = ImageFont.truetype(bold_font_path, 24)
bold36 = ImageFont.truetype(bold_font_path, 36)
bold48 = ImageFont.truetype(bold_font_path, 48)

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

def draw_current_weather(image, draw_image, current_period):
    font_current = bold36

    # Border
    x1 = 10
    y1 = 130
    x2 = 260
    y2 = 410
    mid_x = (x1 + x2) / 2
    padding = 10
    draw_image.rectangle((x1, y1, x2, y2))

    # Time
    time = datetime.fromisoformat(current_period["startTime"]).strftime("%-I %p")
    draw_image.text((center_justified_x(draw_image, mid_x, time, font_current), y1 + padding), time, font = font_current, fill = 0)

    # Icon
    icon = get_weather_icon(
        current_period["shortForecast"],
        current_period["isDaytime"]
    )
    icon_size = 96
    icon_bg = Image.new("L", icon.size, 255)
    icon_bg.paste(0, mask=icon.getchannel("A"))
    image.paste(icon_bg, (int(mid_x - icon_size / 2), 200))

    # Temp
    temp = f"{current_period["temperature"]}°"
    draw_image.text((center_justified_x(draw_image, mid_x, temp, font_current), 310), temp, font = font_current, fill = 0)

    # Conditions
    conditions = current_period["shortForecast"]
    draw_image.text((center_justified_x(draw_image, mid_x, conditions, font_current), 360), conditions, font = font_current, fill = 0)

def draw_forecasted_weather(image, draw_image, i, period):
    forecast_font = bold36

    # Border
    x1 = 260 + int((790 - 260) / 4) * (i - 1)
    y1 = 130
    x2 = 392 + int((790 - 260) / 4) * (i - 1)
    y2 = 410
    mid_x = (x1 + x2) / 2
    padding = 10
    draw_image.rectangle((x1, y1, x2, y2))

    # Time
    time = datetime.fromisoformat(period["startTime"]).strftime("%-I %p")
    draw_image.text((center_justified_x(draw_image, mid_x, time, forecast_font), y1 + padding), time, font = forecast_font, fill = 0)

    # Icon
    icon = get_weather_icon(
        period["shortForecast"],
        period["isDaytime"]
    )
    icon_bg = Image.new("L", icon.size, 255)
    icon_bg.paste(0, mask=icon.getchannel("A"))
    # icon_bg = icon_bg.resize((72, 72), Image.Resampling.LANCZOS)
    image.paste(icon_bg, (int(mid_x - icon_bg.width / 2), 200))

    # Temp
    temp = f"{period["temperature"]}°"
    draw_image.text((center_justified_x(draw_image, mid_x, temp, forecast_font), 310), temp, font = forecast_font, fill = 0)

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

    # Title
    title = f"{city} Forecast"
    draw_image.text((10, 10), title, font = bold48, fill = 0)
    line_end_x = 10 + draw_image.textlength(title, font = bold48)
    draw_image.line((10, 60, line_end_x, 60), fill = 0)

    draw_current_weather(image, draw_image, periods[0])

    for i in range(1, 5):
        draw_forecasted_weather(image, draw_image, i, periods[i])

    epd.display(epd.getbuffer(image), epd.getbuffer(red_image))

    # epd.sleep()


if __name__ == "__main__":
    main()
