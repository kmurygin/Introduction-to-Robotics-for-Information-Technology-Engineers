#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor, TouchSensor
from time import sleep
from enum import Enum


DRIVING_SPEED = 10
TURN_SPEED = 7


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
        sleep(1)

    def get_current_colour(self, colour_sensor):
        r_param, g_param, b_param = colour_sensor.rgb
        if r_param > 150 and g_param < 50 and b_param < 50:
            return "red"
        elif r_param < 60 and g_param < 90 and b_param > 100:
            return "blue"
        elif r_param < 60 and g_param < 60 and b_param < 60:
            return "black"
        return "white"

    def get_colours(self):
        return self.get_current_colour(self.left_colour), self.get_current_colour(self.right_colour)

    def drive_forward(self):
        print("[ROBOT] Driving forward")
        self.left_motor.on(SpeedPercent(DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))

    def adjust_direction(self, direction=Direction.LEFT):
        while True:
            if direction == Direction.RIGHT:
                print("[ROBOT] Turning right")
                self.right_motor.on(SpeedPercent(-(TURN_SPEED-2.5)))
                self.left_motor.on(SpeedPercent(TURN_SPEED-2))
            else:
                print("[ROBOT] Turning left")
                self.left_motor.on(SpeedPercent(-(TURN_SPEED-2.5)))
                self.right_motor.on(SpeedPercent(TURN_SPEED-2))
            
            left_colour, right_colour = self.get_colours()

            if right_colour == "black" and left_colour == "black":
                print("[LEFT SENSOR] Left colour:" + left_colour)
                print("[RIGHT SENSOR] Right colour:" + right_colour)
                break

            if right_colour == "white" and left_colour == "white":
                break
    
    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()


def main():
    robot = Robot()
    robot.calibrate_sensors()

    while True:
        try:
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
