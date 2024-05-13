#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_D, SpeedPercent
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, InfraredSensor
from time import sleep
from enum import Enum

DRIVING_SPEED = 7
TURN_SPEED = 7
ROT_TIME=2.20
BLACKS=['Black'] #TODO, change to class field
# 8, 9

# almost working
# TURN_SPEED = 15 -> 13
# DRIVING_SPEED = 8 -> 10
# 2.5, 2

class Direction(Enum):
    LEFT = 0
    RIGHT = 1


class Robot:
    def __init__(self):
        self.left_motor = LargeMotor(OUTPUT_A)
        self.right_motor = LargeMotor(OUTPUT_B)
        self.medium_motor = LargeMotor(OUTPUT_D)

        self.left_colour = ColorSensor(INPUT_2)
        self.right_colour = ColorSensor(INPUT_1)
        self.infrared = InfraredSensor(INPUT_3)

        self.item = False
        self.color = None
        self.fields = ["Red", "Green", "Blue"]
        BLACKS=['Black']
        self.turn = ""


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
        elif r_param < 40 and g_param > 75 and b_param < 60:
            return "green"
        elif r_param < 60 and g_param < 60 and b_param < 60:
            return "black"
        return "white"


    def get_colours(self):
        return self.get_current_colour(self.left_colour), self.get_current_colour(self.right_colour)


    def drive_forward(self):
        print("[ROBOT] Driving forward")
        self.left_motor.on(SpeedPercent(DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))

    def drive_straight_back(self):
        self.motor_left.on(SpeedPercent(-DRIVING_SPEED))
        self.motor_right.on(SpeedPercent(-DRIVING_SPEED))


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
        self.left_motor.on(SpeedPercent(-DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))
        sleep(2) # changed sleep value

    def turn_right(self):
        self.left_motor.on(SpeedPercent(DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(-DRIVING_SPEED))
        sleep(1) #changed sleep value


    def turn_left(self):
        self.left_motor.on(SpeedPercent(-DRIVING_SPEED))
        self.right_motor.on(SpeedPercent(DRIVING_SPEED))
        sleep(1) #changed sleep value

    def pick_up_the_item(self):
        # global ITEM
        # global COLOR
        # global BLACKS
        # search for the item
        while self.infrared.proximity > 25: #changed value, TODO adjust to the robot crane length
            self.motor_left.on(SpeedPercent(-TURN_SPEED))
            self.motor_right.on(SpeedPercent(TURN_SPEED))
            sleep(0.5)
            print("Distance: {}".format(self.infrared.proximity))

        while self.infrared.proximity >= 5: #changed value, TODO adjust to the robot crane length
            self.dr()

        # ready to pick up item
        self.motor_left.on(SpeedPercent(0))
        self.motor_right.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), -60)
        sleep(2)
        self.drive_straight_back()
        self.item = True
        print("ITEM TRUE")
        sleep(1.5)
        self.turn_back()
        COLOR = "Blue"
        BLACKS.append("Red")


    def put_down_the_item(self):
        self.motor_right.on(SpeedPercent(DRIVING_SPEED))
        self.motor_left.on(SpeedPercent(DRIVING_SPEED))
        sleep(2.5)
        self.motor_right.on(SpeedPercent(0))
        self.motor_left.on(SpeedPercent(0))
        self.medium_motor.on_for_degrees(SpeedPercent(5), 60)
        sleep(2)
        self.drive_straight_back()
        sleep(1.5)
        self.item = False
        print("ITEM FALSE")
        self.turn_back()
        self.color = "Red"

    def turn_into_color_field(self, r_col, l_col, direction=0):
    # 0=left
    # 1=right

        field_color = l_col
        turn_name = 'LEFT'
        if direction:
            field_color = r_col
            turn_name = 'RIGHT'
        #self.print_colors(r_col, l_col)

        print("SKRECAM NA KOLOR {}".format(field_color))
        self.drive_forward()
        sleep(1.5)
        if turn_name=="RIGHT":
            self.turn_right()
        else:
            self.turn_left()
        self.turn = turn_name

    

def main():
    robot = Robot()
    robot.calibrate_sensors()

    while True:

        try:
            l_col, r_col = robot.get_colours()

            if r_col in BLACKS and l_col == "White":
                # if sensors detect going off the track to the left
                robot.adjust_direction(direction=1)

            elif r_col == "White" and l_col in BLACKS:
                # if sensors detect going off the track to the right
                robot.adjust_direction(direction=0)

            elif r_col in robot.fields and l_col in robot.fields:
                # inside field color
                print("Field colour detcted")
                robot.(r_col, l_col)
                l_col, r_col = get_colors()

                if not ITEM:
                    pick_up_the_item()
                else:
                    put_down_the_item()

                while r_col == get_color(color_right) and l_col == get_color(color_left):
                    # drive in color field until you're out of it
                    print("JADE PROSTO W POLU KOLORU")
                    print_colors(r_col, l_col)
                    l_col, r_col = get_colors()

                    drive_straight_forward()

                FIELDS_COLORS.remove("Red")

            elif r_col in FIELDS_COLORS and l_col == "White" and TURN == "" and (COLOR == "" or r_col == COLOR):
                # turn right and drive straight forward until there is the same color on both sensors
                turn_into_color_field(r_col, l_col, direction=1)

            elif l_col in FIELDS_COLORS and r_col == "White" and TURN == "" and (COLOR == "" or l_col == COLOR):
                # turn left and drive straight forward until there is the same color on both sensors
                turn_into_color_field(r_col, l_col, direction=0)

            elif r_col in BLACKS and l_col in BLACKS and TURN == "LEFT":
                # turn right to go back on the track after exiting color field
                print("DOUBLE BLACK I JAZDA W LEWO")
                sleep(1.5)
                turn_90_left()
                TURN = ''
                BLACKS.remove("Red")
                if not ITEM:
                    COLOR = ''

            elif r_col in BLACKS and l_col in BLACKS and TURN == "RIGHT":
                # turn left to go back on the track after exiting color field
                print("DOUBLE BLACK I JAZDA W PRAWO")
                sleep(1.5)
                turn_90_right()
                TURN = ''
                BLACKS.remove("Red")
                if not ITEM:
                    COLOR = ''

            else:
                # continue straight
                print_colors(r_col, l_col)
                print_rgb()
                print("JADE PROSTO")
                drive_straight_forward()

        except Exception:
            continue


if __name__ == "__main__":
    main()
