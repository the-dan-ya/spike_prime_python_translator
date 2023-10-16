#Beginning of snake_translator
'''
This is the code for the snake translator. For latest version go to:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/snake_translator.py

Documentation -> README.md:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/README.md

Change Log:
9/28/2023 Initial Version
9/30/2023 Removed async functions for better alignment with word blocks
10/2/2023 Fixed after async call sleep time. name cleanup
'''

from hub import light_matrix, port, motion_sensor, button, sound
import runloop, motor, motor_pair, color_sensor, color, distance_sensor #from lego
import time, math#from micropython
from app import sound as appsound

# change names to follow convention: velocity is deg/sec, speed is percent of full speed as in wb
default_movement_velocity = 360

degrees_per_cm = 360/17.5

class unit:
    CM = 0
    IN = 1
    DEGREES = 2
    ROTATIONS = 3
    SECONDS = 4

class direction:
    FORWARD = 101
    BACKWARD = -101

default_motor_velocities = {

}

movement_motors = []


def absolute_position_wb2py(wb_position:int):
    return ((wb_position+180) % 360) - 180

def unit_to_degrees(amount:float, in_unit:int, veclocity:int= 0):
    if in_unit == unit.CM:
        return int(amount * degrees_per_cm)
    elif in_unit == unit.ROTATIONS:
        return int(amount*360)
    elif in_unit == unit.IN:
        return int(amount*degrees_per_cm*2.54)
    elif in_unit == unit.SECONDS:
        return int(amount*(veclocity))
    else:
        return int(amount)

def degrees_to_unit(amount:float, in_unit:int, velocity:int= 0):
    if in_unit == unit.CM:
        return int(amount / degrees_per_cm)
    elif in_unit == unit.ROTATIONS:
        return int(amount/360)
    elif in_unit == unit.IN:
        return int(amount/degrees_per_cm/2.54)
    elif in_unit == unit.SECONDS:
        return int(amount/(velocity))
    else:
        return int(amount)


def get_default_velocity_for(motor_port):
    if motor_port in default_motor_velocities.keys():
        return default_motor_velocities[motor_port]
    else:
        return default_movement_velocity

# move up because needed for wait async completion
#CONTROL
def wait_seconds(amount:float):
    time.sleep_ms(int(amount*1000))

def wait_until(function):
    while not function():
        pass

#MOTORS
def run_for(motor_port:int, orientation: int, amount: float, in_unit: int):
    velocity = get_default_velocity_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        velocity = -velocity
    degrees_to_run = unit_to_degrees(amount,in_unit, velocity)
    ''' alternatively, check relative position until done
    start_position = motor.relative_position(motor_port)
    while abs(motor.relative_position(motor_port)-(start_position)) < abs(degrees_to_run):
        motor.run(motor_port, velocity)
    motor.stop(motor_port)
    '''
    motor.run_for_degrees(motor_port, degrees_to_run, velocity)
    time.sleep_ms(int(1000*(abs(degrees_to_run)/velocity)))
    wait_until(lambda:motor.velocity(motor_port) ==0)


def go_to_absolute_position(motor_port:int, orientation:int, wb_position:int):
    velocity = get_default_velocity_for(motor_port)
    target_position = absolute_position_wb2py(wb_position)
    current_position = motor.absolute_position(motor_port)
    if target_position != current_position:
        motor.run_to_absolute_position(motor_port,target_position,velocity,direction = orientation)
        degrees_to_run = 0
        if orientation == motor.CLOCKWISE:
            if target_position > current_position:
                degrees_to_run = target_position-current_position
            else:
                degrees_to_run = 360-current_position+target_position
        elif orientation == motor.COUNTERCLOCKWISE:
            if target_position < current_position:
                degrees_to_run = current_position - target_position
            else:
                degrees_to_run = 360- target_position + current_position
        elif orientation == motor.SHORTEST_PATH:
            if target_position > current_position:
                degrees_to_run = target_position-current_position
            else:
                degrees_to_run = current_position-target_position
        time.sleep_ms(int(1000*(abs(degrees_to_run)/velocity)))
        wait_until(lambda:motor.velocity(motor_port) ==0)

def start_motor(motor_port:int, orientation:int):
    velocity = get_default_velocity_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        velocity = - velocity
    motor.run(motor_port, velocity)

def stop_motor(motor_port:int):
    motor.stop(motor_port)

def set_speed_to(motor_port:int, speed_percent:int):
    default_motor_velocities[motor_port] = speed_percent*10

def absolute_position(motor_port:int):
    return motor.absolute_position(motor_port)

def motor_speed(motor_port:int):
    return abs(motor.velocity(motor_port))


#MOVEMENT
def move_for(direction_or_steer: int, amount: float, in_unit: int):
    velocity = default_movement_velocity
    move_steer = direction_or_steer
    if direction_or_steer == direction.FORWARD:
        move_steer = 0
    elif direction_or_steer == direction.BACKWARD:
        move_steer = 0
        velocity = -default_movement_velocity
    degrees_to_run= unit_to_degrees(amount, in_unit, velocity)
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees_to_run, move_steer, velocity= velocity)
    time.sleep_ms(int(abs(degrees_to_run/velocity)*1000))
    # wait until it's done and stopped. Still need sleep other wise it may not even start
    wait_until(lambda: motor.velocity(movement_motors[0])==0 and motor.velocity(movement_motors[1]) ==0 )



def start_moving(steer_value: int):
    velocity = default_movement_velocity
    start_steer = steer_value
    if steer_value == direction.FORWARD:
        start_steer = 0
    elif steer_value == direction.BACKWARD:
        start_steer = 0
        velocity = -default_movement_velocity
    motor_pair.move(motor_pair.PAIR_1, start_steer, velocity= velocity)

def stop_moving():
    motor_pair.stop(motor_pair.PAIR_1)

def set_movement_speed_to(speed_percent:int):
    global default_movement_velocity
    default_movement_velocity = speed_percent*10

def set_movement_motors_to(left_drive:int, right_drive:int):
    global movement_motors
    motor_pair.unpair(motor_pair.PAIR_1)
    motor_pair.pair(motor_pair.PAIR_1,left_drive, right_drive)
    movement_motors = [left_drive, right_drive]

def set_1_motor_rotation_to_cm(circumference:float):
    global degrees_per_cm
    degrees_per_cm=360/circumference

#LIGHT
#None for now and maybe never

#SOUND
def play_beep_for_seconds(key_number:int, duration:float, volume=75):
    #temporary translation, the frequency is not actually the keynote of word blocks
    sound.beep(int(key_number*5), int(duration*1000), volume)
    time.sleep_ms(int(duration*1000))

#EVENTS
#Please figure out on your own
#See example in Competition Ready



#Please learn basic python before coding in python

#SENSORS
def is_color(color_port:int, color_constant:int):
    return color_sensor.color(color_port) == color_constant

def get_color(color_port:int):
    return color_sensor.color(color_port)

#Use below and math :)

def relative_position(motor_port:int):
    return motor.relative_position(motor_port)

def reflection(color_port:int):
    return color_sensor.reflection(color_port)

def is_button_pressed(side:int):
    if side == button.LEFT:
        return button.pressed(button.LEFT) > 0
    else:
        return button.pressed(button.RIGHT) > 0

def start_moving_at_speed(left_speed: int, right_speed:int):
    motor_pair.move_tank(motor_pair.PAIR_1, left_speed*10, right_speed*10)

def set_yaw_angle_to(angle:int):
    motion_sensor.reset_yaw(-angle*10)

def yaw_angle():
    return -int(motion_sensor.tilt_angles()[0]/10)

def pitch_angle():
    return int(motion_sensor.tilt_angles()[1]/10)

def roll_angle():
    return int(motion_sensor.tilt_angles()[2]/10)

def set_relative_position_to(motor_port:int, relative:int):
    motor.reset_relative_position(motor_port, relative)

def go_to_relative_position_at_speed(motor_port:int, target_position:int, speed:int):
    current_position = motor.relative_position(motor_port)
    motor.run_to_relative_position(motor_port, target_position, speed*10)
    time.sleep_ms(int(abs(target_position-current_position)/(speed*10)*1000))
    wait_until(lambda: motor.velocity(motor_port)==0)

#END OF LIBRARY