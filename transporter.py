#!/usr/bin/env python3

from time import sleep
from enum import Enum
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor
# from ev3dev2.sound import Sound

TURN=''
ITEM=False
COLOR='red'
DRIVING_SPEED=7
TURN_SPEED=7
ROT_TIME=2.70
BLACKS=['black']
FIELDS_COLORS=["red", "green", "blue"]


class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Robot:
    def __init__(self):
        self.left_motor = LargeMotor(OUTPUT_A)
        self.right_motor = LargeMotor(OUTPUT_B)
        self.medium_motor = MediumMotor(OUTPUT_D)

        self.left_colour = ColorSensor(INPUT_2)
        self.right_colour = ColorSensor(INPUT_3)
        self.infrared = InfraredSensor(INPUT_1)


    def calibrate_sensors(self):
        print("[ROBOT] Calibration started")
        self.right_colour.calibrate_white()
        self.left_colour.calibrate_white()
        print("[ROBOT] Calibration finished")
        sleep(2)


    def get_current_colour(self, colour_sensor):
        r_param, g_param, b_param = colour_sensor.rgb
        if r_param > 150 and g_param < 50 and b_param < 50:
            return "red"
        elif r_param < 60 and g_param < 90 and b_param > 100:
            return "blue"
        elif r_param < 40 and g_param > 75 and b_param < 60:
            return "green"
        elif r_param < 60 and g_param < 60 and b_param < 60:
            return "black"
        return "white"


    def get_colours(self):
        return self.get_current_colour(self.left_colour), self.get_current_colour(self.right_colour)


    def print_colours(self, r_color, l_color):
        print("lewy kolor: {}".format(l_color))
        print("prawy kolor: {}".format(r_color))


    def print_rgb(self):
        print('left: {}'.format(self.left_colour.rgb))
        print('right: {}'.format(self.right_colour.rgb))

    def drive_forward(self):
        print("[ROBOT] Driving forward")
        self.left_motor.on(SpeedPercent(DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))

    def drive_straight_back(self):
        print("[ROBOT] Driving forward")
        self.left_motor.on(SpeedPercent(-DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(-DRIVING_SPEED))


    def turn_180(self):
        self.left_motor.on(SpeedPercent(-TURN_SPEED))
        self.right_motor.on(SpeedPercent(TURN_SPEED))
        sleep(ROT_TIME*2)
        print("OBROT O 180")


    def turn_90_right(self):
        self.left_motor.on(SpeedPercent(TURN_SPEED))
        self.right_motor.on(SpeedPercent(-TURN_SPEED))
        sleep(ROT_TIME)


    def turn_90_left(self):
        self.left_motor.on(SpeedPercent(-TURN_SPEED))
        self.right_motor.on(SpeedPercent(TURN_SPEED))
        sleep(ROT_TIME)


    def adjust_direction(self, direction=Direction.LEFT):
        while True:
            if direction == Direction.RIGHT:
                print("[ROBOT] Turning right")
                self.right_motor.on(SpeedPercent(-(TURN_SPEED-2.5)))
                self.left_motor.on(SpeedPercent(TURN_SPEED-2))
                # self.right_motor.on(SpeedPercent(-(.5)))
                # self.left_motor.on(SpeedPercent(TURN_SPEED))
            else:
                print("[ROBOT] Turning left")
                self.left_motor.on(SpeedPercent(-(TURN_SPEED-2.5)))
                self.right_motor.on(SpeedPercent(TURN_SPEED-2))
                # self.right_motor.on(SpeedPercent(TURN_SPEED))
                # self.left_motor.on(SpeedPercent(-0.5))

            left_colour, right_colour = self.get_colours()

            # print("[LEFT SENSOR] Left colour:" + left_colour)
            # print("[RIGHT SENSOR] Right colour:" + right_colour)

            if right_colour == "black" and left_colour == "black":
                print("[LEFT SENSOR] Left colour:" + left_colour)
                print("[RIGHT SENSOR] Right colour:" + right_colour)
                break

            if right_colour == "white" and left_colour == "white":
                break


    def pick_up_the_item(self):
        global ITEM
        global COLOR
        global BLACKS
        # search for the item
        while self.infrared.proximity > 30:
            self.left_motor.on(SpeedPercent(-TURN_SPEED))
            self.right_motor.on(SpeedPercent(TURN_SPEED))
            sleep(0.5)
            print("Distance: {}".format(self.infrared.proximity))

        while self.infrared.proximity >= 7:
            self.drive_forward()

        # ready to pick up item
        self.left_motor.on(SpeedPercent(0))
        self.right_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), 60)
        sleep(2)
        self.drive_straight_back()
        ITEM = True
        print("ITEM TRUE")
        sleep(1.5)
        self.turn_180()
        COLOR = "blue"
        BLACKS.append("red")


    def put_down_the_item(self):
        global ITEM
        global COLOR
        self.right_motor.on(SpeedPercent(TURN_SPEED))
        self.left_motor.on(SpeedPercent(TURN_SPEED))
        sleep(2.5)
        self.right_motor.on(SpeedPercent(0))
        self.left_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), -60)
        sleep(2)
        self.drive_straight_back()
        sleep(1.5)
        ITEM = False
        print("ITEM FALSE")
        self.turn_180()
        COLOR = "red"


    def turn_into_color_field(self, r_col, l_col, direction=Direction.LEFT):
        # 0=left
        # 1=right

        global TURN
        field_color = l_col
        turn_name = 'LEFT'
        if direction:
            field_color = r_col
            turn_name = 'RIGHT'
        self.print_colours(r_col, l_col)

        print("SKRECAM NA KOLOR {}".format(field_color))
        self.drive_forward()
        sleep(1.5)
        if turn_name=="RIGHT":
            self.turn_90_right()
        else:
            self.turn_90_left()
        TURN = turn_name


def main():
    global ITEM
    global TURN
    global COLOR
    global BLACKS
    global FIELDS_COLORS

    robot = Robot()

    robot.calibrate_sensors()

    while True:

        try:
            l_col, r_col = robot.get_colours()
            robot.print_rgb()

            if r_col in BLACKS and l_col == "white":
                # if sensors detect going off the track to the left
                robot.adjust_direction(direction=Direction.RIGHT)

            elif r_col == "white" and l_col in BLACKS:
                # if sensors detect going off the track to the right
                robot.adjust_direction(direction=Direction.LEFT)

            elif r_col in FIELDS_COLORS and l_col in FIELDS_COLORS:
                # inside field color
                print("JESTEM W POLU KOLORU")
                robot.print_colours(r_col, l_col)
                l_col, r_col = robot.get_colours()

                if not ITEM:
                    robot.pick_up_the_item()
                else:
                    robot.put_down_the_item()

                while r_col == robot.get_current_colour(robot.right_colour) and l_col == robot.get_current_colour(robot.left_colour):
                    # drive in color field until you're out of it
                    print("JADE PROSTO W POLU KOLORU")
                    robot.print_colours(r_col, l_col)
                    l_col, r_col = robot.get_colours()

                    robot.drive_forward()

                FIELDS_COLORS.remove("red")

            elif r_col in FIELDS_COLORS and l_col == "white" and TURN == "" and (COLOR == "" or r_col == COLOR):
                # turn right and drive straight forward until there is the same color on both sensors
                robot.turn_into_color_field(r_col, l_col, direction=Direction.RIGHT)

            elif l_col in FIELDS_COLORS and r_col == "white" and TURN == "" and (COLOR == "" or l_col == COLOR):
                # turn left and drive straight forward until there is the same color on both sensors
                robot.turn_into_color_field(r_col, l_col, direction=Direction.LEFT)

            elif r_col in BLACKS and l_col in BLACKS and TURN == "LEFT":
                # turn right to go back on the track after exiting color field
                print("DOUBLE BLACK I JAZDA W LEWO")
                sleep(1.5)
                robot.turn_90_left()
                TURN = ''
                BLACKS.remove("red")
                if not ITEM:
                    COLOR = ''

            elif r_col in BLACKS and l_col in BLACKS and TURN == "RIGHT":
                # turn left to go back on the track after exiting color field
                print("DOUBLE BLACK I JAZDA W PRAWO")
                sleep(1.5)
                robot.turn_90_right()
                TURN = ''
                BLACKS.remove("red")
                if not ITEM:
                    COLOR = ''

            else:
                # continue straight
                robot.print_colours(r_col, l_col)
                robot.print_rgb()
                print("JADE PROSTO")
                robot.drive_forward()

        except Exception as e:
            print(e)
            continue


if __name__ == "__main__":
    main()
