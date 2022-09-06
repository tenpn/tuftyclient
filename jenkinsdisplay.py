from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB565
import math
import time

display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB565)

# solarized colours
BG = display.create_pen(0, 43, 54) # base03
BG_EM = display.create_pen(7, 54, 66) # base02
FG_BODY = display.create_pen(131, 148, 150) # base0
FG_BODY_EM = display.create_pen(147, 161, 161) # base1
FG_BODY_BG = display.create_pen(88, 110, 117) # base01

HIGH_RED = display.create_pen(220, 50, 47)
HIGH_YELLOW = display.create_pen(181, 137, 0)
HIGH_GREEN = display.create_pen(133, 153, 0)

HIGH_BLUE = display.create_pen(38, 139, 210)
HIGH_CYAN = display.create_pen(42, 161, 152)
HIGH_MAGENTA = display.create_pen(211, 54, 130)
HIGH_ORANGE = display.create_pen(203, 75, 22)
HIGH_VIOLET = display.create_pen(108, 113, 196)

ROW_SPACING = 10
ROW_BIAS = 2  # text rendering doesn't seem exact? compensate!
ROW_SCALE = 4
COL_TAB = 55
COL_TAB_2 = 250
INFO_SCALE = 2
ROW_INFO_HEIGHT = 8*INFO_SCALE
MAX_BUILD_NAME_WIDTH = 255
MAX_DESC_WIDTH = 190

SCROLL_PAUSE: float = 3
SCROLL_DURATION: float = 3

def draw_prefixed_scrolled_text(prefix: str, text: str, timer: float, left_x: int, max_width: int, y: int, prefix_col, text_col) -> None:
    """draws a prefix, then the main string in a scrolling window

    Args:
        prefix (str): doesn't scroll
        text (str): main text. could scroll if doesn't fit in remaining space
        timer (float): some seconds-based timer, to do scrolling off
        left_x (int): left edge of the window we're drawing in 
        max_width (int): width of window we're drawing in 
        y (int): top row of the window we're drawing in
    """
    if len(prefix) > 0:
        display.set_pen(prefix_col)
        display.text(prefix, left_x, y, scale=INFO_SCALE)
        prefix_width = display.measure_text(prefix, scale=INFO_SCALE) + 4
        left_x += prefix_width
        max_width -= prefix_width

    display.set_pen(text_col)
    draw_scrolled_text(text, timer, y, left_x, max_width)

def draw_scrolled_text(text: str, timer: float, y: int, left_x: int, max_width: int) -> None:
    """draw some text, scrolling it to keep it fitted in the window. uses ROW_INFO_HEIGHT as implicit window height.

    Args:
        timer (float): some seconds-based timer, to do scrolling off
        y (int): top row of the window we're drawning in
        left_x (int): left edge of window we're drawing in 
        max_width (int): width of window we're drawing in
    """
    
    full_text_width = display.measure_text(text, scale=INFO_SCALE)
    
    if full_text_width <= max_width:
        display.text(text, left_x, y, scale=INFO_SCALE)
        return
    
    px_to_scroll = full_text_width - max_width
    total_cycle_duration = SCROLL_PAUSE*2.0 + SCROLL_DURATION*2.0
    intra_cycle_time = timer % total_cycle_duration
    
    scroll_t = 0 if intra_cycle_time < SCROLL_PAUSE \
        else ((intra_cycle_time-SCROLL_PAUSE)/SCROLL_DURATION) if intra_cycle_time < (SCROLL_PAUSE+SCROLL_DURATION) \
        else 1 if intra_cycle_time < (SCROLL_PAUSE+SCROLL_DURATION+SCROLL_PAUSE) \
        else (1-((intra_cycle_time-(SCROLL_PAUSE*2+SCROLL_DURATION))/SCROLL_DURATION))
        
    display.set_clip(left_x, y, max_width, ROW_INFO_HEIGHT)
    display.text(text, left_x - int(scroll_t*px_to_scroll), y, scale=INFO_SCALE)
    display.remove_clip()
    
def get_time_breakdown(total_secs: float):
    """takes seconds, splits into hours/mins/secs

    Args:
        total_secs (int): 

    Returns:
        (int, int, int): (hours, minutes, seconds)
    """
    complete_hours = int(math.floor(total_secs/3600.0))
    complete_minutes = int(math.floor((total_secs - (complete_hours*3600))/60.0))
    remaining_seconds = int(math.floor(total_secs - (complete_minutes*60) - (complete_hours*3600)))
    return (complete_hours, complete_minutes, remaining_seconds)

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

    for machine_state in jenkins_state["machines"]:
        display.set_pen(BG_EM)
        this_row = row
        row += row_step
        display.line(0, this_row, 320, this_row)

        display.set_pen(FG_BODY if machine_state["is_online"] else FG_BODY_BG)
        display.text(machine_state["machine"], 10, this_row+ROW_SPACING+ROW_BIAS, scale=ROW_SCALE)
        
        if "build" not in machine_state:
            continue
        
        scroll_timer = ms_since_received/1000.0
        
        # "Health:" and "Deploy:" prefixes don't scroll
        build_prefix = ""
        build_name = machine_state["build"]
        build_delim_index = build_name.find(":")
        if build_delim_index >= 0:
            build_prefix = build_name[:build_delim_index+1]
            build_name = build_name[build_delim_index+1:].strip()
            
        build_prefix_col = HIGH_VIOLET if "Health" in build_prefix \
            else HIGH_CYAN if "Deploy" in build_prefix \
            else FG_BODY_BG
        draw_prefixed_scrolled_text(build_prefix, 
                                    build_name, 
                                    scroll_timer, 
                                    COL_TAB,
                                    MAX_BUILD_NAME_WIDTH, 
                                    this_row + ROW_SPACING+ROW_BIAS-2, 
                                    build_prefix_col, 
                                    HIGH_BLUE)
        
        # changelists don't scroll
        desc_prefix = str(machine_state["changelist"]) if "changelist" in machine_state else ""
        desc_text = machine_state["step"]
        
        draw_prefixed_scrolled_text(desc_prefix, 
                                    desc_text, 
                                    scroll_timer, 
                                    COL_TAB, 
                                    MAX_DESC_WIDTH, 
                                    this_row+ROW_SPACING + ROW_BIAS+ROW_INFO_HEIGHT, 
                                    FG_BODY_BG, 
                                    FG_BODY)
        
        # build a nice elapsed string
        (machine_elapsed_hours, machine_elapsed_minutes, machine_elapsed_seconds) = \
            get_time_breakdown(machine_state["duration"] + (ms_since_received/1000))
        machine_elapsed_str = f"{machine_elapsed_hours}:{machine_elapsed_minutes:02}:{machine_elapsed_seconds:02}"
        display.set_pen(FG_BODY_BG)
        display.text(machine_elapsed_str, COL_TAB_2, this_row + ROW_SPACING + ROW_BIAS+ROW_INFO_HEIGHT, scale=INFO_SCALE)

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

    (data_age_hours, data_age_mins, data_age_secs) = get_time_breakdown(ms_since_received/1000)
    data_age_str = "rx " + \
        (f"{data_age_hours}:{data_age_mins:02}:{data_age_secs:02}" if data_age_hours > 0 else f"{data_age_mins}:{data_age_secs:02}")
    data_age_width = display.measure_text(data_age_str, scale=1)
    display.set_pen(FG_BODY_BG if ms_since_received < 900000 else FG_BODY_EM)
    display.text(data_age_str, 305-data_age_width, 225, scale=1)
    
    display.update()

if __name__ == "__main__":
    # some testing data 
    data = {"machines": [
        {
            "machine": "N1",
            "is_online": True,
            "build": "Health: release-pc-EU-Debug",
            "changelist": 24876,
            "step": "Editmode-Tests",
            "duration": 200
        },
        {
            "machine": "N2",
            "is_online": True,
            "build": "Deploy: release-ps5-EU-Release",
            "changelist": 24876,
            "step": "Editmode-Tests HERE LONG",
            "duration": 1230
        },
        {
            "machine": "N3",
            "is_online": True,
            "build": "trunk-pc-debug",
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

