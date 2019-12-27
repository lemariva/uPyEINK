import gc
import urequests

WIDGET_WIDTH = 190
WIDGET_HEIGHT = 384

icon_map = {
    "snow": ["snow", "sleet"],
    "rain": ["rain"],
    "cloud": ["fog", "cloudy", "partly-cloudy-day", "partly-cloudy-night"],
    "sun": ["clear-day", "clear-night"],
    "storm": [],
    "wind": ["wind"]
}

class ForecastWidget:

    def __init__(self, language="en", api_key=None, units="metric", hours="12", location="Hannover, DE"):
        if (api_key is None or ""):
            raise ValueError('API key is missing')

        self._location = location
        self._language = language
        self._api_key = api_key

    def _refresh_weather(self):
        url = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}".format(self._location, self._api_key)
        print(url)
        r = urequests.get(url)
        gc.collect()
        return r.json()

    def get_data(self, hours_break=1):
        weather = {}
        weather_raw = self._refresh_weather()
        weather['city'] = {}
        weather['city']['s+'] = weather_raw['city']['sunrise']
        weather['city']['s-'] = weather_raw['city']['sunset']
        weather['city']['n'] = weather_raw['city']['name'] + ", " + weather_raw['city']['country']
        weather['city']['tz'] = weather_raw['city']['timezone']
  
        weather['next'] = {}
        for idx, item in enumerate(weather_raw['list']):
            weather['next'][idx] = {}
            weather['next'][idx]['dt'] = item['dt']
            #weather['next'][idx]['icon'] = item['weather'][0]['icon']
            weather['next'][idx]['m'] = item['weather'][0]['main']
            #weather['next'][idx]['description'] = item['weather'][0]['description']
            weather['next'][idx]['w'] = str(item['wind']['speed']) + "km/h " + str(item['wind']['deg']) + "°"
            weather['next'][idx]['t'] = str(item['main']['temp']) + "° ({0}°)".format(item['main']['feels_like'])
            #weather['next'][idx]['tl'] = "{0}°m - {1}°M".format(item['main']['temp_max'], item['main']['temp_min'])
            #weather['next'][idx]['p'] = item['main']['pressure']

            if(idx > hours_break):
                break
        
        weather_raw = []
        urequests = []
        gc.collect()
        gc.mem_free()

        return weather
