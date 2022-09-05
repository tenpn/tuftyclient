from picographics import PicoGraphics, DISPLAY_TUFTY_2040
import math

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
        
        display.set_pen(FG_BODY_EM)
        display.text(machine_state["build"] + " " + str(machine_state["changelist"]), COL_TAB, this_row +
                    ROW_SPACING+ROW_BIAS-2, scale=INFO_SCALE)
        display.text(machine_state["step"], COL_TAB, this_row+ROW_SPACING +
                    ROW_BIAS+row_info_height, scale=INFO_SCALE)
        
        # build a nice elapsed string
        machine_elapsed_total_seconds = machine_state["duration"] + (ms_since_received/1000)
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
            "build": "Health: pp-trunk-pc-EU-Debug",
            "changelist": 24876,
            "step": "Editmode-Tests",
            "duration": 200
        },
        {
            "machine": "N2",
            "is_online": True,
        },
        {
            "machine": "N3",
            "is_online": False,
        },
    ]}
    show(data, 0)
