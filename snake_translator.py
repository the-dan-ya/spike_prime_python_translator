#Beginning of snake_translator
'''
This is the code for the snake translator. For latest version go to:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/snake_translator.py

Documentation -> README.md:
https://github.com/the-dan-ya/spike_prime_python_translator/blob/main/README.md

Change Log: 
9/28/2023 Initial Version
'''
from hub import light_matrix, port, motion_sensor, button, sound
import runloop, motor, motor_pair, color_sensor, color
from app import sound as appsound

default_movement_speed = 360

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

default_motor_speeds = {
    
}

def unit_to_degrees(amount:float, in_unit:int):
    if in_unit == unit.CM:
        return int(amount * degrees_per_cm)
    elif in_unit == unit.ROTATIONS:
        return int(amount*360)
    elif in_unit == unit.IN:
        return int(amount*degrees_per_cm*2.54)
    else:
        return int(amount)

def get_default_speed_for(motor_port):
    if motor_port in default_motor_speeds.keys():
        return default_motor_speeds[motor_port]
    else:
        return default_movement_speed

#MOTORS
async def run_for(motor_port:int, orientation: int, amount: float, in_unit: int):
    motor_speed = get_default_speed_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        motor_speed = -motor_speed
    if in_unit == unit.SECONDS:
        await motor.run_for_time(motor_port, int(amount*1000), motor_speed)
    else:
        await motor.run_for_degrees(motor_port, unit_to_degrees(amount, in_unit), motor_speed)

async def go_to_absolute_position(motor_port:int, orientation:int, position:int):
    await motor.run_to_absolute_position(motor_port,position,get_default_speed_for(motor_port),direction = orientation)

def start_motor(motor_port:int, orientation:int):
    motor_speed = get_default_speed_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        motor_speed = -motor_speed
    motor.run(motor_port, motor_speed)

def stop_motor(motor_port:int):
    motor.stop(motor_port)

def set_speed_to(motor_port:int, speed_percent:int):
    default_motor_speeds[motor_port] = speed_percent*10

def absolute_position(motor_port:int):
    return motor.absolute_position(motor_port)

def motor_speed(motor_port:int):
    return abs(motor.velocity(motor_port))

#MOVEMENT
async def move_for(steer_value: int, amount: float, in_unit: int):
    move_speed=default_movement_speed
    move_steer = steer_value
    if steer_value == direction.FORWARD:
        move_steer = 0
    elif steer_value == direction.BACKWARD:
        move_steer = 0
        move_speed = -default_movement_speed
    if in_unit == unit.SECONDS:
        await motor_pair.move_for_time(motor_pair.PAIR_1, int(amount*1000), move_steer, velocity= move_speed)
    else:
        await motor_pair.move_for_degrees(motor_pair.PAIR_1, unit_to_degrees(amount, in_unit), move_steer, velocity= move_speed)

def start_moving(steer_value: int):
    start_move_speed = default_movement_speed
    start_steer = steer_value
    if steer_value == direction.FORWARD:
        start_steer = 0
    elif steer_value == direction.BACKWARD:
        start_steer = 0
        start_move_speed = -default_movement_speed
    motor_pair.move(motor_pair.PAIR_1, start_steer, velocity= start_move_speed)

def stop_moving():
    motor_pair.stop(motor_pair.PAIR_1)

def set_movement_speed_to(speed_percent:int):
    global default_movement_speed
    default_movement_speed=speed_percent*10

def set_movement_motors_to(left_drive:int, right_drive:int):
    motor_pair.unpair(motor_pair.PAIR_1)
    motor_pair.pair(motor_pair.PAIR_1,left_drive, right_drive)

def set_1_motor_rotation_to_cm(circumference:float):
    global degrees_per_cm
    degrees_per_cm=360/circumference

#LIGHT
#None for now and maybe never

#SOUND
async def play_beep_for_seconds(key_number:int, duration:float, volume=75):
    #temporary translation, the frequency is not actually the keynote of word blocks
    await sound.beep(int(key_number*5), int(duration*1000), volume)

#EVENTS
#Please figure out on your own 
#See example in Competition Ready

#CONTROL
async def wait_seconds(amount:float):
    await runloop.sleep_ms(int(amount*1000))

async def wait_until(function):
    await runloop.until(function)
#Please learn basic python before coding in python

#SENSORS
def is_color(color_port:int, color_constant:int):
    return color_sensor.color(color_port) == color_constant

def get_color(color_port:int):
    return color_sensor.color(color_port)

#END OF TRANSLATOR