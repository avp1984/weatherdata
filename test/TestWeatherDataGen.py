import unittest
from datetime import datetime
import sys, os
sys.path.append(os.path.abspath(os.path.join('.', 'src')))
sys.path.append('WeatherDataGen')
import WeatherDataGen as wd

class TestWeatherDataGen(unittest.TestCase):

    def test_gen_dummy_weather(self):
        dt = datetime.strptime('2019-03-01 10:10:10', '%Y-%m-%d %H:%M:%S')
        data = wd.gen_dummy_weather("Sydney", "-33.8548157,151.2164539", "10", dt, "-10y")
        self.assertTrue('Sydney|-33.8548157,151.2164539' in data)

    def test_get_geo_loc(self):
        loc = "Sydney"
        data = wd.get_geo_loc("Sydney")
        self.assertEqual('-33.8548157,151.2164539', data)

    def test_calc_pressure(self):
        data = wd.calc_pressure(34, 10.3)
        self.assertEqual(round(1013.02918833, 1), round(data, 1))

    def test_calc_humidity(self):
        data = wd.calc_humidity(34, -1)
        self.assertEqual(round(75.0, 1), round(data, 1))   

    def test_get_random_date(self):
        dt = datetime.strptime('2019-03-01 10:10:10', '%Y-%m-%d %H:%M:%S')
        data = wd.get_random_date(dt, "-0y")
        self.assertTrue("2019" in str(data))   

if __name__ == '__main__':
    unittest.main()

