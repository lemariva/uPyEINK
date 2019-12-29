import gc
import e7in5
from machine import Pin

import utime
from microWebSrv import MicroWebSrv
import font16
import font8

from widgets.forecast import ForecastWidget
from widgets.news import NewsWidget
import widgets.notes_server as NoteServer

import settings
import functions

DELAY_TIME = 10000

busy = Pin(25, mode=Pin.IN)
cs = Pin(15, mode=Pin.OUT)
rst = Pin(26, mode=Pin.OUT)
dc = Pin(27, mode=Pin.OUT)
sck = Pin(13, mode=Pin.OUT)
miso = Pin(12, mode=Pin.IN)
mosi = Pin(14, mode=Pin.OUT)

## Server
NoteServer.run()
gc.collect()

## Display
epd = e7in5.EPD(rst, dc, busy, cs, sck, mosi, miso)

while True:
    epd.init_v1()
    epd.clear_frame()
    gc.collect()
    print("loading data...")
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
    get_keys = NoteServer.Note.get_keys()
    note_idx = 0
    y_move = 25
    x_move = 320
    for key in get_keys:
        note = NoteServer.Note.get_id(key)[0]
        if note.archived == 0:
            epd.display_string_at(1 + x_move * (note_idx > 5), 210 + y_move * (note_idx - (note_idx > 5) * 5),
                                  functions.replace_unicode(note.timestamp), font8, e7in5.COLORED)
            epd.display_string_at(1 + x_move * (note_idx > 5), 218 + y_move * (note_idx - (note_idx > 5) * 5),
                                  functions.replace_unicode(note.content), font16, e7in5.UNCOLORED)
            note_idx = note_idx + 1
        gc.collect()
    get_keys = None
    note = None
    gc.collect()

    ## Display Update
    print("updating display...")
    epd.display_string_at(1, 375, "updated: %d-%02d-%02d %02d:%02d:%02d" % utime.localtime()[:6], font8, e7in5.COLORED)
    epd.display_frame()
    print("updated...")
    gc.collect()
    utime.sleep_ms(DELAY_TIME)
    