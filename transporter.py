#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor, TouchSensor
from time import sleep
from enum import Enum
from line_follower import Robot

DRIVING_SPEED = 12
TURN_SPEED = 4

# 8, 9

# almost working
# TURN_SPEED = 15 -> 13
# DRIVING_SPEED = 8 -> 10
# 2.5, 2

class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class TransporterRobot(Robot):
    def __init__(self):
        super.__init__()
        self.is_item = False

    def turn_180(self):
        print("[ROBOT] Turning 180 degrees")
        self.left_motor.on(SpeedPercent(-DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))
        sleep(5) # to be later modified

    def turn_90_right(self):
        self.left_motor.on(SpeedPercent(DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(-DRIVING_SPEED))
        sleep(2)


    def turn_90_left(self):
        self.left_motor.on(SpeedPercent(-DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))
        sleep(2)

    def take_item(self):
        pass

    

def main():
    robot = Robot()
    robot.calibrate_sensors()

    while True:
        try:
            # if robot.touch_sensor.is_pressed:
            #     robot.stop()
            #     break
            left_colour, right_colour = robot.get_colours()
            if right_colour == "black" and left_colour == "white":
                robot.adjust_direction(Direction.RIGHT)
            elif right_colour == "white" and left_colour == "black":
                robot.adjust_direction(Direction.LEFT)
            else:
                if right_colour == "black" and left_colour == "black":
                    print("[LEFT SENSOR] Left colour:" + left_colour)
                    print("[RIGHT SENSOR] Right colour:" + right_colour)
                robot.drive_forward()

        except Exception as e:
            print("[ERROR]" + str(e))
            continue


if __name__ == "__main__":
    main()
