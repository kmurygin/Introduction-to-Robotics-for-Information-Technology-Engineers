#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor
from time import sleep
from enum import Enum

DRIVING_SPEED = 7
TURNING_SPEED = 7
ROT_TIME=2.20
# BLACKS=['Black'] #TODO, change to class field
# 8, 9

# almost working
# self.turning_speed = 15 -> 13
# DRIVING_SPEED = 8 -> 10
# 2.5, 2

class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Robot:
    def __init__(self, driving_speed=DRIVING_SPEED, turning_speed=TURNING_SPEED):
        self.left_motor = LargeMotor(OUTPUT_A)
        self.right_motor = LargeMotor(OUTPUT_B)
        self.medium_motor = LargeMotor(OUTPUT_D)

        self.left_colour = ColorSensor(INPUT_2)
        self.right_colour = ColorSensor(INPUT_1)
        self.infrared = InfraredSensor(INPUT_3)

        self.item: bool = False
        self.color = None
        self.field_colors = ["red", "green", "blue"]
        self.blacks = ["black"]
        self.turn = ""

        self.driving_speed = driving_speed
        self.turning_speed = turning_speed

    def calibrate_sensors(self):
        print("[ROBOT] Calibration started")
        self.right_colour.calibrate_white()
        self.left_colour.calibrate_white()
        print("[ROBOT] Calibration finished")
        sleep(1) #additional sleep to make sure everything is well calibrated

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

    def drive_forward(self):
        print("[ROBOT] Driving forward")
        self.left_motor.on(SpeedPercent(self.driving_speed))
        self.right_motor.on(SpeedPercent(self.driving_speed))

    def drive_straight_back(self):
        self.motor_left.on(SpeedPercent(-self.driving_speed))
        self.motor_right.on(SpeedPercent(-self.driving_speed))

    def adjust_direction(self, direction=Direction.LEFT):
        while True:
            if direction == Direction.RIGHT:
                print("[ROBOT] Turning right")
                self.right_motor.on(SpeedPercent(-(self.turning_speed-2.5)))
                self.left_motor.on(SpeedPercent(self.turning_speed-2))

            else:
                print("[ROBOT] Turning left")
                self.left_motor.on(SpeedPercent(-(self.turning_speed-2.5)))
                self.right_motor.on(SpeedPercent(self.turning_speed-2))
            
            left_colour, right_colour = self.get_colours()

            # print("[LEFT SENSOR] Left colour:" + left_colour)
            # print("[RIGHT SENSOR] Right colour:" + right_colour)

            if right_colour == "black" and left_colour == "black":
                print("[LEFT SENSOR] Left colour:" + left_colour)
                print("[RIGHT SENSOR] Right colour:" + right_colour)
                break

            if right_colour == "white" and left_colour == "white":
                break

    
    # def stop(self): #UNUSED, TO BE DELETED?
    #     self.left_motor.stop()
    #     self.right_motor.stop()


    def turn_back(self):
        print("[ROBOT] Turning 180 degrees")
        self.left_motor.on(SpeedPercent(-self.driving_speed))
        self.right_motor.on(SpeedPercent(self.driving_speed))
        sleep(2) # changed sleep value

    def turn_right(self):
        print("[ROBOT] Turning right")
        self.left_motor.on(SpeedPercent(self.driving_speed))
        self.right_motor.on(SpeedPercent(-self.driving_speed))
        sleep(1) #changed sleep value

    def turn_left(self):
        print("[ROBOT] Turning left")
        self.left_motor.on(SpeedPercent(-self.driving_speed))
        self.right_motor.on(SpeedPercent(self.driving_speed))
        sleep(1) #changed sleep value

    def pick_up_the_item(self):
        # global ITEM
        # global COLOR
        # global BLACKS
        # search for the item
        while self.infrared.proximity > 25: #changed value, TODO adjust to the robot crane length
            self.motor_left.on(SpeedPercent(-self.turning_speed))
            self.motor_right.on(SpeedPercent(self.turning_speed))
            sleep(0.5)
            print("[ROBOT] Distance: {}".format(self.infrared.proximity))

        while self.infrared.proximity >= 5: #changed value, TODO adjust to the robot crane length
            self.dr()

        # ready to pick up item
        self.motor_left.on(SpeedPercent(0))
        self.motor_right.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), -60)
        sleep(2)
        self.drive_straight_back()
        self.item = True
        print("[ROBOT] The item has been picked up")
        sleep(1.5)
        self.turn_back()
        self.color = "blue"
        self.blacks.append("red")

    def put_down_the_item(self):
        self.motor_right.on(SpeedPercent(self.driving_speed))
        self.motor_left.on(SpeedPercent(self.driving_speed))
        sleep(2.5)
        self.motor_right.on(SpeedPercent(0))
        self.motor_left.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), 60)
        sleep(2)
        self.drive_straight_back()
        sleep(1.5)
        self.item = False
        print("[ROBOT] The item has been put down")
        self.turn_back()
        self.color = "red"

    def turn_into_color_field(self, r_col, l_col, direction=0):
    # 0=left
    # 1=right

        field_color = l_col
        turn_name = 'LEFT'
        if direction:
            field_color = r_col
            turn_name = 'RIGHT'
        #self.print_colors(r_col, l_col)

        print("[ROBOT] Turning for color: {}".format(field_color))
        self.drive_forward()
        sleep(1.5)
        if turn_name=="RIGHT":
            self.turn_right()
        else:
            self.turn_left()
        self.turn = turn_name

    def run(self):
        while True:
            try:
                l_col, r_col = self.get_colours()

                if r_col in self.blacks and l_col == "white":
                    # if sensors detect going off the track to the left
                    self.adjust_direction(direction=1)

                elif r_col == "white" and l_col in self.blacks:
                    # if sensors detect going off the track to the right
                    self.adjust_direction(direction=0)

                elif r_col in self.fields and l_col in self.fields:
                    # inside field color
                    print("[ROBOT] Field colour detcted")
                    self.print_colors(r_col, l_col)
                    l_col, r_col = self.get_colors()

                    if not self.item:
                        self.pick_up_the_item()
                    else:
                        self.put_down_the_item()

                    while r_col == self.get_color(self.color_right) and l_col == self.get_color(self.color_left):
                        # drive in color field until you're out of it
                        print("[ROBOT] Driving forward in color field")
                        self.print_colors(r_col, l_col)
                        l_col, r_col = self.get_colors()

                        self.drive_straight_forward()

                    self.field_colors.remove("red")

                elif r_col in self.field_colors and l_col == "white" and TURN == "" and (COLOR == "" or r_col == COLOR):
                    # turn right and drive straight forward until there is the same color on both sensors
                    self.turn_into_color_field(r_col, l_col, direction=Direction.RIGHT)

                elif l_col in self.field_colors and r_col == "white" and TURN == "" and (COLOR == "" or l_col == COLOR):
                    # turn left and drive straight forward until there is the same color on both sensors
                    self.turn_into_color_field(r_col, l_col, direction=Direction.LEFT)

                elif r_col in self.blacks and l_col in self.blacks and TURN == "LEFT":
                    # turn right to go back on the track after exiting color field
                    print("[ROBOT] Turning left- double black detected")
                    sleep(1.5)
                    self.turn_90_left()
                    TURN = ''
                    self.blacks.remove("red")
                    if not self.item:
                        COLOR = ''

                elif r_col in self.blacks and l_col in self.blacks and TURN == "RIGHT":
                    # turn left to go back on the track after exiting color field
                    print("[ROBOT] Turning right- double black detected")
                    sleep(1.5)
                    self.turn_90_right()
                    TURN = ''
                    self.blacks.remove("red")
                    if not self.item:
                        COLOR = ''

                else:
                    # continue straight
                    self.print_colors(r_col, l_col)
                    self.print_rgb()
                    print("[ROBOT] Driving forward")
                    self.drive_straight_forward()

            except Exception:
                continue

def main():
    robot = Robot()
    robot.calibrate_sensors()
    robot.run()

if __name__ == "__main__":
    main()
