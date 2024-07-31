#START SNAKE_TRANSLATOR
'''
This is the code for the snake translator. For latest version go to:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/snake_translator.py

Documentation -> README.md:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/README.md

Change Log:
9/28/2023 Initial Version
9/30/2023 Removed async functions for better alignment with word blocks
10/2/2023 Fixed after async call sleep time. name cleanup
10/29/2023 clean up with missions
1/4/2024 Clean up naming conventions and functions
7/27/2024 Fixed wb2py bug
'''

from hub import light, light_matrix, port, motion_sensor, button, sound
import runloop, motor, motor_pair, color_sensor, color, distance_sensor, force_sensor #from lego
import time, math#from micropython
from app import sound as appsound
from app import music as appmusic

# change names to follow convention: velocity is deg/sec, speed is percent of full speed as in wb
default_movement_speed = 30

degrees_per_cm = 360/27.57

class unit:
    CM = 0
    IN = 1
    DEGREES = 2
    ROTATIONS = 3
    SECONDS = 4

class direction:
    FORWARD = 101
    BACKWARD = -101

class size:
    LARGE = 0
    MEDIUM = 1
    SMALL = 2# large 1050 medium 1110 small 660

default_motor_speeds = {
}

max_velocity = 1110 # large 1050 medium 1110 small 660

movement_motors = []

#WB is 0 to 360, PY is -180 to 180
def _absolute_position_wb2py(wb_position:int):
    if wb_position > 180:
        return wb_position-360
    else:
        return wb_position

    #return ((wb_position+180) % 360) - 180 #mod version

def unit_to_degrees(amount:float, in_unit:int, in_velocity:int= 0):
    if in_unit == unit.CM:
        return int(amount * degrees_per_cm)
    elif in_unit == unit.ROTATIONS:
        return int(amount*360)
    elif in_unit == unit.IN:
        return int(amount*degrees_per_cm*2.54)
    elif in_unit == unit.SECONDS:
        return int(amount*(in_velocity))
    else:
        return int(amount)

def degrees_to_unit(amount:float, in_unit:int, in_velocity:int= 0):
    if in_unit == unit.CM:
        return int(amount / degrees_per_cm)
    elif in_unit == unit.ROTATIONS:
        return int(amount/360)
    elif in_unit == unit.IN:
        return int(amount/degrees_per_cm/2.54)
    elif in_unit == unit.SECONDS:
        return int(amount/(in_velocity))
    else:
        return int(amount)

def get_default_speed_for(motor_port):
    if motor_port in default_motor_speeds.keys():
        return default_motor_speeds[motor_port]
    else:
        return default_movement_speed

# move up because needed for wait async completion
#CONTROL
def wait_seconds(amount:float):
    time.sleep_ms(int(amount*1000))

def wait_until(function):
    while not function():
        pass

#MOTORS
def get_motor_speed(motor_port,speed=0):
    if speed != 0:
        in_speed = speed
    else:
        in_speed = get_default_speed_for(motor_port)
    return in_speed

def run_for(motor_port:int, orientation: int, amount: float, in_unit: int, speed = 0, wait = True):
    in_speed=get_motor_speed(motor_port,speed)
    if orientation == motor.COUNTERCLOCKWISE:
        in_speed = -in_speed
    velocity = int(in_speed/100*max_velocity)
    degrees_to_run = abs(unit_to_degrees(amount,in_unit, velocity))
    motor.run_for_degrees(motor_port, degrees_to_run, velocity)
    if wait:
        time.sleep_ms(int(1000*abs(degrees_to_run/velocity)))
        wait_until(lambda:motor.velocity(motor_port) ==0)

def go_to_absolute_position(motor_port:int, orientation:int, wb_position:int,speed:int = 0,wait = True):
    in_speed=get_motor_speed(motor_port,speed)
    target_position_py = _absolute_position_wb2py(wb_position)
    motor.run_to_absolute_position(motor_port,target_position_py,int(in_speed/100*max_velocity),direction = orientation)
    if wait:
        time.sleep_ms(200)
        wait_until(lambda:motor.velocity(motor_port) ==0)

def start_motor(motor_port:int, orientation:int,speed=0):
    in_speed=get_motor_speed(motor_port,speed)
    if orientation == motor.COUNTERCLOCKWISE:
        in_speed = -in_speed
    motor.run(motor_port, int(in_speed/100*max_velocity))

def stop_motor(motor_port:int):
    motor.stop(motor_port)

def absolute_position(motor_port:int):
    py_position = motor.absolute_position(motor_port)
    if py_position < 0: return py_position+360
    else: return py_position

#python api bug means it doesn't have to be converted :)
def motor_speed(motor_port:int):
    return abs(motor.velocity(motor_port))

#MOVEMENT
def get_movement_speed(speed):
    if speed != 0:
        in_speed = speed
    else:
        in_speed = default_movement_speed
    return in_speed

def get_steering_movement_speed(direction_or_steer,speed):
    in_speed=get_movement_speed(speed)

    if direction_or_steer == direction.FORWARD:
        move_steer = 0
    elif direction_or_steer == direction.BACKWARD:
        move_steer = 0
        in_speed = -in_speed
    else:
        move_steer=direction_or_steer
    return (move_steer, in_speed)

def move_for(direction_or_steer: int, amount: float, in_unit: int, speed = 0, wait = True):
    steer_speed = get_steering_movement_speed(direction_or_steer,speed)
    velocity = int(steer_speed[1]/100*max_velocity)
    degrees_to_run= abs(unit_to_degrees(amount, in_unit, velocity))
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees_to_run, steer_speed[0], velocity= velocity)
    if wait:
        time.sleep_ms(int(abs(degrees_to_run/velocity)*1000))
    # wait until it's done and stopped. Still need sleep other wise it may not even start
        wait_until(lambda: motor_speed(movement_motors[0])==0 and motor_speed(movement_motors[1]) ==0 )

def start_moving(direction_or_steer: int, speed = 0):
    steer_speed = get_steering_movement_speed(direction_or_steer,speed)
    velocity = int(steer_speed[1]/100*max_velocity)
    motor_pair.move(motor_pair.PAIR_1, steer_speed[0], velocity= velocity)

def start_moving_at_speed(left_speed: float, right_speed:float):
    motor_pair.move_tank(motor_pair.PAIR_1, int(left_speed/100*max_velocity), int(right_speed/100*max_velocity))

def stop_moving():
    motor_pair.stop(motor_pair.PAIR_1)

def set_movement_speed_to(speed_percent:int):
    global default_movement_speed
    default_movement_speed = speed_percent

def set_movement_motors_to(left_drive:int, right_drive:int):
    global movement_motors
    motor_pair.unpair(motor_pair.PAIR_1)
    motor_pair.pair(motor_pair.PAIR_1,left_drive, right_drive)
    movement_motors = [left_drive, right_drive]

def set_1_motor_rotation_to_cm(circumference:float):
    global degrees_per_cm
    degrees_per_cm=360.0/circumference

def set_movement_motor_size(motor_size: int):
    global max_velocity
    if motor_size == size.LARGE:
        max_velocity = 1050
    elif motor_size == size.SMALL:
        max_velocity = 660
    else:
        max_velocity = 1110

def set_wheel_size(wheel_size: int):
    if wheel_size == size.LARGE:
        set_1_motor_rotation_to_cm(27.57)
    else:
        set_1_motor_rotation_to_cm(17.5)

#LIGHT
#None for now and future!

#SOUND
def play_beep_for_seconds(key_number:int, duration:float, volume=75):
    #temporary translation, the frequency is not actually the keynote of word blocks
    sound.beep(int(key_number*5), int(duration*1000), volume)

#EVENTS
#See example in Competition Ready
#Please figure out on your own and learn basic python before coding in python

#SENSORS
def is_color(color_port:int, color_constant:int):
    return color_sensor.color(color_port) == color_constant

def get_color(color_port:int):
    return color_sensor.color(color_port)

def distance_cm(sensor_port):
    return distance_sensor.distance(sensor_port)/10.0

#Use below and math :)

def relative_position(motor_port:int):
    return motor.relative_position(motor_port)

def reflection(color_port:int):
    return color_sensor.reflection(color_port)

def is_button_pressed(side:int=0):
    if side == button.LEFT:
        return button.pressed(button.LEFT) > 0
    elif side == button.RIGHT:
        return button.pressed(button.RIGHT) > 0
    else:
        return button.pressed(button.LEFT) > 0 or button.pressed(button.RIGHT) >0

def is_double_tapped():
    return motion_sensor.gesture() == motion_sensor.DOUBLE_TAPPED

def is_tapped():
    return motion_sensor.gesture() == motion_sensor.TAPPED

def set_yaw_angle_to(angle:float):
    motion_sensor.reset_yaw(-int(angle*10))
    wait_seconds(0.1) #the gyro sensor needs some time to update itself and gain conscience

def yaw_angle():
    return -(motion_sensor.tilt_angles()[0]/10)

def pitch_angle():
    return (motion_sensor.tilt_angles()[1]/10)

def roll_angle():
    return (motion_sensor.tilt_angles()[2]/10)

def set_relative_position_to(motor_port:int, relative:int):
    motor.reset_relative_position(motor_port, relative)

#END SNAKE_TRANSLATOR
