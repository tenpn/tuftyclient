import time
import serialusb
from picographics import PicoGraphics, DISPLAY_TUFTY_2040

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
display.set_font("bitmap8")
BG = display.create_pen(0, 43, 54)
FG_BODY = display.create_pen(131, 148, 150)

if __name__ == "__main__":
    serial = serialusb.SerialUSB()
    while True:
        serial.update()
        while serial.is_any():
            show = serial.pop_next()
            display.set_pen(BG)
            display.clear()
            display.set_pen(FG_BODY)
            display.text("got " + show, 0, 0)
            display.update()
        time.sleep_ms(100)