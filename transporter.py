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
        """
        Sets up initial values for variables, the motors and colour sensors with proper inputs and outputs.
        """
        self.left_motor = LargeMotor(OUTPUT_A)
        self.right_motor = LargeMotor(OUTPUT_B)
        self.medium_motor = MediumMotor(OUTPUT_D)

        self.left_colour = ColorSensor(INPUT_2)
        self.right_colour = ColorSensor(INPUT_3)
        self.infrared = InfraredSensor(INPUT_1)

        self.turn = ''
        self.is_item = False
        self.next_colour = 'red'
        self.driving_speed = 8
        self.turn_speed = 7
        self.rotation_time = 3
        self.blacks = ['black']
        self.fields_colours = ["red", "green", "blue"]

    def calibrate_sensors(self):
        """
        Calibrates the colour sensors to white.
        """
        print("[ROBOT] Calibration started")
        self.right_colour.calibrate_white()
        self.left_colour.calibrate_white()
        print("[ROBOT] Calibration finished")
        sleep(2)

    def get_current_colour(self, colour_sensor):
        """
        Returns the current colour detected by given colour sensor.

        Args:
            colour_sensor (ColorSensor): The color sensor to read from.

        Returns:
            str: The color detected by the sensor.
        """
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
        """
        Returns the current colours detected by both colour sensors.

        Returns:
            tuple: The colours detected by the left and right sensors.
        """
        return self.get_current_colour(self.left_colour), self.get_current_colour(self.right_colour)

    def print_colours(self, right_colour, left_colour):
        """
        Prints the colours detected by both sensors.

        Args:
            right_colour (str): The color detected by the right sensor.
            left_colour (str): The color detected by the left sensor.
        """
        print("[LEFT SENSOR] Left colour: {}".format(left_colour))
        print("[RIGHT SENSOR] Right colour: {}".format(right_colour))

    def print_rgb(self):
        """
        Prints the RGB values detected by robot's both colour sensors.
        """
        print("[LEFT SENSOR] Left colour- rgb: {}".format(self.left_colour.rgb))
        print("[RIGHT SENSOR] Right colour- rgb: {}".format(self.right_colour.rgb))

    def drive_forward(self):
        """
        Drives the robot forward at the set driving speed.
        """
        self.left_motor.on(SpeedPercent(self.driving_speed))
        self.right_motor.on(SpeedPercent(self.driving_speed))

    def drive_straight_back(self):
        """
        Drives the robot straight backward at the set driving speed.
        """
        self.left_motor.on(SpeedPercent(-self.driving_speed))
        self.right_motor.on(SpeedPercent(-self.driving_speed))

    def turn_180(self):
        """
        Turns the robot 180 degrees.
        """
        self.left_motor.on(SpeedPercent(-self.turn_speed))
        self.right_motor.on(SpeedPercent(self.turn_speed))
        sleep(self.rotation_time * 2)

    def turn_90_right(self):
        """
        Turns the robot 90 degrees to the right.
        """
        self.left_motor.on(SpeedPercent(self.turn_speed))
        self.right_motor.on(SpeedPercent(-self.turn_speed))
        sleep(self.rotation_time)

    def turn_90_left(self):
        """
        Turns the robot 90 degrees to the left.
        """
        self.left_motor.on(SpeedPercent(-self.turn_speed))
        self.right_motor.on(SpeedPercent(self.turn_speed))
        sleep(self.rotation_time)

    def adjust_direction(self, direction=Direction.LEFT):
        """
        Adjusts the robot's direction to follow the line.

        Args:
            direction (Direction): The direction to adjust towards.
        """
        while True:
            if direction == Direction.RIGHT:
                self.right_motor.on(SpeedPercent(-(self.turn_speed - 2.5)))
                self.left_motor.on(SpeedPercent(self.turn_speed - 2))
            else:
                self.left_motor.on(SpeedPercent(-(self.turn_speed - 2.5)))
                self.right_motor.on(SpeedPercent(self.turn_speed - 2))

            left_colour, right_colour = self.get_colours()

            if right_colour == "black" and left_colour == "black":
                print("[LEFT SENSOR] Left colour:" + left_colour)
                print("[RIGHT SENSOR] Right colour:" + right_colour)
                break

            if right_colour == "white" and left_colour == "white":
                break

    def pick_up_the_item(self):
        """
        Searches for and picks up the item using the infrared sensor and medium motor.
        """
        while self.infrared.proximity > 30:
            self.left_motor.on(SpeedPercent(-self.turn_speed))
            self.right_motor.on(SpeedPercent(self.turn_speed))
            sleep(0.5)
            print("[INFRARED_SENSOR] Distance: {}".format(self.infrared.proximity))

        while self.infrared.proximity >= 2:
            self.drive_forward()
            print("[INFRARED_SENSOR] Distance: {}".format(self.infrared.proximity))

        # ready to pick up item
        self.left_motor.on(SpeedPercent(0))
        self.right_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), 60)
        sleep(2)
        self.drive_straight_back()
        self.is_item = True
        print("[ROBOT] Item has been picked up")
        sleep(1.5)
        self.turn_180()
        self.next_colour = "blue"
        self.blacks.append("red")

    def put_down_the_item(self):
        """
        Puts down the item using the medium motor.
        """
        self.right_motor.on(SpeedPercent(self.turn_speed))
        self.left_motor.on(SpeedPercent(self.turn_speed))
        sleep(.5)
        self.right_motor.on(SpeedPercent(0))
        self.left_motor.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), -60)
        sleep(2)
        self.drive_straight_back()
        sleep(1.5)
        self.is_item = False
        print("[ROBOT] Item has been put down")
        self.turn_180()
        self.next_colour = "red"

    def turn_into_color_field(self, right_colour, left_colour, direction=Direction.LEFT):
        """
        Turns the robot into the color field based on the detected colours and direction.

        Args:
            right_colour (str): The colour detected by the right sensor.
            left_colour (str): The colour detected by the left sensor.
            direction (Direction): The direction to turn towards.
        """
        field_color = left_colour
        turn_name = Direction.LEFT
        if direction == Direction.RIGHT:
            field_color = right_colour
            turn_name = Direction.RIGHT
        self.print_colours(right_colour, left_colour)
        print("[ROBOT] TURN_NAME: {}".format(turn_name))
        print("[ROBOT] Turning to colour {}".format(field_color))
        self.drive_forward()
        sleep(1.5)
        if turn_name == Direction.RIGHT:
            self.turn_90_right()
        else:
            self.turn_90_left()
        self.turn = turn_name


def main():
    """
    Main function for transporter task.
    """
    robot = Robot()
    robot.calibrate_sensors()

    while True:
        try:
            l_col, r_col = robot.get_colours()

            if r_col in robot.blacks and l_col == "white":
                # if sensors detect going off the track to the left
                robot.adjust_direction(direction=Direction.RIGHT)

            elif r_col == "white" and l_col in robot.blacks:
                # if sensors detect going off the track to the right
                robot.adjust_direction(direction=Direction.LEFT)

            elif r_col in robot.fields_colours and l_col in robot.fields_colours:
                # inside field color
                print("[ROBOT] I am in colour field")
                robot.print_colours(r_col, l_col)
                l_col, r_col = robot.get_colours()

                if not robot.is_item:
                    robot.pick_up_the_item()
                else:
                    robot.put_down_the_item()

                while r_col == robot.get_current_colour(robot.right_colour) and l_col == robot.get_current_colour(
                        robot.left_colour):
                    # drive in color field until you're out of it
                    print("[ROBOT] I am driving forward in colour field")
                    robot.print_colours(r_col, l_col)
                    l_col, r_col = robot.get_colours()

                    robot.drive_forward()

                robot.fields_colours.remove("red")

            elif r_col in robot.fields_colours and l_col == "white" and robot.turn == "" and (
                    robot.next_colour == "" or r_col == robot.next_colour):
                robot.turn_into_color_field(r_col, l_col, direction=Direction.RIGHT)

            elif l_col in robot.fields_colours and r_col == "white" and robot.turn == "" and (
                    robot.next_colour == "" or l_col == robot.next_colour):
                robot.turn_into_color_field(r_col, l_col, direction=Direction.LEFT)

            elif r_col in robot.blacks and l_col in robot.blacks and robot.turn == Direction.LEFT:
                print("[ROBOT] Double black detected, turning left")
                sleep(1.5)
                robot.turn_90_left()
                robot.turn = ''
                robot.blacks.remove("red")
                if not robot.is_item:
                    robot.next_colour = ''

            elif r_col in robot.blacks and l_col in robot.blacks and robot.turn == Direction.RIGHT:
                print("[ROBOT] Double black detected, turning right")
                sleep(1.5)
                robot.turn_90_right()
                robot.turn = ''
                robot.blacks.remove("red")
                if not robot.is_item:
                    robot.next_colour = ''

            else:
                robot.print_colours(r_col, l_col)
                robot.print_rgb()
                print("[ROBOT] Driving forward")
                robot.drive_forward()

        except Exception as e:
            print("[ERROR]" + str(e))
            continue


if __name__ == "__main__":
    main()
