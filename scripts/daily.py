import json, os, requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

creds_json = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

sheet = client.open(os.getenv("GOOGLE_SHEET_NAME")).worksheet("Daily")

headers = ["Date", "Temp Min (°C)", "Temp Max (°C)", "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)", "Wind Deg (°)", "Clouds (%)", "UV Index", "Dew Point (°C)", "Pop", "Description"]

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
for day in data['daily']:
    row = [
        datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d'),
        day['temp']['min'],
        day['temp']['max'],
        day['humidity'],
        day['pressure'],
        day['wind_speed'],
        day.get('wind_deg'),
        day['clouds'],
        day.get('uvi'),
        day['dew_point'],
        day.get('pop'),
        day['weather'][0]['description']
    ]
    rows.append(row)

sheet.append_rows(rows)
