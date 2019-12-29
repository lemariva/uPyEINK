# uPyEINK
This project runs on the [e-Paper ESP32 Driver board](https://www.banggood.com/custlink/mKvmb95GQR) and allows you to display information (weather, news, notes) on a [Waveshare 7.5" E-INK V1 display](https://www.banggood.com/custlink/3GGmQZH3nV).

Three widgets displaying following information are available:
* Weather: weather forecast obtained using the [OpenWeatherMap api](https://openweathermap.org/api).
* News: news highlights obtained using the [NewsApi api](https://newsapi.org/).
* Notes: notes that can be added using a web-server that runs on the ESP32.

## DIY
The RAM of the ESP32-WROOM (512kb) running MicroPython is very limited. Therefore, it is not possible to load the un-compiled modules and run the code. You will get the annoying error:
```
MemoryError: memory allocation failed, allocating xxxx bytes
```
To avoid that, you should include the modules under the folder `frozen_modules` as "frozen" modules on your MicroPython firmware. If you don't know how to do that, check the sub-section "Freeze MicroPython Module" below.

### Configure the project
Rename the files:
* `boot.py.sample` to `boot.py` and include your Wi-Fi credentials:
    * ssid_ = ''
    * wpa2_pass = ''
    You need that your ESP32 connect to Wi-Fi to update the widgets.
* `settings.py.sample` to `settings.py` and set up the following variables:
    * news_api_key ([info here](https://newsapi.org/register))
    * weather_api_key ([info here](https://openweathermap.org/appid))

Upload the code to the ESP32, using e.g. [VSCode and PyMakr extension](https://lemariva.com/blog/2018/12/micropython-visual-studio-code-as-ide) and have fun!

The web-server is available under `http://<esp32-ip>` and you can add and remove notes that will be displayed on the E-INK display. 

The E-INK update frequency is set to 2 hours (`settings.update_interval` in milliseconds) and after 5 updates (`settings.calibration_interval`) the ESP32 cleans the display to avoid ghosting and reset the board to update the clock using a ntp server. If you want to, you can activate the deep sleep functionality (`settings.deep_sleep`) but you lose the web-server and you can only update the notes only when the ESP32 is updating the display.

## Compiled Libraries
There are two ways to reduce memory use on MicroPython:
* Compile the MicroPython module using the `mpy-cross` compiler, or
* Include the modules as "frozen" modules inside the MicroPython firmware.

### Compile a MicroPython Module
To compile a module you need to download the MicroPython repository.
```
git clone https://github.com/micropython/micropython.git
```
Then, go to the `mpy-cross` folder and compile the cross-compiler:
```
cd micropython/mpy-cross
make
```
Then, you can compile a MicroPython file using:
```
./my-cross foo.py
```
This generates a `.mpy` file that you can load on your ESP32 board. You need to remove the original `.py`, otherwise you import the un-compiled file every time you use `import ...`.

More info: [here](https://github.com/micropython/micropython/tree/master/mpy-cross).

If you use another MicroPython version (e.g. [MicroPython LoBo](https://github.com/loboris/MicroPython_ESP32_psRAM_LoBo)), you need to clone that repository and `make` the cross-compiler, otherwise the obtained `.mpy` file won't work on your ESP32

### Freeze MicroPython Module
To include your module in the firmware, you need to clone the MicroPython repository using:
```
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init
```
and copy the module files that you want to freeze into `micropython/ports/esp32`. This way is a bit more complicated but it makes you code [faster](https://kapusta.cc/2018/03/31/epd/). After cloning the repository, you have to compile it but first you need to set up the toolchain and the ESP-IDF:

#### Setting up the toolchain and ESP-IDF
The binary toolchain (binutils, gcc, etc.) can be installed using the following
guides:

  * [Linux installation](https://docs.espressif.com/projects/esp-idf/en/stable/get-started/linux-setup.html)
  * [MacOS installation](https://docs.espressif.com/projects/esp-idf/en/stable/get-started/macos-setup.html)
  * [Windows installation](https://docs.espressif.com/projects/esp-idf/en/stable/get-started/windows-setup.html)

Once everything is set up, you will need to update your PATH environment variable to include the ESP32 toolchain. For example, you can issue the following commands on (at least) Linux:
```
export PATH=$PATH:$HOME/esp/crosstool-NG/builds/xtensa-esp32-elf/bin
```

Then, clone the esp-idf repository under e.g. `~/esp/` using the following code:
```
cd ~/esp32/
git clone https://github.com/espressif/esp-idf.git
git checkout <current supported ESP-IDF commit hash>
git submodule update --init --recursive
```
`<current supported ESP-IDF commit hash>` this hash can be seen in the file `micropython/ports/esp32/Makefile`:

```
# the git hash of the currently supported ESP IDF version
ESPIDF_SUPHASH_V3 := 6ccb4cf5b7d1fdddb8c2492f9cbc926abaf230df
ESPIDF_SUPHASH_V4 := 310beae373446ceb9a4ad9b36b5428d7fdf2705f
```

Otherwise, you can type `make` inside the `micropython/ports/esp32/` and you get an error, if you don't have the correct ESP-IDF version. Of course, this can be done, after setting the environmental variable `$IDF_PATH` to the cloned repository e.g.:
```
export $IDF_PATH=$HOME/esp/esp-idf
```
#### Making and deploying the firmware
After those steps, you can type `make deploy` inside the folder `micropython/ports/esp32/`. The command compiles the firmware and if your board is connected to the USB (`/dev/ttyUSB0`, otherwise check the `Makefile` to change it), it uploads the firmware to the board.

You should see something like this:
```
Use make V=1 or set BUILD_VERBOSE in your environment to increase build verbosity.
Building with ESP IDF v3
MPY e7in5.py
[...]
MPY fonts/monaco16.py
[...]
MPY widgets/forecast.py
[...]
GEN build-GENERIC/frozen_content.c
[...]
Writing build-GENERIC/firmware.bin to the board
esptool.py v2.8-dev
Serial port /dev/ttyUSB0
Connecting.....
Chip is ESP32D0WDQ6 (revision 1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: cc:50:e3:a8:80:cc
Uploading stub...
Running stub...
Stub running...
Changing baud rate to 460800
Changed.
Configuring flash size...
Auto-detected Flash size: 4MB
Compressed 1336896 bytes to 816859...
Wrote 1336896 bytes (816859 compressed) at 0x00001000 in 20.9 seconds (effective 510.7 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

The modules are compiled (MPY) and added to the MicroPython firmware as frozen modules. 

If you have some problems to load the firmware/code to your ESP32 board, try erasing the flash first using:
```
esptool.py --port /dev/ttyUSB0 erase_flash
```
and then deploying the firmware again. This is needed, if you were using the ESP32 with arduino's code.

## Acknowledgement
* [A MicroPython implementation for a smaller display](https://kapusta.cc/2018/03/31/epd/)
* [Database implementation and HTML/CSS designs](https://github.com/pfalcon/notes-pico)
* [LUT and some code](https://github.com/mcauser/micropython-waveshare-epaper)
* [Some other code](https://www.waveshare.com/wiki/Libraries_Installation_for_RPi)