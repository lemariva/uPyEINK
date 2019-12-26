import e7in5 
import gc
from machine import Pin
import fonts.font20 as font20

busy = Pin(25, mode=Pin.IN)
cs = Pin(15, mode=Pin.OUT)
rst = Pin(26, mode=Pin.OUT)
dc = Pin(27, mode=Pin.OUT)
sck = Pin(13, mode=Pin.OUT)
miso = Pin(12, mode=Pin.IN)
mosi = Pin(14, mode=Pin.OUT)

epd = e7in5.EPD(rst, dc, busy, cs, sck, mosi, miso)

epd.init_v1()

fb_size = int(epd.width * epd.height / 4)
frame_black = bytearray(fb_size)

epd.clear_frame(frame_black)

epd.draw_vertical_line(frame_black, 10, 1, 384, e7in5.COLORED)

epd.draw_horizontal_line(frame_black, 1, 1, 640, e7in5.UNCOLORED)
epd.display_string_at(frame_black, 20, 30, "Waveshare E-INK working test", font20, e7in5.COLORED)

epd.display_frame(frame_black)
gc.collect()

