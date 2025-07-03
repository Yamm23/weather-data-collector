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
    "Date",
    "Temp Max (°C)",
    "Temp Min (°C)",
    "Humidity Avg (%)",
    "Pressure Sea Level Avg (hPa)",
    "Pressure Surface Level Avg (hPa)",
    "Altimeter Setting Avg (hPa)",
    "Cloud Cover Avg (%)",
    "Cloud Base Avg (km)",
    "Cloud Ceiling Avg (km)",
    "Wind Speed Avg (m/s)",
    "Wind Speed Max (m/s)",
    "Wind Gust Max (m/s)",
    "Wind Direction Avg (°)",
    "Rain Accumulation Sum (mm)",
    "Rain Intensity Max (mm/hr)",
    "Sleet Intensity Max (mm/hr)",
    "Precipitation Probability Max (%)",
    "Visibility Max (km)",
    "UV Index Max",
    "Sunrise Time",
    "Sunset Time",
    "Weather Code Max"
]

# Write headers if sheet is empty
if not sheet.row_values(1):
    sheet.append_row(headers)

# Read existing dates in the first column to avoid duplicates
existing_dates = sheet.col_values(1)

def convert_time(timestr):
    if timestr:
        try:
            dt_obj = datetime.fromisoformat(timestr[:-1]).astimezone(nepal_tz)
            return dt_obj.strftime('%H:%M:%S')
        except Exception:
            return timestr
    return ""

for day in days:
    dt = datetime.fromisoformat(day['time'][:-1]).astimezone(nepal_tz).strftime('%Y-%m-%d')
    if dt not in existing_dates:
        v = day['values']
        row = [
            dt,
            v.get("temperatureMax"),
            v.get("temperatureMin"),
            v.get("humidityAvg"),
            v.get("pressureSeaLevelAvg"),
            v.get("pressureSurfaceLevelAvg"),
            v.get("altimeterSettingAvg"),
            v.get("cloudCoverAvg"),
            v.get("cloudBaseAvg"),
            v.get("cloudCeilingAvg"),
            v.get("windSpeedAvg"),
            v.get("windSpeedMax"),
            v.get("windGustMax"),
            v.get("windDirectionAvg"),
            v.get("rainAccumulationSum"),
            v.get("rainIntensityMax"),
            v.get("sleetIntensityMax"),
            v.get("precipitationProbabilityMax"),
            v.get("visibilityMax"),
            v.get("uvIndexMax"),
            convert_time(v.get("sunriseTime")),
            convert_time(v.get("sunsetTime")),
            v.get("weatherCodeMax")
        ]
        sheet.append_row(row)

print("Daily weather forecast updated with new fields!")
