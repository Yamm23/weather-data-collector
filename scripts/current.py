import json, os, requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

creds_json = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

sheet = client.open(os.getenv("GOOGLE_SHEET_NAME")).worksheet("Current")

# Add headers if sheet empty
values = sheet.get_all_values()
if len(values) == 0:
    headers = ["Timestamp", "Temp (°C)", "Feels Like (°C)", "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)", "Wind Deg (°)", "Clouds (%)", "UV Index", "Dew Point (°C)", "Description"]
    sheet.append_row(headers)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT, LON = 27.7172, 85.3240
URL = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

data = requests.get(URL).json()
current = data['current']

row = [
    datetime.fromtimestamp(current['dt']).strftime('%Y-%m-%d %H:%M:%S'),
    current['temp'],
    current['feels_like'],
    current['humidity'],
    current['pressure'],
    current['wind_speed'],
    current.get('wind_deg'),
    current['clouds'],
    current.get('uvi'),
    current['dew_point'],
    current['weather'][0]['description']
]
sheet.append_row(row)
