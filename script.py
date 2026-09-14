import sys
import os
import requests
import json
from datetime import datetime

from waveshare_epd import epd7in5b_V2
from PIL import Image,ImageDraw,ImageFont

sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

project_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(project_dir, 'fonts', 'Sansation-Regular.ttf')
bold_font_path = os.path.join(project_dir, 'fonts', 'Sansation-Regular.ttf')

def get_coordinates():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data['lat'], data['lon']
    except Exception as e:
        print(f"Error: {e}")


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
        url = data['properties']['forecast']
        response = requests.get(url)
        data = response.json()
        periods = data['properties']['periods']
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
    font72 = ImageFont.truetype(font_path, 72)
    bold24 = ImageFont.truetype(bold_font_path, 24)
    bold36 = ImageFont.truetype(bold_font_path, 36)
    bold48 = ImageFont.truetype(bold_font_path, 48)
    bold72 = ImageFont.truetype(bold_font_path, 72)

    # Title
    title = f"{city} Forecast"
    draw_image.text((10, 10), title, font = bold48, fill = 0)
    line_end_x = 10 + draw_image.textlength(title, font = bold48)
    draw_image.line((10, 60, line_end_x, 60), fill = 0)

    # Today/Tonight
    current_period = periods[0]
    current_name = current_period["name"]
    draw_image.rectangle((10, 130, 310, 410))
    x = 20
    y = 150
    draw_image.text((x, y), current_name, font = bold36, fill = 0)
    draw_image.text((x, 310), f"{current_period["temperature"]}°", font = bold36, fill = 0)
    draw_image.text((x, 350), current_period["shortForecast"], font = bold36, fill = 0)

    # Future Days
    future_days = []
    for period in periods[1:]:
        if period["isDaytime"] == True:
            future_days.append(period)

    # epd.display(epd.getbuffer(image), epd.getbuffer(red_image))
    epd.sleep()

if __name__ == "__main__":
    main()
