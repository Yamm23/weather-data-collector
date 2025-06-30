import os
import requests
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Setup Google Sheets client ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

# Nepal timezone
nepal_tz = pytz.timezone('Asia/Kathmandu')

sheet = client.open("WeatherLog").sheet1  # or use .worksheet("Current")

# OpenWeather API config
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Kathmandu"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Fetch weather data
response = requests.get(URL)
data = response.json()

# Extract data
timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(nepal_tz).strftime('%Y-%m-%d %H:%M:%S')
temp = data['main']['temp']
feels_like = data['main']['feels_like']
temp_min = data['main']['temp_min']
temp_max = data['main']['temp_max']
humidity = data['main']['humidity']
pressure = data['main']['pressure']
wind_speed = data['wind']['speed']
wind_deg = data['wind'].get('deg', None)
visibility = data.get('visibility', None)
clouds = data['clouds']['all']
desc = data['weather'][0]['description']
weather_main = data['weather'][0]['main']
weather_id = data['weather'][0]['id']
rain_1h = data.get('rain', {}).get('1h', 0.0)
snow_1h = data.get('snow', {}).get('1h', 0.0)
sunrise = datetime.fromtimestamp(data['sys']['sunrise'], tz=pytz.utc).astimezone(nepal_tz).strftime('%H:%M:%S')
sunset = datetime.fromtimestamp(data['sys']['sunset'], tz=pytz.utc).astimezone(nepal_tz).strftime('%H:%M:%S')

# Headers & data row
headers = [
    "Timestamp", "Temp (°C)", "Feels Like (°C)", "Temp Min (°C)", "Temp Max (°C)",
    "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)", "Wind Direction (deg)",
    "Visibility (m)", "Cloudiness (%)", "Description", "Weather Main", "Weather ID",
    "Rain (mm)", "Snow (mm)", "Sunrise (HH:MM:SS)", "Sunset (HH:MM:SS)"
]

data_row = [
    timestamp, temp, feels_like, temp_min, temp_max, humidity, pressure,
    wind_speed, wind_deg, visibility, clouds, desc, weather_main, weather_id,
    rain_1h, snow_1h, sunrise, sunset
]

# Write headers if empty
if not sheet.row_values(1):
    sheet.append_row(headers)

# Append data
sheet.append_row(data_row)

print("Weather data appended successfully!")
