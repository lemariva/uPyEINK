import gc
import urequests
gc.collect()

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

    def _refresh_weather(self, lines_break):
        url = "https://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&appid={}&cnt={}".format(self._location, self._api_key, lines_break)
        r = urequests.get(url)
        gc.collect()
        return r.json()

    def get_data(self, lines_break=4):
        weather = {}
        weather_raw = self._refresh_weather(lines_break)
        weather['city'] = {}
        weather['city']['sunrise'] = weather_raw['city']['sunrise']
        weather['city']['sunset'] = weather_raw['city']['sunset']
        weather['city']['name'] = weather_raw['city']['name'] + ", " + weather_raw['city']['country']
        weather['city']['tz'] = weather_raw['city']['timezone']
  
        weather['next'] = {}
        for idx, item in enumerate(weather_raw['list']):
            weather['next'][idx] = {}
            weather['next'][idx]['dt'] = item['dt']
            weather['next'][idx]['icon'] = item['weather'][0]['icon']
            weather['next'][idx]['main'] = item['weather'][0]['main']
            weather['next'][idx]['desc'] = item['weather'][0]['description']
            weather['next'][idx]['wind'] = "{0}km/h ({1}dg)".format(item['wind']['speed'], item['wind']['deg'])
            weather['next'][idx]['temp'] = "{0} (f:{1})".format(str(item['main']['temp']), item['main']['feels_like'])
          
            if item['main']['temp_max'] - item['main']['temp'] > item['main']['temp'] - item['main']['temp_min']:
                weather['next'][idx]['temp_dt'] = "+/- {}".format(item['main']['temp_max'] - item['main']['temp'])
            else:
                weather['next'][idx]['temp_dt'] = "+/- {}".format(item['main']['temp'] - item['main']['temp_min'])
            
            weather['next'][idx]['press'] = "{}p".format(item['main']['pressure'])
        
        weather_raw = None
        gc.collect()
        gc.mem_free()

        return weather
