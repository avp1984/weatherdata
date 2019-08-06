import datetime
import random
import time
import json
import os
import sys

from faker import Faker
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


KELVIN_SCALE = 273.15
HPA_CONVERTION = 1013.25;

#Heavy object, so creating only once per the execution
faker = Faker()

#Weather data blueprint
loc_weather = {"Sunny": {"temp": (30, 17)}, "Rain": {"temp": (25, 17)}, "Snow": {"temp": (0, -5)}}


def get_geo_loc(location_name):
    """Get the latitude and longitude of the game location
    - location
    :return latitude,longitude
    """

    #Uses third party API to get geo position
    try:
        geolocator = Nominatim(user_agent="MacOSX")
        location = geolocator.geocode(location_name)
    except GeocoderTimedOut as e:
        raise RuntimeError('Geocode failed: {}'.format(e.message))
    return str(location.latitude) + "," + str(location.longitude)

def get_random_date(end, year_limit):
    """Use Faker lib to generate a ISO8601 format datetime
    -end
    -year window duration in the past
    :return ISO8601 datetime value
    """

    #Uses Faker for geting fake date by providing a look back years
    dt = faker.date_time_between(end_date=end, start_date=year_limit)
    return dt.isoformat()

def calc_humidity(temp, freez_temp):
    """Returns a calculated humidity using formula RH = 100 - 5(T -Tz)
    - temperature
    - freeze temperature of that location
    :return humidity
    """

    hum = abs(100 - (5 * (temp - freez_temp)))
    return hum

def calc_pressure(temp, elev):
    """Pressure can be calculated using Hypsometric formula P=P0(1- (0.0065h / T + 0.0065h+273.15)) * 5.257
    - temperature
    - elevation
    :return pressure hPa
    """

    height_factor = (0.0065 * float(elev));
    deno = temp + height_factor + KELVIN_SCALE
    pressure_atm = 1 - (height_factor / deno)
    pressure_hpa = (HPA_CONVERTION * pressure_atm)
    return pressure_hpa;

def calc_temperature(temp_max, temp_min):
    """The temperature is found through the mathematical random value, but this API can be extended to find it from paid
    weather data providers
    - location
    :return temperature in celsius
    """

    temp = round(random.uniform(temp_max, temp_min), 1)
    return temp;

def gen_dummy_weather(location, geo, elev, dt, limit):
    """Generate dummy data for weather
    - weather
    - temperature
    - pressure
    - humidity
    :return: location|geo|temperature|weather|temperature|pressure|humidity
    """

    weather_rand = random.choice(list(loc_weather.keys()))
    weather_condition = loc_weather[weather_rand]

    #Can utilize openweathermap API to get real values
    (temp_max, temp_min) = weather_condition["temp"]

    #Get a random temparature based on max and min temperature of the given location
    temperature = round(calc_temperature(temp_max, temp_min), 1)

    #Calculate pressure
    pressure = round(calc_pressure(temperature, elev), 1)

    #Calculate humidity
    humidity = round(calc_humidity(temperature, temp_min),1)

    #Get a fake datetime
    date = get_random_date(dt, limit)

    #Get a fake elevation from base elevation
    elevation = round(random.uniform((float(elev)),2),2)
    return location + "|" + geo + "," + str(elevation) + "|" + date + "|" + weather_rand + "|" + str(temperature) + "|" + str(pressure) + "|" + str(humidity) + "\n"


# Argument parsing and initiation
def main(argv):
    if len(argv) < 3: 
        print('Invalid number of arguments, correct usage is `python WeatherDataGen.py <config_file> <output_file>`\n'
              'Example :>> python src/WeatherDataGen.py src/config.json weatherdata.psv')
        exit()

    config_file = argv[1]
    out_file = argv[2]
    print('Starting Weather Data Generation...')
    dt = datetime.datetime.now()
    try:
        weather_data = open(out_file, "w")
        with open(config_file) as json_file:

            #Load game location configurations
            config_data = json.load(json_file)
            for loc_config in config_data['game-locations']:
                loc = loc_config['loc']
                elev = loc_config['elevation']

                #How much weather data required for the location
                data_count = loc_config['test-data-count']

                look_back = loc_config['look-back']

                #Find the latitude and longitude of the location
                geo = get_geo_loc(loc)
                #elev = requests.get('https://api.open-elevation.com/api/v1/lookup?locations=' + geo)
                for i in range(0, int(data_count)):
                    #Generate weather data
                    data = gen_dummy_weather(loc, geo , elev, dt, look_back)

                    #Persist the weather data
                    weather_data.write(data)
    except RuntimeError as e:
        print('Unexpected error in execution: {}'.format(e.message))
        sys.exit()

    #Close the weather data file
    finally:
        weather_data.close()
    print('Finished Weather Data Generation, data file can be accessed from: {}'.format(out_file))

if __name__ == '__main__':
    main(sys.argv)

