#!/usr/bin/env python3

from time import sleep
from enum import Enum
from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor


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

        self.turn = ''
        self.item = False
        self.colour = 'Red'
        self.driving_speed = 8
        self.turn_speed = 7
        self.rot_time = 3
        self.blacks = ['Black']
        self.fields_colours = ["Red", "Green", "Blue"]

    def calibrate_sensors(self):
        print("[ROBOT] Calibration started")
        self.right_colour.calibrate_white()
        self.left_colour.calibrate_white()
        print("[ROBOT] Calibration finished")
        sleep(2)

    def get_current_colour(self, colour_sensor):
        r_param, g_param, b_param = colour_sensor.rgb
        if r_param > 150 and g_param < 50 and b_param < 50:
            return "Red"
        elif r_param < 60 and g_param < 90 and b_param > 100:
            return "Blue"
        elif r_param < 40 and g_param > 75 and b_param < 60:
            return "Green"
        elif r_param < 60 and g_param < 60 and b_param < 60:
            return "Black"
        return "White"


    def get_colours(self):
        return self.get_current_colour(self.left_colour), self.get_current_colour(self.right_colour)


    def print_colours(self, r_color, l_color):
        print("lewy kolor: {}".format(l_color))
        print("prawy kolor: {}".format(r_color))


    def print_rgb(self):
        print('left: {}'.format(self.left_colour.rgb))
        print('right: {}'.format(self.right_colour.rgb))

    def drive_forward(self):
        self.left_motor.on(SpeedPercent(self.driving_speed))
        self.right_motor.on(SpeedPercent(self.driving_speed))

    def drive_straight_back(self):
        self.left_motor.on(SpeedPercent(-self.driving_speed))
        self.right_motor.on(SpeedPercent(-self.driving_speed))

    def turn_180(self):
        self.left_motor.on(SpeedPercent(-self.turn_speed))
        self.right_motor.on(SpeedPercent(self.turn_speed))
        sleep(self.rot_time*2)

    def turn_90_right(self):
        self.left_motor.on(SpeedPercent(self.turn_speed))
        self.right_motor.on(SpeedPercent(-self.turn_speed))
        sleep(self.rot_time)

    def turn_90_left(self):
        self.left_motor.on(SpeedPercent(-self.turn_speed))
        self.right_motor.on(SpeedPercent(self.turn_speed))
        sleep(self.rot_time)

    def adjust_direction(self, direction=Direction.LEFT):
        while True:
            if direction == Direction.RIGHT:
                self.right_motor.on(SpeedPercent(-(self.turn_speed-2.5)))
                self.left_motor.on(SpeedPercent(self.turn_speed-2))
            else:
                self.left_motor.on(SpeedPercent(-(self.turn_speed-2.5)))
                self.right_motor.on(SpeedPercent(self.turn_speed-2))

            left_colour, right_colour = self.get_colours()

            # print("[LEFT SENSOR] Left colour:" + left_colour)
            # print("[RIGHT SENSOR] Right colour:" + right_colour)

            if right_colour == "Black" and left_colour == "Black":
                print("[LEFT SENSOR] Left colour:" + left_colour)
                print("[RIGHT SENSOR] Right colour:" + right_colour)
                break

            if right_colour == "White" and left_colour == "White":
                break

    def pick_up_the_item(self):
        # search for the item
        while self.infrared.proximity > 30:
            self.left_motor.on(SpeedPercent(-self.turn_speed))
            self.right_motor.on(SpeedPercent(self.turn_speed))
            sleep(0.5)
            print("Distance: {}".format(self.infrared.proximity))

        while self.infrared.proximity >= 2:
            self.drive_forward()
            print("Distance: {}".format(self.infrared.proximity))

        # ready to pick up item
        self.left_motor.on(SpeedPercent(0))
        self.right_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), 60)
        sleep(2)
        self.drive_straight_back()
        self.item = True
        print("ITEM TRUE")
        sleep(1.5)
        self.turn_180()
        self.colour = "Blue"
        self.blacks.append("Red")


    def put_down_the_item(self):
        self.right_motor.on(SpeedPercent(self.turn_speed))
        self.left_motor.on(SpeedPercent(self.turn_speed))
        sleep(.5)
        self.right_motor.on(SpeedPercent(0))
        self.left_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), -60)
        sleep(2)
        self.drive_straight_back()
        sleep(1.5)
        self.item = False
        print("ITEM FALSE")
        self.turn_180()
        self.colour = "Red"


    def turn_into_color_field(self, r_col, l_col, direction=Direction.LEFT):
        field_color = l_col
        turn_name = 'LEFT'
        if direction == Direction.RIGHT:
            field_color = r_col
            turn_name = 'RIGHT'
        self.print_colours(r_col, l_col)
        print("TURN_NAME: {}".format(turn_name))
        print("SKRECAM NA KOLOR {}".format(field_color))
        self.drive_forward()
        sleep(1.5)
        if turn_name=="RIGHT":
            self.turn_90_right()
        else:
            self.turn_90_left()
        self.turn = turn_name

def main():
    robot = Robot()

    robot.calibrate_sensors()

    while True:
            try:
                l_col, r_col = robot.get_colours()
                # robot.print_rgb()
                print("WCHODZE TUTAJ 1: {}".format(r_col in robot.fields_colours and l_col == "White" and robot.turn == "" and (robot.colour == "" or r_col == robot.colour)))
                print("WCHODZE TUTAJ 2: {}".format(l_col in robot.fields_colours and r_col == "White" and robot.turn == "" and (robot.colour == "" or l_col == robot.colour)))

                if r_col in robot.blacks and l_col == "White":
                    # if sensors detect going off the track to the left
                    robot.adjust_direction(direction=Direction.RIGHT)

                elif r_col == "White" and l_col in robot.blacks:
                    # if sensors detect going off the track to the right
                    robot.adjust_direction(direction=Direction.LEFT)

                elif r_col in robot.fields_colours and l_col in robot.fields_colours:
                    # inside field color
                    print("JESTEM W POLU KOLORU")
                    robot.print_colours(r_col, l_col)
                    l_col, r_col = robot.get_colours()

                    if not robot.item:
                        robot.pick_up_the_item()
                    else:
                        robot.put_down_the_item()

                    while r_col == robot.get_current_colour(robot.right_colour) and l_col == robot.get_current_colour(robot.left_colour):
                        # drive in color field until you're out of it
                        print("JADE PROSTO W POLU KOLORU")
                        robot.print_colours(r_col, l_col)
                        l_col, r_col = robot.get_colours()

                        robot.drive_forward()

                    robot.fields_colours.remove("Red")

                elif r_col in robot.fields_colours and l_col == "White" and robot.turn == "" and (robot.colour == "" or r_col == robot.colour):
                    # turn right and drive straight forward until there is the same color on both sensors
                    print("WCHODZE TUTAJ 1: {}".format(r_col in robot.fields_colours and l_col == "White" and robot.turn == "" and (robot.colour == "" or r_col == robot.colour)))
                    robot.turn_into_color_field(r_col, l_col, direction=Direction.RIGHT)

                elif l_col in robot.fields_colours and r_col == "White" and robot.turn == "" and (robot.colour == "" or l_col == robot.colour):
                    # turn left and drive straight forward until there is the same color on both sensors
                    print("WCHODZE TUTAJ 2: {}".format(l_col in robot.fields_colours and r_col == "White" and robot.turn == "" and (robot.colour == "" or l_col == robot.colour)))
                    robot.turn_into_color_field(r_col, l_col, direction=Direction.LEFT)

                elif r_col in robot.blacks and l_col in robot.blacks and robot.turn == "LEFT":
                    # turn right to go back on the track after exiting color field
                    print("DOUBLE BLACK I JAZDA W LEWO")
                    sleep(1.5)
                    robot.turn_90_left()
                    robot.turn = ''
                    robot.blacks.remove("Red")
                    if not robot.item:
                        robot.colour = ''

                elif r_col in robot.blacks and l_col in robot.blacks and robot.turn == "RIGHT":
                    # turn left to go back on the track after exiting color field
                    print("DOUBLE BLACK I JAZDA W PRAWO")
                    sleep(1.5)
                    robot.turn_90_right()
                    robot.turn = ''
                    robot.blacks.remove("Red")
                    if not robot.item:
                        robot.colour = ''

                else:
                    robot.print_colours(r_col, l_col)
                    robot.print_rgb()
                    print("JADE PROSTO")
                    robot.drive_forward()

            except Exception:
                continue


if __name__ == "__main__":
    main()
