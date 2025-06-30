import json, os, requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

creds_json = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

sheet = client.open(os.getenv("GOOGLE_SHEET_NAME")).worksheet("Hourly")

headers = ["Timestamp", "Temp (°C)", "Feels Like (°C)", "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)", "Wind Deg (°)", "Clouds (%)", "UV Index", "Dew Point (°C)", "Pop", "Description"]

values = sheet.get_all_values()
if len(values) == 0:
    sheet.append_row(headers)
else:
    sheet.clear()
    sheet.append_row(headers)

API_KEY = os.getenv("OPENWEATHER_API_KEY")
LAT, LON = 27.7172, 85.3240
URL = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

data = requests.get(URL).json()

rows = []
for hour in data['hourly']:
    row = [
        datetime.fromtimestamp(hour['dt']).strftime('%Y-%m-%d %H:%M:%S'),
        hour['temp'],
        hour['feels_like'],
        hour['humidity'],
        hour['pressure'],
        hour['wind_speed'],
        hour.get('wind_deg'),
        hour['clouds'],
        hour.get('uvi'),
        hour['dew_point'],
        hour.get('pop'),
        hour['weather'][0]['description']
    ]
    rows.append(row)

sheet.append_rows(rows)
