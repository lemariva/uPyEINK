"""
 Copyright [2019] [Mauro Riva <info@lemariva.com> <lemariva.com>]

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.
"""

import gc
import urequests

WIDGET_WIDTH = 190
WIDGET_HEIGHT = 384

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
