import time
import serialusb
import jenkinsdisplay
import json

if __name__ == "__main__":
    serial = serialusb.SerialUSB()
    show = None
    last_show_time = None
    received_time = 0
    while True:
        serial.update()
        while serial.is_any():
            show = json.loads(serial.pop_next())
            last_show_time = None            
            received_time = time.ticks_ms()
            
        if show is None:
            jenkinsdisplay.display.set_pen(jenkinsdisplay.BG)
            jenkinsdisplay.display.clear()
            jenkinsdisplay.display.set_pen(jenkinsdisplay.FG_BODY)
            jenkinsdisplay.display.text("len " + str(serial.pending_len()), 0, 100)
            jenkinsdisplay.display.update()
            
        elif last_show_time is None or time.ticks_diff(time.ticks_ms(), last_show_time) > 333:
            ms_since_received = time.ticks_diff(time.ticks_ms(), received_time)
            jenkinsdisplay.show(show, ms_since_received)
            last_show_time = time.ticks_ms()
            
        time.sleep_ms(100)
