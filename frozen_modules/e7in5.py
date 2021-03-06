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
import utime
from machine import Pin, SPI
from bmp import BitmapHeader, BitmapHeaderInfo
gc.collect()

# Display resolution
EPD_WIDTH = 640
EPD_HEIGHT = 384

# EPD1IN54B commands
PANEL_SETTING = 0x00
POWER_SETTING = 0x01
POWER_OFF = 0x02
POWER_OFF_SEQUENCE_SETTING = 0x03
POWER_ON = 0x04
POWER_ON_MEASURE = 0x05
BOOSTER_SOFT_START = 0x06
DEEP_SLEEP = 0x07
DATA_START_TRANSMISSION_1 = 0x10
DATA_STOP = 0x11
DISPLAY_REFRESH = 0x12
DATA_START_TRANSMISSION_2 = 0x13
PLL_CONTROL = 0x30
TEMPERATURE_SENSOR_COMMAND = 0x40
TEMPERATURE_SENSOR_CALIBRATION = 0x41
TEMPERATURE_SENSOR_WRITE = 0x42
TEMPERATURE_SENSOR_READ = 0x43
VCOM_AND_DATA_INTERVAL_SETTING = 0x50
LOW_POWER_DETECTION = 0x51
TCON_SETTING = 0x60
TCON_RESOLUTION = 0x61
SOURCE_AND_GATE_START_SETTING = 0x62
GET_STATUS = 0x71
AUTO_MEASURE_VCOM = 0x80
VCOM_VALUE = 0x81
VCM_DC_SETTING_REGISTER = 0x82
PROGRAM_MODE = 0xA0
ACTIVE_PROGRAM = 0xA1
READ_OTP_DATA = 0xA2

# Color or no color
COLORED = 1
UNCOLORED = 0

# Display orientation
ROTATE_0 = 0
ROTATE_90 = 1
ROTATE_180 = 2
ROTATE_270 = 3

class EPD:
    def __init__(self, reset, dc, busy, cs, clk, mosi, miso):
        self.reset_pin = reset
        self.dc_pin = dc
        self.busy_pin = busy
        self.cs_pin = cs

        self.spi = SPI(1, baudrate=200000, polarity=0, phase=0, sck=clk, miso=miso, mosi=mosi)

        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

        self.rotate = ROTATE_0

        fb_size = int(self.width * self.height / 4)
        self.frame_buffer = bytearray(fb_size)

    def _spi_transfer(self, package):
        self.cs_pin(False)
        self.spi.write(bytearray([package]))
        self.cs_pin(True)

    def init_v1(self):
        self.reset()

        self.send_command(0x01) # POWER_SETTING
        self.send_data(0x37)
        self.send_data(0x00)

        self.send_command(0x00) # PANEL_SETTING
        self.send_data(0xCF)
        self.send_data(0x08)

        self.send_command(0x06) # BOOSTER_SOFT_START
        self.send_data(0xC7)
        self.send_data(0xCC)
        self.send_data(0x28)

        self.send_command(0x04) # POWER_ON
        self.wait_until_idle()

        self.send_command(0x30) # PLL_CONTROL
        self.send_data(0x3C) # PLL:  0-15:0x3C, 15+:0x3A

        self.send_command(0x41) # TEMPERATURE_CALIBRATION
        self.send_data(0x00)

        self.send_command(0x50) # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x77)

        self.send_command(0x60) # TCON_SETTING
        self.send_data(0x22)

        self.send_command(0x61) # TCON_RESOLUTION
        self.send_data(0x02) # source 640
        self.send_data(0x80)
        self.send_data(0x01) # gate 384
        self.send_data(0x80)

        self.send_command(0x82) # VCM_DC_SETTING
        self.send_data(0x1E) #all temperature  range

        self.send_command(0xE5) # FLASH CONTROL
        self.send_data(0x03)

        self.send_command(0x10) # DATA_START_TRANSMISSION_1

        self.delay_ms(2000)

        #self.set_lut_bw()
        #self.set_lut_red()

        return 0

    def init_v2(self):
        self.reset()

        self.send_command(0x01)	# POWER SETTING
        self.send_data(0x07)
        self.send_data(0x07)    # VGH=20V,VGL=-20V
        self.send_data(0x3f)	# VDH=15V
        self.send_data(0x3f)	# VDL=-15V

        self.send_command(0x04) # POWER ON
        self.delay_ms(100)
        self.ready_busy_v2()

        self.send_command(0X00) # PANNEL SETTING
        self.send_data(0x0F)    # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x61)     #tres
        self.send_data(0x03)		#source 800
        self.send_data(0x20)
        self.send_data(0x01)		#gate 480
        self.send_data(0xE0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)			#VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0X60)			#TCON SETTING
        self.send_data(0x22)


        self.send_command(0x10)

        for x in range(0, 800 / 8 * 480):
            self.send_data(0x00)

        self.send_command(0x13)
        for x in range(0, 800 / 8 *480):
            self.send_data(0x00)

        self.send_command(0x10)
        
        gc.collect()
        return 0

    def ready_busy_v2(self):
        while True:
            self.send_command(0x71)
            busy = self.busy_pin()
            busy = not (busy & 0x01)
            if not busy:
                break
        self.delay_ms(200)

    lut_vcom0 = [
        0x0E, 0x14, 0x01, 0x0A, 0x06, 0x04, 0x0A, 0x0A,
        0x0F, 0x03, 0x03, 0x0C, 0x06, 0x0A, 0x00
    ]

    lut_w = [
        0x0E, 0x14, 0x01, 0x0A, 0x46, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x86, 0x0A, 0x04
    ]

    lut_b = [
        0x0E, 0x14, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x4A, 0x04
    ]

    lut_g1 = [
        0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04
    ]

    lut_g2 = [
        0x8E, 0x94, 0x01, 0x8A, 0x06, 0x04, 0x8A, 0x4A,
        0x0F, 0x83, 0x43, 0x0C, 0x06, 0x0A, 0x04
    ]

    lut_vcom1 = [
        0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_red0 = [
        0x83, 0x5D, 0x01, 0x81, 0x48, 0x23, 0x77, 0x77,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    lut_red1 = [
        0x03, 0x1D, 0x01, 0x01, 0x08, 0x23, 0x37, 0x37,
        0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ]

    def delay_ms(self, delaytime):
        utime.sleep_ms(delaytime)

    def send_command(self, command):
        self.dc_pin(0)
        self._spi_transfer(command)

    def send_data(self, data):
        self.dc_pin(True)
        self._spi_transfer(data)

    def wait_until_idle(self):
        while self.busy_pin() == False:      # 0: idle, 1: busy
            self.delay_ms(100)

    def reset(self):
        self.reset_pin(0)         # module reset
        self.delay_ms(200)
        self.reset_pin(1)
        self.delay_ms(200)

    def set_lut_bw(self):
        self.send_command(0x20)               # vcom
        for count in range(0, 15):
            self.send_data(self.lut_vcom0[count])
        self.send_command(0x21)         # ww --
        for count in range(0, 15):
            self.send_data(self.lut_w[count])
        self.send_command(0x22)         # bw r
        for count in range(0, 15):
            self.send_data(self.lut_b[count])
        self.send_command(0x23)         # wb w
        for count in range(0, 15):
            self.send_data(self.lut_g1[count])
        self.send_command(0x24)         # bb b
        for count in range(0, 15):
            self.send_data(self.lut_g2[count])

    def set_lut_red(self):
        self.send_command(0x25)
        for count in range(0, 15):
            self.send_data(self.lut_vcom1[count])
        self.send_command(0x26)
        for count in range(0, 15):
            self.send_data(self.lut_red0[count])
        self.send_command(0x27)
        for count in range(0, 15):
            self.send_data(self.lut_red1[count])


    def clear_frame(self, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        for i in range(int(self.width * self.height / 4)):
            frame_buffer[i] = 0xFF


    def display_frame(self, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
  
        self.send_command(DATA_START_TRANSMISSION_1)
        for i in range(0, int(self.width * self.height / 4)):
            temp1 = frame_buffer[i]
            j = 0
            while j < 4:
                if (temp1 & 0xC0) == 0xC0:
                    temp2 = 0x03
                elif (temp1 & 0xC0) == 0x00:
                    temp2 = 0x00
                else:
                    temp2 = 0x04
                temp2 = (temp2 << 4) & 0xFF
                temp1 = (temp1 << 2) & 0xFF
                j += 1
                if (temp1 & 0xC0) == 0xC0:
                    temp2 |= 0x03
                elif (temp1 & 0xC0) == 0x00:
                    temp2 |= 0x00
                else:
                    temp2 |= 0x04
                temp1 = (temp1 << 2) & 0xFF
                self.send_data(temp2)
                j += 1
        self.send_command(DISPLAY_REFRESH)
        self.delay_ms(100)
        self.wait_until_idle()
        gc.collect()

    # after this, call epd.init() to awaken the module
    def sleep(self):
        self.send_command(VCOM_AND_DATA_INTERVAL_SETTING)
        self.send_data(0x17)
        self.send_command(VCM_DC_SETTING_REGISTER)         #to solve Vcom drop
        self.send_data(0x00)
        self.send_command(POWER_SETTING)         #power setting
        self.send_data(0x02)        #gate switch to external
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x00)
        self.wait_until_idle()
        self.send_command(POWER_OFF)         #power off

    def set_rotate(self, rotate):
        if rotate == ROTATE_0:
            self.rotate = ROTATE_0
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        elif rotate == ROTATE_90:
            self.rotate = ROTATE_90
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH
        elif rotate == ROTATE_180:
            self.rotate = ROTATE_180
            self.width = EPD_WIDTH
            self.height = EPD_HEIGHT
        elif rotate == ROTATE_270:
            self.rotate = ROTATE_270
            self.width = EPD_HEIGHT
            self.height = EPD_WIDTH

    def set_pixel(self, x, y, colored, frame_buffer):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return
        if self.rotate == ROTATE_0:
            self.set_absolute_pixel(x, y, colored, frame_buffer)
        elif self.rotate == ROTATE_90:
            point_temp = x
            x = EPD_WIDTH - y
            y = point_temp
            self.set_absolute_pixel(x, y, colored, frame_buffer)
        elif self.rotate == ROTATE_180:
            x = EPD_WIDTH - x
            y = EPD_HEIGHT- y
            self.set_absolute_pixel(x, y, colored, frame_buffer)
        elif self.rotate == ROTATE_270:
            point_temp = x
            x = y
            y = EPD_HEIGHT - point_temp
            self.set_absolute_pixel(x, y, colored, frame_buffer)


    def set_absolute_pixel(self, x, y, colored, frame_buffer=None):
        # To avoid display orientation effects
        # use EPD_WIDTH instead of self.width
        # use EPD_HEIGHT instead of self.height
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        if x < 0 or x >= EPD_WIDTH or y < 0 or y >= EPD_HEIGHT:
            return

        if colored:
            frame_buffer[int((x + y * EPD_WIDTH) / 4)] &= ~(0xC0 >> (x % 4 * 2))
            frame_buffer[int((x + y * EPD_WIDTH) / 4)] |= 0x40 >> (x % 4 * 2)
        else:
            frame_buffer[int((x + y * EPD_WIDTH) / 4)] &= ~(0xC0 >> (x % 4 * 2))

            #frame_buffer[int((x + y * EPD_WIDTH) / 4)] |= (0x80 >> (x % 8))
            #print(0x80 >> (x % 4))


    def draw_char_at(self, x, y, char, font, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        char_offset = (ord(char) - ord(' ')) * font.height * (int(font.width / 8) + (1 if font.width % 8 else 0))
        offset = 0

        for j in range(font.height):
            for i in range(font.width):
                if font.data[char_offset+offset] & (0x80 >> (i % 8)):
                    self.set_pixel(x + i, y + j, colored, frame_buffer)
                if i % 8 == 7:
                    offset += 1
            if font.width % 8 != 0:
                offset += 1


    def display_string_at(self, x, y, text, font, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        refcolumn = x

        # Send the string character by character on EPD
        for idx, char in enumerate(text):
            # Display one character on EPD
            self.draw_char_at(refcolumn, y, char, font, colored, frame_buffer)
            # Decrement the column position by 16
            refcolumn += font.width


    def draw_line(self, x0, y0, x1, y1, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        # Bresenham algorithm
        dx = abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while (x0 != x1) and (y0 != y1):
            self.set_pixel(x0, y0, colored, frame_buffer)
            if 2 * err >= dy:
                err += dy
                x0 += sx
            if 2 * err <= dx:
                err += dx
                y0 += sy


    def draw_horizontal_line(self, x, y, width, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        for i in range(x, x + width):
            self.set_pixel(i, y, colored, frame_buffer)


    def draw_vertical_line(self, x, y, height, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        for i in range(y, y + height):
            self.set_pixel(x, i, colored, frame_buffer)


    def draw_rectangle(self, x0, y0, x1, y1, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        self.draw_horizontal_line(min_x, min_y, max_x - min_x + 1, colored, frame_buffer)
        self.draw_horizontal_line(min_x, max_y, max_x - min_x + 1, colored, frame_buffer)
        self.draw_vertical_line(min_x, min_y, max_y - min_y + 1, colored, frame_buffer)
        self.draw_vertical_line(max_x, min_y, max_y - min_y + 1, colored, frame_buffer)


    def draw_filled_rectangle(self, x0, y0, x1, y1, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        min_x = x0 if x1 > x0 else x1
        max_x = x1 if x1 > x0 else x0
        min_y = y0 if y1 > y0 else y1
        max_y = y1 if y1 > y0 else y0
        for i in range(min_x, max_x + 1):
            self.draw_vertical_line(i, min_y, max_y - min_y + 1, colored, frame_buffer)


    def draw_circle(self, x, y, radius, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            return
        while True:
            self.set_pixel(x - x_pos, y + y_pos, colored, frame_buffer)
            self.set_pixel(x + x_pos, y + y_pos, colored, frame_buffer)
            self.set_pixel(x + x_pos, y - y_pos, colored, frame_buffer)
            self.set_pixel(x - x_pos, y - y_pos, colored, frame_buffer)
            e2 = err
            if e2 <= y_pos:
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if e2 > x_pos:
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break


    def draw_filled_circle(self, x, y, radius, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer
        # Bresenham algorithm
        x_pos = -radius
        y_pos = 0
        err = 2 - 2 * radius
        if (x >= self.width or y >= self.height):
            return
        while True:
            self.set_pixel(x - x_pos, y + y_pos, colored, frame_buffer)
            self.set_pixel(x + x_pos, y + y_pos, colored, frame_buffer)
            self.set_pixel(x + x_pos, y - y_pos, colored, frame_buffer)
            self.set_pixel(x - x_pos, y - y_pos, colored, frame_buffer)
            self.draw_horizontal_line(x + x_pos, y + y_pos, 2 * (-x_pos) + 1, colored, frame_buffer)
            self.draw_horizontal_line(x + x_pos, y - y_pos, 2 * (-x_pos) + 1, colored, frame_buffer)
            e2 = err
            if e2 <= y_pos:
                y_pos += 1
                err += y_pos * 2 + 1
                if(-x_pos == y_pos and e2 <= x_pos):
                    e2 = 0
            if e2 > x_pos:
                x_pos += 1
                err += x_pos * 2 + 1
            if x_pos > 0:
                break


    def draw_bmp(self, image_path, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        self.draw_bmp_at(0, 0, image_path, colored, frame_buffer)


    def draw_bmp_at(self, x, y, image_path, colored, frame_buffer=None):
        if frame_buffer is None:
            frame_buffer = self.frame_buffer

        if x >= self.width or y >= self.height:
            return

        try:
            with open(image_path, 'rb') as bmp_file:
                header = BitmapHeader(bmp_file.read(BitmapHeader.SIZE_IN_BYTES))
                header_info = BitmapHeaderInfo(bmp_file.read(BitmapHeaderInfo.SIZE_IN_BYTES))
                data_end = header.file_size - 2

                if header_info.width > self.width:
                    widthClipped = self.width
                elif x < 0:
                    widthClipped = header_info.width + x
                else:
                    widthClipped = header_info.width

                if header_info.height > self.height:
                    heightClipped = self.height
                elif y < 0:
                    heightClipped = header_info.height + y
                else:
                    heightClipped = header_info.height

                heightClipped = max(0, min(self.height-y, heightClipped))
                y_offset = max(0, -y)

                if heightClipped <= 0 or widthClipped <= 0:
                    return

                width_in_bytes = int(self.width/8)
                if header_info.width_in_bytes > width_in_bytes:
                    rowBytesClipped = width_in_bytes
                else:
                    rowBytesClipped = header_info.width_in_bytes

                for row in range(y_offset, heightClipped):
                    absolute_row = row + y
                    # seek to beginning of line
                    bmp_file.seek(data_end - (row + 1) * header_info.line_width)

                    line = bytearray(bmp_file.read(rowBytesClipped))
                    if header_info.last_byte_padding > 0:
                        mask = 0xFF<<header_info.last_byte_padding & 0xFF
                        line[-1] &= mask

                    for byte_index, byte in enumerate(line):
                        for i in range(8):
                            if byte & (0x80 >> i):
                                self.set_pixel(byte_index*8 + i + x, absolute_row, colored, frame_buffer)

        except OSError as e:
            print('error: {}'.format(e))
