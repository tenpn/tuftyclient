from picographics import PicoGraphics, DISPLAY_TUFTY_2040
import math
import time

display = PicoGraphics(display=DISPLAY_TUFTY_2040)

BG = display.create_pen(0, 43, 54)
BG_EM = display.create_pen(7, 54, 66)
FG_BODY = display.create_pen(131, 148, 150)
FG_BODY_EM = display.create_pen(147, 161, 161)
FG_BODY_BG = display.create_pen(88, 110, 117)
HIGH_BLUE = display.create_pen(38, 139, 210)
HIGH_GREEN = display.create_pen(133, 153, 0)

ROW_SPACING = 10
ROW_BIAS = 2  # text rendering doesn't seem exact? compensate!
ROW_SCALE = 4
COL_TAB = 55
COL_TAB_2 = 250
INFO_SCALE = 2
MAX_BUILD_NAME_WIDTH = 255
MAX_BUILD_NAME_CHARS = 28
MAX_DESC_WIDTH = 195
MAX_DESC_CHARS = 19

SCROLL_PAUSE: float = 3
SCROLL_SPEED: float = 3 # char per second

def compute_scrolled_text(full_text: str, timer: float, max_width: int, max_chars: int) -> str:
    """scrolls this text according to the constants

    Args:
        full_text (str): text to scroll
        max_width (int): how many pixels wide can we show at once
        timer (float): duration in seconds

    Returns:
        str: scrolled string that fits in max_width
    """
    full_text_width = display.measure_text(full_text, scale=INFO_SCALE)
    if full_text_width > max_width:
        # how many chars do we need to scroll to fit in the desired width? roughly!
        chars_to_scroll = math.ceil(len(full_text) * (full_text_width-max_width)/max_width)
        scroll_duration = chars_to_scroll / SCROLL_SPEED
        total_cycle_duration = SCROLL_PAUSE*2.0 + scroll_duration*2.0
        intra_cycle_time = timer % total_cycle_duration
        # pause, forwards, pause, back
        char_pos = 0 if intra_cycle_time < SCROLL_PAUSE \
            else (((intra_cycle_time-SCROLL_PAUSE)/scroll_duration) * chars_to_scroll) if intra_cycle_time < (SCROLL_PAUSE+scroll_duration) \
            else chars_to_scroll if intra_cycle_time < (SCROLL_PAUSE+scroll_duration+SCROLL_PAUSE) \
            else ((1-((intra_cycle_time-(SCROLL_PAUSE*2+scroll_duration))/scroll_duration)) * chars_to_scroll)
        return full_text[math.floor(char_pos):(math.floor(char_pos)+max_chars)]
    else:
        return full_text

def show(jenkins_state: dict, ms_since_received: int) -> None:
    """displays state on picographics

    Args:
        jenkins_state (object): {machines:[{machine: "", is_online: True/False, build: "", changelist: 0, step: "", duration: int/seconds }]} -- if build is missing, assumes offline
    """
    display.set_pen(BG)
    display.clear()

    display.set_pen(FG_BODY)
    display.set_font("bitmap8")

    row_step = 8*ROW_SCALE + ROW_SPACING*2
    row = (int)(ROW_SPACING/2)
    row_info_height = 8*INFO_SCALE

    for machine_state in jenkins_state["machines"]:
        display.set_pen(BG_EM)
        this_row = row
        row += row_step
        display.line(0, this_row, 320, this_row)

        display.set_pen(FG_BODY if machine_state["is_online"] else FG_BODY_BG)
        display.text(machine_state["machine"], 10, this_row+ROW_SPACING+ROW_BIAS, scale=ROW_SCALE)
        
        if "build" not in machine_state:
            continue
        
        machine_elapsed_total_seconds = machine_state["duration"] + (ms_since_received/1000.0)        

        build_name_to_show = compute_scrolled_text(machine_state["build"], machine_elapsed_total_seconds, MAX_BUILD_NAME_WIDTH, MAX_BUILD_NAME_CHARS)
            
        display.set_pen(FG_BODY_EM)
        display.text(build_name_to_show, COL_TAB, this_row + ROW_SPACING+ROW_BIAS-2, scale=INFO_SCALE)
        
        desc_text = str(machine_state["changelist"]) + " " + machine_state["step"]
        print(f"-{desc_text}- on len {len(desc_text)} measured {display.measure_text(desc_text, scale=INFO_SCALE)} gives {len(desc_text) * (display.measure_text(desc_text, scale=INFO_SCALE)-MAX_DESC_WIDTH)/MAX_DESC_WIDTH}")
        desc_text = compute_scrolled_text(desc_text, machine_elapsed_total_seconds, MAX_DESC_WIDTH, MAX_DESC_CHARS)
        display.text(desc_text, COL_TAB, this_row+ROW_SPACING + ROW_BIAS+row_info_height, scale=INFO_SCALE)
        
        # build a nice elapsed string
        machine_elapsed_hours = math.floor(machine_elapsed_total_seconds/3600)
        machine_elapsed_minutes = math.floor((machine_elapsed_total_seconds - (machine_elapsed_hours*3600))/60)
        machine_elapsed_seconds = math.floor(machine_elapsed_total_seconds - (machine_elapsed_minutes*60) - (machine_elapsed_hours*3600))
        machine_elapsed_str = f"{machine_elapsed_hours}:{machine_elapsed_minutes:02}:{machine_elapsed_seconds:02}"
        display.set_pen(FG_BODY)
        display.text(machine_elapsed_str, COL_TAB_2, this_row + ROW_SPACING + ROW_BIAS+row_info_height, scale=INFO_SCALE)

    display.set_pen(HIGH_BLUE)
    display.line(0, row, 320, row)

    remaining_y = 240-row
    status_circle_radius = (int)((remaining_y - ROW_SPACING*2)/2)

    display.set_pen(HIGH_GREEN)
    row_status_circle_center = row + ROW_SPACING + status_circle_radius
    display.circle(10 + status_circle_radius,
                row_status_circle_center, status_circle_radius)
    display.text("Health: PS4 Rel 20220", 10+status_circle_radius *
                2+10, row_status_circle_center-8, scale=INFO_SCALE)

    display.update()

if __name__ == "__main__":
    # some testing data 
    data = {"machines": [
        {
            "machine": "N1",
            "is_online": True,
            "build": "Health: pp-release-pc-EU-Debug",
            "changelist": 24876,
            "step": "Editmode-Tests",
            "duration": 200
        },
        {
            "machine": "N2",
            "is_online": True,
            "build": "Deploy: pp-release-ps5-EU-Release",
            "changelist": 24876,
            "step": "Editmode-Tests HERE LONG",
            "duration": 1230
        },
        {
            "machine": "N3",
            "is_online": True,
            "build": "pp-trunk-pc-debug",
            "changelist": 24876,
            "step": "Prewarm",
            "duration": 2320
        },
    ]}
    last_show = -1
    start_time = time.ticks_ms()
    while True:
        if last_show < 0 or time.ticks_diff(time.ticks_ms(), last_show) > 250:
            show(data, time.ticks_diff(time.ticks_ms(), start_time))

