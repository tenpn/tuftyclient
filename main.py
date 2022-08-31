import uselect
import time
import sys
from picographics import PicoGraphics, DISPLAY_TUFTY_2040

POLL_READ_ONLY = (
    uselect.POLLIN |
    uselect.POLLHUP |
    uselect.POLLERR
)
display = PicoGraphics(display=DISPLAY_TUFTY_2040)
display.set_font("bitmap8")
BG = display.create_pen(0, 43, 54)
FG_BODY = display.create_pen(131, 148, 150)


def read_loop():
    """_summary_ based on https://goldensyrupgames.com/blog/2022-02-04-pico-simple-two-way-serial/
    """
    serial_poll = uselect.poll()
    serial_poll.register(sys.stdin, POLL_READ_ONLY)
    latest = "-"

    while True:
        while serial_poll.poll(0):
            print("poll heard!")
            latest += str(sys.stdin.read(1))

        display.set_pen(BG)
        display.clear()
        display.set_pen(FG_BODY)
        display.text("got " + latest, 0, 0)
        display.update()

        time.sleep_ms(20)


if __name__ == "__main__":
    read_loop()