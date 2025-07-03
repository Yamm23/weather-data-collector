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

sheet = client.open("WeatherLog").worksheet("Daily")

# Tomorrow.io API Config
API_KEY = os.getenv("TOMORROW_API_KEY")
LAT = 27.7172
LON = 85.3240

# Endpoint for Daily Forecast (Timeline)
url = (
    f"https://api.tomorrow.io/v4/weather/forecast?location={LAT},{LON}"
    f"&timesteps=1d&apikey={API_KEY}"
)

response = requests.get(url)
data = response.json()

days = data['timelines']['daily']

headers = [
    "Date", "Temp Max (C)", "Temp Min (C)", "Humidity (%)",
    "Wind Speed (m/s)", "Cloud Cover (%)", "Precipitation (mm)",
    "UV Index", "Weather Code", "Sunrise", "Sunset"
]

# Write headers if sheet is empty
if not sheet.row_values(1):
    sheet.append_row(headers)

# Clear previous content (optional if you only want 1 record per day)
sheet.clear()
sheet.append_row(headers)

for day in days:
    values = day['values']
    dt = datetime.fromisoformat(day['time'][:-1]).astimezone(nepal_tz).strftime('%Y-%m-%d')
    sunrise = datetime.fromisoformat(values.get("sunriseTime")[:-1]).astimezone(nepal_tz).strftime('%H:%M:%S') if values.get("sunriseTime") else None
    sunset = datetime.fromisoformat(values.get("sunsetTime")[:-1]).astimezone(nepal_tz).strftime('%H:%M:%S') if values.get("sunsetTime") else None
    row = [
        dt,
        values.get("temperatureMax"),
        values.get("temperatureMin"),
        values.get("humidityAvg"),
        values.get("windSpeedAvg"),
        values.get("cloudCoverAvg"),
        values.get("precipitationSum"),
        values.get("uvIndexMax"),
        values.get("weatherCodeMax"),
        sunrise,
        sunset
    ]
    sheet.append_row(row)

print("Daily weather forecast updated!")
