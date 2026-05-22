import requests
import json

def get_coordinates():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data['lat'], data['lon']
    except Exception as e:
        print(f"Error: {e}")

def main():
    lat, lon = get_coordinates()

    try:
        response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
        data = response.json()
        url = data['properties']['forecast']
        response = requests.get(url)
        data = response.json()
        periods = data['properties']['periods']
        print(json.dumps(periods, indent = 4))
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
