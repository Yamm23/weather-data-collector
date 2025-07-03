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

# Read existing dates in the first column to avoid duplicates
existing_dates = sheet.col_values(1)

for day in days:
    dt = datetime.fromisoformat(day['time'][:-1]).astimezone(nepal_tz).strftime('%Y-%m-%d')
    if dt not in existing_dates:
        values = day['values']
        # Sunrise and Sunset may be timestamps or strings; convert if timestamps
        sunrise = values.get("sunriseTime")
        sunset = values.get("sunsetTime")

        # Convert sunrise and sunset ISO strings to local time formatted HH:MM:SS if present
        def convert_time(timestr):
            if timestr:
                try:
                    dt_obj = datetime.fromisoformat(timestr[:-1]).astimezone(nepal_tz)
                    return dt_obj.strftime('%H:%M:%S')
                except Exception:
                    return timestr
            return ""

        sunrise_fmt = convert_time(sunrise)
        sunset_fmt = convert_time(sunset)

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
            sunrise_fmt,
            sunset_fmt
        ]
        sheet.append_row(row)

print("Daily weather forecast updated with new dates!")
