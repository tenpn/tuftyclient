from picographics import PicoGraphics, DISPLAY_TUFTY_2040

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

def show():
    display.set_pen(BG)
    display.clear()

    display.set_pen(FG_BODY)
    display.set_font("bitmap8")

    row_step = 8*ROW_SCALE + ROW_SPACING*2
    row = (int)(ROW_SPACING/2)
    row_info_height = 8*INFO_SCALE

    for i in range(3):
        display.set_pen(BG_EM)
        display.line(0, row, 320, row)

        display.set_pen(FG_BODY_BG)
        display.text("N"+str(i), 10, row+ROW_SPACING+ROW_BIAS, scale=ROW_SCALE)
        display.set_pen(FG_BODY_EM)
        display.text("Health: Rel PS5 Rel 24302", COL_TAB, row +
                    ROW_SPACING+ROW_BIAS-2, scale=INFO_SCALE)
        display.text("Deploy-Playstation", COL_TAB, row+ROW_SPACING +
                    ROW_BIAS+row_info_height, scale=INFO_SCALE)
        display.set_pen(FG_BODY)
        display.text("1:33:00", COL_TAB_2, row+ROW_SPACING +
                    ROW_BIAS+row_info_height, scale=INFO_SCALE)
        row += row_step

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
