import os
import requests
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Setup Google Sheets client ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

sheet = client.open("WeatherLog").sheet1  # Make sure your sheet name matches

# --- Fetch weather data from OpenWeather API ---
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = "Kathmandu"
url = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

response = requests.get(url)
data = response.json()

# --- Extract data ---
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

# --- Prepare headers and data row ---
headers = [
    "Timestamp", "Temp (°C)", "Feels Like (°C)", "Temp Min (°C)", "Temp Max (°C)",
    "Humidity (%)", "Pressure (hPa)", "Wind Speed (m/s)", "Wind Direction (deg)",
    "Visibility (m)", "Cloudiness (%)", "Description", "Sunrise (HH:MM:SS)", "Sunset (HH:MM:SS)"
]

data_row = [
    timestamp, temp, feels_like, temp_min, temp_max, humidity, pressure,
    wind_speed, wind_deg, visibility, clouds, desc, sunrise, sunset
]

# --- Write headers if sheet is empty ---
if not sheet.row_values(1):
    sheet.append_row(headers)

# --- Append the weather data ---
sheet.append_row(data_row)

print("Weather data appended successfully!")
