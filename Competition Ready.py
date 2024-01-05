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
'''

from hub import light, light_matrix, port, motion_sensor, button, sound
import runloop, motor, motor_pair, color_sensor, color, distance_sensor #from lego
import time, math#from micropython
from app import sound as appsound

# change names to follow convention: velocity is deg/sec, speed is percent of full speed as in wb
default_movement_speed = 50

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

class size:
    LARGE = 0
    MEDIUEM = 1
    SMALL = 2# large 1050 medium 1110 small 660

default_motor_speeds = {
}

max_velocity = 1110 # large 1050 medium 1110 small 660

movement_motors = []

def _absolute_position_wb2py(wb_position:int):
    if wb_position < 0:
        return 360+wb_position
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
def run_for(motor_port:int, orientation: int, amount: float, in_unit: int, speed = 0, wait = True):
    if speed != 0:
        in_speed = speed
    else:
        in_speed = get_default_speed_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        in_speed = -in_speed
    velocity = int(in_speed/100*max_velocity)
    degrees_to_run = unit_to_degrees(amount,in_unit, velocity)
    motor.run_for_degrees(motor_port, degrees_to_run, velocity)
    if wait:
        time.sleep_ms(int(1000*abs(degrees_to_run/velocity)))
        wait_until(lambda:motor.velocity(motor_port) ==0)

def go_to_absolute_position(motor_port:int, orientation:int, wb_position:int,wait = True):
    in_speed = get_default_speed_for(motor_port)
    target_position = _absolute_position_wb2py(wb_position)
    current_position = motor.absolute_position(motor_port)
    if target_position != current_position:
        motor.run_to_absolute_position(motor_port,target_position,int(in_speed/100*max_velocity),direction = orientation)
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
        if wait:
            time.sleep_ms(int(1000*(abs(degrees_to_run)/(in_speed/100*max_velocity))))
            wait_until(lambda:motor.velocity(motor_port) ==0)

def start_motor(motor_port:int, orientation:int,speed=0):
    if speed != 0:
        in_speed = speed
    else:
        in_speed = get_default_speed_for(motor_port)
    if orientation == motor.COUNTERCLOCKWISE:
        in_speed = - in_speed
    motor.run(motor_port, int(in_speed/100*max_velocity))

def stop_motor(motor_port:int):
    motor.stop(motor_port)

def set_speed_to(motor_port:int, speed_percent:int):
    default_motor_speeds[motor_port] = speed_percent

def absolute_position(motor_port:int):
    py_position = motor.absolute_position(motor_port)
    if py_position > 180: return py_position-360
    else: return py_position

#python api bug means it doesn't have to be converted :)
def motor_speed(motor_port:int):
    return abs(motor.velocity(motor_port))

#MOVEMENT
def move_for(direction_or_steer: int, amount: float, in_unit: int, speed = 0, wait = True):
    if speed == 0:
        in_speed = default_movement_speed
    else:
        in_speed = speed
    move_steer = direction_or_steer
    if direction_or_steer == direction.FORWARD:
        move_steer = 0
    elif direction_or_steer == direction.BACKWARD:
        move_steer = 0
        in_speed = -in_speed
    velocity = int(in_speed/100*max_velocity)
    degrees_to_run= unit_to_degrees(amount, in_unit, velocity)
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degrees_to_run, move_steer, velocity= velocity)
    if wait:
        time.sleep_ms(int(abs(degrees_to_run/velocity)*1000))
    # wait until it's done and stopped. Still need sleep other wise it may not even start
        wait_until(lambda: motor_speed(movement_motors[0])==0 and motor_speed(movement_motors[1]) ==0 )

def start_moving(steer_value: int, speed = 0):
    if speed == 0:
        in_speed = default_movement_speed
    else:
        in_speed = speed
    start_steer = steer_value
    if steer_value == direction.FORWARD:
        start_steer = 0
    elif steer_value == direction.BACKWARD:
        start_steer = 0
        in_speed = -in_speed
    velocity = int(in_speed/100*max_velocity)
    motor_pair.move(motor_pair.PAIR_1, start_steer, velocity= velocity)

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
        set_1_motor_rotation_to_cm(20.57)
    else:
        set_1_motor_rotation_to_cm(17.5)

#LIGHT
#None for now and maybe never

#SOUND
def play_beep_for_seconds(key_number:int, duration:float, volume=75):
    #temporary translation, the frequency is not actually the keynote of word blocks
    sound.beep(int(key_number*5), int(duration*1000), volume)

#EVENTS
#Please figure out on your own
#See example in Competition Ready

#Please learn basic python before coding in python

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

def start_moving_at_speed(left_speed: float, right_speed:float):
    motor_pair.move_tank(motor_pair.PAIR_1, int(left_speed/100*max_velocity), int(right_speed/100*max_velocity))

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

def go_to_relative_position_at_speed(motor_port:int, target_position:int, speed:int,wait = True):
    current_position = motor.relative_position(motor_port)
    motor.run_to_relative_position(motor_port, target_position, int(speed/100*max_velocity))
    if wait:
        time.sleep_ms(int(abs(target_position-current_position)/(speed/100*max_velocity)*1000))
        wait_until(lambda: motor.velocity(motor_port)==0)

#END SNAKE_TRANSLATOR

#Run Below Library Above

#Training Camp 1
def driving_around_main():
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(50)
    set_1_motor_rotation_to_cm(17.5)
    wait_seconds(1)
    set_yaw_angle_to(0)
    start_moving(100)
    wait_until(lambda: yaw_angle() > 89)
    stop_moving()

def driving_around_left():
    while True:
        wait_until(lambda: is_button_pressed(button.LEFT))
        wait_seconds(1)
        move_for(direction.FORWARD, 20,unit.CM)
        move_for(direction.BACKWARD, 20, unit.CM)

def driving_around_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        wait_seconds(1)
        start_moving(0)
        wait_until(lambda: is_color(port.A,color.BLACK))
        stop_moving()

def driving_square():
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(30)
    set_1_motor_rotation_to_cm(17.5)

    wait_seconds(1)
    for i in range (4):
        move_for(0, 10, unit.CM)
        move_for(100, 0.5, unit.ROTATIONS)

#Training Camp 2
def playing_with_objects():
    set_movement_motors_to(port.C,port.D)
    set_movement_speed_to(30)
    set_1_motor_rotation_to_cm(17.5)
    set_speed_to(port.E,20)
    run_for(port.E,motor.CLOCKWISE,1,unit.SECONDS)
    run_for(port.E, motor.COUNTERCLOCKWISE, 1, unit.SECONDS)
    play_beep_for_seconds(60,0.2)
    play_beep_for_seconds(72,0.2)

#Training Camp 3
def reacting_to_lines_left():
    def enough(): return is_color(port.B, color.BLACK)
    while True:
        wait_until(lambda: is_button_pressed(button.LEFT))
        set_movement_motors_to(port.E, port.F)
        set_movement_speed_to(50)
        start_moving(0)
        wait_until(enough)
        stop_moving()

def reacting_to_lines_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        set_movement_motors_to(port.C,port.D)
        set_movement_speed_to(30)
        while True:
            if is_color(port.B, color.BLACK):
                start_moving(50)
            else:
                start_moving(-50)

def reacting_to_lines_alt():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        set_movement_motors_to(port.C,port.D)
        power = 30
        while True:
            if reflection(port.B)<50:
                start_moving_at_speed(5, power)
            else:
                start_moving_at_speed(power,5)

def relative_distance_cm(motor_port:int):
    return abs(relative_position(motor_port)/degrees_per_cm)

def test_moving():
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(20)
    '''
    start_moving(direction.FORWARD)
    wait_seconds(2)
    start_moving(direction.BACKWARD)
    wait_seconds(2)
    '''
    start_moving(80)

#Training Camp 4
#hint, combine start_moving and wait_until functions for a "move_until" function to save time
def guided_mission_full():
    run_for(port.E, motor.COUNTERCLOCKWISE,1,unit.ROTATIONS)
    set_relative_position_to(port.E,0)
    go_to_relative_position_at_speed(port.E,140, 75)
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(30)
    set_yaw_angle_to(0)
    speed = 30
    wait_seconds(1)
    move_for(direction.FORWARD, 1, unit.ROTATIONS)
    start_moving(-30)
    wait_until(lambda: is_color(port.B, color.BLACK))
    while not 44<yaw_angle():
        if reflection(port.B) <50:
            start_moving_at_speed(speed,0)
        else:
            start_moving_at_speed(0,speed)
    stop_moving()
    wait_seconds(1)
    start_moving(-100)
    wait_until(yaw_angle()<-89)
    stop_moving()
    move_for(0,6.5,unit.DEGREES)
    start_moving(-30)
    wait_until(lambda: is_color(port.B, color.BLACK))
    stop_moving()
    start_moving_at_speed(50,0)
    wait_until(lambda: -46<yaw_angle())
    stop_moving()
    start_moving(direction.FORWARD)
    wait_until(lambda: is_color(port.B, color.BLACK))
    go_to_relative_position_at_speed(port.E,55,50)
    for i in range(2): #this is how many times the robot pushes forward
        start_moving(direction.BACKWARD)
        wait_until(lambda: is_color(port.B, color.BLACK))
        stop_moving()
        move_for(direction.FORWARD,0.7,unit.ROTATIONS)
        stop_moving()
    go_to_relative_position_at_speed(port.E, 140,75)
    start_moving(-direction.BACKWARD)
    wait_until(lambda: is_color(port.B, color.BLACK))
    stop_moving()
    start_moving_at_speed(-50,50)
    wait_until(lambda:yaw_angle()<-170)
    stop_moving()
    move_for(direction.FORWARD,3,unit.ROTATIONS)

#Training Camp 5
def advanced_driving():
    set_movement_motors_to(port.C,port.D)
    set_movement_speed_to(50)
    set_1_motor_rotation_to_cm(17.5)
    wait_seconds(1)
    move_for(direction.FORWARD,20,unit.CM)
    move_for(direction.BACKWARD, 20, unit.CM)
    move_for(-40,20,unit.ROTATIONS)
    set_yaw_angle_to(0)
    start_moving(100) 
    wait_until(lambda: yaw_angle()>90)
    start_moving(-100)
    wait_until(lambda: yaw_angle()<0)

#Training Camp 6
def my_code_main():
    set_movement_motors_to(port.E,port.F)
    set_movement_speed_to(100)
    set_1_motor_rotation_to_cm(17.5)

def forward():
    move_for(direction.FORWARD,5,unit.ROTATIONS)

def my_code_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        forward()
        appsound.play('Wand')
        appsound.play('Emotional Piano')

#Training Camp 7
def upgrade_time():
    set_speed_to(port.C,100)
    run_for(port.C,motor.COUNTERCLOCKWISE,1,unit.SECONDS)
    run_for(port.C, motor.CLOCKWISE,70, unit.DEGREES)
    play_beep_for_seconds(60,0.2)
    run_for(port.C, motor.CLOCKWISE,180,unit.DEGREES)

#Training Camp 8
def mission_ready():
    #do your own
    pass

#input everything here
async def main():
    set_movement_motors_to(port.E,port.F)
    mission_ready

runloop.run(main())
