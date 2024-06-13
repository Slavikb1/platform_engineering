import datetime
import requests

WEEK = 7
DAY = 24


def get_date():
    """
    function get dates for full week in Israely format
    """
    date = []
    for i in range(WEEK):
        date.append((datetime.date.today()+datetime.timedelta(i)).strftime('%d/%m/%Y'))
    return date


def get_day():
    """
    function get days of the week for full week as a day name format
    """
    day_of_week = []
    dt = datetime.datetime.now().date()
    for i in range(WEEK):
        day_of_week.append((dt + datetime.timedelta(i)).strftime('%A'))
    return day_of_week


def lat_lon(city, key):
    """
    function get the longitude, altitude and country code from the API
    Input: city name, API key
    Output: longitude, altitude and country code
    """
    openweathermap_data = []
    geo_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={key}"
    geo_data = requests.get(geo_url)
    if not geo_data:
        return 0
    geo_data = geo_data.json() #removed the city from format to see if its working

    openweathermap_data.append(geo_data['coord']['lon'])
    openweathermap_data.append(geo_data['coord']['lat'])
    openweathermap_data.append(geo_data['sys']['country'])
    # icon = geo_data['weather'][0]['icon']
    return openweathermap_data


def weather_data(lon, lat):
    """
    function get the weather data from the API
    Input: longitude, altitude
    Output: weekly day temperature, night temperature and daily humidity average
    """
    # CONST hours probe for average temperatures
    H_PROBE = 6
    open_meteo_data = []
    data_url = (f"https://api.open-meteo.com/v1/forecast?latitude={lon}&longitude={lat}"
                f"&hourly=temperature_2m,relative_humidity_2m")
    data = requests.get(data_url)
    if not data:
        return 0
    data = data.json()
    temperature = data['hourly']['temperature_2m']
    humidity = data['hourly']['relative_humidity_2m']
    day_temp_avg = []
    night_temp_avg = []
    humidity_avg = []

    for i in range(WEEK):
        humidity_avg.append(sum(humidity[:DAY]) / DAY)
        humidity = humidity[DAY:]

        night_temp_avg.append((sum(temperature[:6]))/H_PROBE)
        temperature = temperature[10:]

        day_temp_avg.append(sum(temperature[:6])/H_PROBE)
        temperature = temperature[14:]

    open_meteo_data.append(day_temp_avg)
    open_meteo_data.append(night_temp_avg)
    open_meteo_data.append(humidity_avg)
    open_meteo_data.append(get_day())
    open_meteo_data.append(get_date())

    return open_meteo_data
