import requests
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === OpenWeather API Setup ===
API_KEY = os.getenv("OPENWEATHER_API_KEY")  # Use environment variable
CITY = "Kathmandu"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = "service_account.json"  # Path to your service account JSON key file
creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
client = gspread.authorize(creds)
sheet = client.open("WeatherLog").sheet1

# === Fetch Weather Data ===
response = requests.get(URL)
data = response.json()

timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M:%S')
sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M:%S')

# === Append Row to Google Sheet ===
sheet.append_row([
    timestamp, CITY, temp, feels_like, temp_min, temp_max, humidity,
    pressure, wind_speed, wind_deg, visibility, clouds, desc, sunrise, sunset
])

print("✅ Weather data logged successfully.")
