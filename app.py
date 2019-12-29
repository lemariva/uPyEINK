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
import e7in5
import settings
import functions

import utime
import font16
import font8
import machine
from microWebSrv import MicroWebSrv

from widgets.forecast import ForecastWidget
from widgets.news import NewsWidget
import widgets.notes as NoteServer

DELAY_TIME = 600000

busy = machine.Pin(25, mode=machine.Pin.IN)
cs = machine.Pin(15, mode=machine.Pin.OUT)
rst = machine.Pin(26, mode=machine.Pin.OUT)
dc = machine.Pin(27, mode=machine.Pin.OUT)
sck = machine.Pin(13, mode=machine.Pin.OUT)
miso = machine.Pin(12, mode=machine.Pin.IN)
mosi = machine.Pin(14, mode=machine.Pin.OUT)

## Server
NoteServer.run()
## Display
epd = e7in5.EPD(rst, dc, busy, cs, sck, mosi, miso)
gc.collect()

def run():
    epd.init_v1()
    while True:
        try:
            epd.clear_frame()
            gc.collect()
            ## Weather Section
            weather_widget = ForecastWidget(api_key=settings.weather_api_key, location=settings.location)
            weather = weather_widget.get_data()
            weather_widget = None

            epd.display_string_at(5, 5, weather['city']['name'], font16, e7in5.UNCOLORED)
            epd.display_string_at(5, 25, "Sunrise: ", font16, e7in5.UNCOLORED)
            epd.display_string_at(100, 25, functions.seconds_to_text(weather['city']['sunrise'], weather['city']['tz']), font16, e7in5.COLORED)
            epd.display_string_at(5, 40, "Sunset: ", font16, e7in5.UNCOLORED)
            epd.display_string_at(100, 40, functions.seconds_to_text(weather['city']['sunset'], weather['city']['tz']), font16, e7in5.COLORED)

            x_move = 110
            for index in weather['next']:
                forecast = weather['next'][index]
                #print(forecast)
                epd.display_string_at(200 + x_move * index, 5, functions.seconds_to_text(forecast['dt'], weather['city']['tz']), font16, e7in5.COLORED)
                epd.display_string_at(200 + x_move * index, 20, forecast['main'], font16, e7in5.UNCOLORED)
                epd.display_string_at(200 + x_move * index, 35, forecast['temp'], font8, e7in5.UNCOLORED)
                epd.display_string_at(200 + x_move * index, 45, forecast['temp_dt'], font8, e7in5.UNCOLORED)
                epd.display_string_at(200 + x_move * index, 55, forecast['wind'], font8, e7in5.UNCOLORED)
                epd.display_string_at(200 + x_move * index, 65, forecast['press'], font8, e7in5.UNCOLORED)
                epd.draw_vertical_line(300 + x_move * index, 5, 65, e7in5.COLORED)

            epd.draw_horizontal_line(1, 75, 640, e7in5.COLORED)
            gc.collect()

            ## News Section
            news_widget = NewsWidget(api_key=settings.news_api_key, country=settings.news_country)
            news = news_widget.get_data()
            news_widget = None

            y_move = 30
            if news['status'] == 'ok':
                for index, article in enumerate(news['articles']):
                    epd.display_string_at(1, 80 + y_move * index,
                                        functions.replace_unicode(article['title']), font16, e7in5.COLORED)
                    epd.display_string_at(5, 95 + y_move * index,
                                        functions.replace_unicode(article['description']), font8, e7in5.UNCOLORED)

            epd.draw_horizontal_line(1, 205, 640, e7in5.COLORED)
            gc.collect()

            ## Notes Section
            get_keys = NoteServer.models_btree.Note.get_keys()
            note_idx = 0
            y_move = 25
            x_move = 320
            for key in get_keys:
                note = NoteServer.models_btree.Note.get_id(key)[0]
                if note.archived == 0:
                    epd.display_string_at(1 + x_move * (note_idx > 5), 210 + y_move * (note_idx - (note_idx > 5) * 6),
                                        functions.replace_unicode(note.timestamp), font8, e7in5.COLORED)
                    epd.display_string_at(1 + x_move * (note_idx > 5), 218 + y_move * (note_idx - (note_idx > 5) * 6),
                                        functions.replace_unicode(note.content), font16, e7in5.UNCOLORED)
                    note_idx = note_idx + 1
            get_keys = None
            note = None
            gc.collect()

            ## Display Update
            epd.display_string_at(1, 375, "updated: %d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[:6], font8, e7in5.COLORED)
            epd.display_frame()
            gc.collect()
            utime.sleep_ms(DELAY_TIME)
            #machine.deepsleep(DELAY_TIME)
        except:
            print("An exception occurred!")
            machine.reset()
