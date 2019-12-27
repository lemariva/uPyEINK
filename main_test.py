import gc
import e7in5 
from machine import Pin

import resources.fonts.font20 as font20
import resources.fonts.font16 as font16
from widgets.forecast import ForecastWidget
import settings

def secondsToText(secs, timezone):
    secs = secs + timezone
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    #result = ("{0} day{1}, ".format(days, "s" if days!=1 else "") if days else "") + \
    result = "{0}:{1}:{2}".format(hours, minutes, seconds)
    return result

busy = Pin(25, mode=Pin.IN)
cs = Pin(15, mode=Pin.OUT)
rst = Pin(26, mode=Pin.OUT)
dc = Pin(27, mode=Pin.OUT)
sck = Pin(13, mode=Pin.OUT)
miso = Pin(12, mode=Pin.IN)
mosi = Pin(14, mode=Pin.OUT)

epd = e7in5.EPD(rst, dc, busy, cs, sck, mosi, miso)
epd.init_v1()

## Weather Section
weather_widget = ForecastWidget(api_key=settings.weather_api_key, location=settings.location)
#weather = weather_widget.get_data()

## Display Images
gc.collect()
gc.mem_free()

fb_size = int(epd.width * epd.height / 4)
frame_black = bytearray(fb_size)
epd.clear_frame(frame_black)

#epd.display_string_at(frame_black, 5, 5, weather['name'], font16, e7in5.UNCOLORED)
#epd.display_string_at(frame_black, 5, 25, "Sunrise: ", font16, e7in5.UNCOLORED)
#epd.display_string_at(frame_black, 100, 25, secondsToText(weather['sys']['sunrise'], weather['timezone']), font16, e7in5.COLORED)
#epd.display_string_at(frame_black, 5, 40, "Sunset: ", font16, e7in5.UNCOLORED)
#epd.display_string_at(frame_black, 100, 40, secondsToText(weather['sys']['sunset'], weather['timezone']), font16, e7in5.COLORED)

#epd.draw_vertical_line(frame_black, 10, 1, 384, e7in5.COLORED)
#epd.draw_horizontal_line(frame_black, 1, 1, 640, e7in5.UNCOLORED)
epd.display_string_at(frame_black, 20, 30, "Waveshare E-INK working test", font20, e7in5.COLORED)
#epd.draw_bmp(frame_black, 'resources/icons/10d.bmp', e7in5.COLORED)

epd.display_frame(frame_black)
gc.collect()

