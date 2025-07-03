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

# --- Configuration ---
LAT = 27.7172
LON = 85.3240
TOMORROW_API_KEY = os.getenv("TOMORROW_API_KEY")
nepal_tz = pytz.timezone("Asia/Kathmandu")

# --- Google Sheet ---
sheet = client.open("WeatherLog").worksheet("Realtime")  # change tab if needed

# --- API Request ---
url = f"https://api.tomorrow.io/v4/weather/realtime?location={LAT},{LON}&apikey={TOMORROW_API_KEY}"
response = requests.get(url)
data = response.json()

# --- Parse and Extract ---
values = data['data']['values']

timestamp = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(nepal_tz).strftime('%Y-%m-%d %H:%M:%S')
temperature = values.get('temperature')
apparent_temperature = values.get('temperatureApparent')
humidity = values.get('humidity')
wind_speed = values.get('windSpeed')
wind_direction = values.get('windDirection')
pressure = values.get('pressureSeaLevel')
precipitation = values.get('precipitationIntensity', 0.0)
cloud_cover = values.get('cloudCover')
visibility = values.get('visibility')

# --- Prepare Headers and Row ---
headers = [
    "Timestamp", "Temp (°C)", "Apparent Temp (°C)", "Humidity (%)", "Pressure (hPa)",
    "Wind Speed (m/s)", "Wind Direction (°)", "Precipitation (mm/hr)",
    "Cloud Cover (%)", "Visibility (km)"
]

row = [
    timestamp, temperature, apparent_temperature, humidity, pressure,
    wind_speed, wind_direction, precipitation, cloud_cover, visibility
]

# --- Add headers if empty ---
if not sheet.row_values(1):
    sheet.append_row(headers)

# --- Append new row ---
sheet.append_row(row)
print("Realtime weather logged successfully.")
