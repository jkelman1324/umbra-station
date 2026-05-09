import requests

def get_coordinates():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data['lat'], data['lon']
    except Exception as e:
        print(f"Error: {e}")

def main():
    lat, lon = get_coordinates()
    print(f"Latitude: {lat} | Longitude: {lon}")

if __name__ == "__main__":
    main()
