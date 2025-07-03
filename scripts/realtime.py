import os
import requests
from datetime import datetime
import pytz
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Google Sheets setup ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)
sheet = client.open("WeatherLog").worksheet("Current")

# --- API Config ---
API_KEY = os.getenv("TOMORROW_API_KEY")
LAT = 27.7172
LON = 85.3240
nepal_tz = pytz.timezone('Asia/Kathmandu')

# --- Request Real-time Weather ---
url = f"https://api.tomorrow.io/v4/weather/realtime?location={LAT},{LON}&apikey={API_KEY}"
response = requests.get(url)
data = response.json()

# --- Parse data ---
values = data['data']['values']
api_time_str = data['data']['time']
timestamp = datetime.fromisoformat(api_time_str.replace("Z", "+00:00")).astimezone(nepal_tz).strftime('%Y-%m-%d %H:%M:%S')

# --- Relevant Weather Fields (No Freezing Rain) ---
headers = [
    "Timestamp", "Temperature (°C)", "Apparent Temp (°C)", "Dew Point (°C)", "Humidity (%)",
    "Rain Intensity (mm/hr)", "Sleet Intensity",
    "Cloud Cover (%)", "Cloud Base (km)", "Cloud Ceiling (km)",
    "Visibility (km)", "UV Index", "UV Health Concern",
    "Wind Speed (m/s)", "Wind Direction (°)", "Wind Gust (m/s)",
    "Altimeter Setting (hPa)", "Pressure Sea Level (hPa)", "Pressure Surface Level (hPa)",
    "Weather Code"
]

data_row = [
    timestamp,
    values.get("temperature"),
    values.get("temperatureApparent"),
    values.get("dewPoint"),
    values.get("humidity"),
    values.get("rainIntensity"),
    values.get("sleetIntensity"),
    values.get("cloudCover"),
    values.get("cloudBase"),
    values.get("cloudCeiling"),
    values.get("visibility"),
    values.get("uvIndex"),
    values.get("uvHealthConcern"),
    values.get("windSpeed"),
    values.get("windDirection"),
    values.get("windGust"),
    values.get("altimeterSetting"),
    values.get("pressureSeaLevel"),
    values.get("pressureSurfaceLevel"),
    values.get("weatherCode")
]

# --- Write headers if sheet is empty ---
if not sheet.row_values(1):
    sheet.append_row(headers)

# --- Append data row ---
sheet.append_row(data_row)
print("✅ Real-time weather data appended successfully!")
