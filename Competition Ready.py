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
import runloop, motor, motor_pair, color_sensor, color #from lego
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

def move_until(steer_value:int, function):
    start_moving(steer_value)
    wait_until(function)
    stop_moving()

def move_at_speed_until(left_speed:int,right_speed:int, function):
    start_moving_at_speed(left_speed,right_speed)
    wait_until(function)
    stop_moving()

#END OF LIBRARY

#Run Below Library Above

#Training Camp 1
async def driving_around_main():
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(50)
    set_1_motor_rotation_to_cm(17.5)
    wait_seconds(1)
    set_yaw_angle_to(0)
    start_moving(100)
    wait_until(lambda: yaw_angle() > 89)
    stop_moving()

async def driving_around_left():
    while True:
        wait_until(lambda: is_button_pressed(button.LEFT))
        wait_seconds(1)
        move_for(direction.FORWARD, 20,unit.CM)
        move_for(direction.BACKWARD, 20, unit.CM)

async def driving_around_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        wait_seconds(1)
        start_moving(0)
        wait_until(lambda: is_color(port.A,color.BLACK))
        stop_moving()

async def driving_square():
    set_movement_motors_to(port.E, port.F)
    set_movement_speed_to(30)
    set_1_motor_rotation_to_cm(17.5)

    wait_seconds(1)
    for i in range (4):
        move_for(0, 10, unit.CM)
        move_for(100, 0.5, unit.ROTATIONS)

#Training Camp 2
async def playing_with_objects():
    set_movement_motors_to(port.C,port.D)
    set_movement_speed_to(30)
    set_1_motor_rotation_to_cm(17.5)
    set_speed_to(port.E,20)
    run_for(port.E,motor.CLOCKWISE,1,unit.SECONDS)
    run_for(port.E, motor.COUNTERCLOCKWISE, 1, unit.SECONDS)
    play_beep_for_seconds(60,0.2)
    play_beep_for_seconds(72,0.2)

#Training Camp 3
async def reacting_to_lines_left():
    def enough(): return is_color(port.B, color.BLACK)
    while True:
        wait_until(lambda: is_button_pressed(button.LEFT))
        set_movement_motors_to(port.E, port.F)
        set_movement_speed_to(50)
        start_moving(0)
        wait_until(enough)
        stop_moving()

async def reacting_to_lines_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        set_movement_motors_to(port.C,port.D)
        set_movement_speed_to(30)
        while True:
            if is_color(port.B, color.BLACK):
                start_moving(50)
            else:
                start_moving(-50)

async def reacting_to_lines_alt():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        set_movement_motors_to(port.C,port.D)
        power = 30
        while True:
            if reflection(port.B)<50:
                start_moving_at_speed(5, power)
            else:
                start_moving_at_speed(power,5)

def gain_line_follow(condition): #from training camp 3 education lego version
    desired_power = 25
    gain = 0.3
    average = 55
    count = 0
    while not condition():
        count += 1
        left_power = int(desired_power - gain*(average - reflection(port.A)))
        right_power = int(desired_power + gain*(average - reflection(port.A)))
        start_moving_at_speed(left_power, right_power)
    stop_moving()

def gain_yaw_follow(expected_yaw:int, condition): #gyro straight
    desired_power = 25
    gain = 0.3
    average = expected_yaw
    count = 0
    while not condition():
        count += 1
        left_power = int(desired_power + gain*(average - yaw_angle()))
        right_power = int(desired_power - gain*(average - yaw_angle()))
        start_moving_at_speed(left_power, right_power)
    stop_moving()

def steer_by_yaw(expected_yaw:int, condition, velocity= default_movement_velocity):
    while not condition():
        motor_pair.move(motor_pair.PAIR_1, expected_yaw-yaw_angle(), velocity= velocity*10)
    stop_moving()

def relative_distance_cm(motor_port:int):
    return abs(relative_position(motor_port)/degrees_per_cm)

async def test_moving():
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
async def guided_mission_short():
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
    move_until(-100, lambda:yaw_angle()<-89)
    move_for(0,6.5,unit.DEGREES)
    move_until(-30, lambda:is_color(port.B, color.BLACK))
    move_at_speed_until(50,0,lambda: -46<yaw_angle())
    move_until(direction.FORWARD,lambda: is_color(port.B, color.BLACK))
    go_to_relative_position_at_speed(port.E,55,50)
    for i in range(2): #this is how many times the robot pushes forward
        start_moving(direction.BACKWARD)
        wait_until(lambda: is_color(port.B, color.BLACK))
        stop_moving()
        move_for(direction.FORWARD,0.7,unit.ROTATIONS)
        stop_moving()
    go_to_relative_position_at_speed(port.E, 140,75)
    move_until(direction.BACKWARD,lambda: is_color(port.B, color.BLACK))
    move_at_speed_until(-50,50,lambda:yaw_angle()<-170)
    move_for(direction.FORWARD,3,unit.ROTATIONS)

async def guided_mission_full():
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
async def advanced_driving():
    set_movement_motors_to(port.C,port.D)
    set_movement_speed_to(50)
    set_1_motor_rotation_to_cm(17.5)
    wait_seconds(1)
    move_for(direction.FORWARD,20,unit.CM)
    move_for(direction.BACKWARD, 20, unit.CM)
    move_for(-40,20,unit.ROTATIONS)
    set_yaw_angle_to(0)
    move_until(100, lambda: yaw_angle()>90)
    move_until(-100, lambda: yaw_angle()<0)

#Training Camp 6
async def my_code_main():
    set_movement_motors_to(port.E,port.F)
    set_movement_speed_to(100)
    set_1_motor_rotation_to_cm(17.5)

def forward():
    move_for(direction.FORWARD,5,unit.ROTATIONS)

async def my_code_right():
    while True:
        wait_until(lambda: is_button_pressed(button.RIGHT))
        forward()
        appsound.play('Wand')
        appsound.play('Emotional Piano')

#Training Camp 7
async def upgrade_time():
    set_speed_to(port.C,100)
    run_for(port.C,motor.COUNTERCLOCKWISE,1,unit.SECONDS)
    run_for(port.C, motor.CLOCKWISE,70, unit.DEGREES)
    play_beep_for_seconds(60,0.2)
    run_for(port.C, motor.CLOCKWISE,180,unit.DEGREES)

#Training Camp 8
async def mission_ready():
    #do your own
    set_movement_motors_to(port.E, port.F)

#Techies Code
def match_color(color_port:int, r,g,b,i):
    rgbi = color_sensor.rgbi(color_port)
    return abs(rgbi[0] - r) <= 5 and abs(rgbi[1] - g) <= 5 and abs(rgbi[2] - b) <= 5 and abs(rgbi[3] - i) <= 5


#runloop.run(driving_around_main(), driving_around_left(), driving_around_right())
#runloop.run(driving_square())
#runloop.run(playing_with_objects(), driving_around_left(),driving_around_right())
#runloop.run(reacting_to_lines_left(), reacting_to_lines_right())
#runloop.run(reacting_to_lines_other())

runloop.run(guided_mission_full())
'''
async def when_right_button_pressed_old():
    while True:
        runloop.until(lambda: button.pressed(button.RIGHT)> 0)
        runloop.sleep_ms(1000)
        motor_pair.move_for_degrees(motor_pair.PAIR_1, 7200, -40, velocity= default_movement_speed)


async def when_left_button_pressed_old():
    while True:
        runloop.until(lambda: button.pressed(button.LEFT)>0)
        runloop.sleep_ms(1000)
        motor_pair.move_for_degrees(motor_pair.PAIR_1, int(20*degrees_per_cm), 0, velocity= default_movement_speed)
        motor_pair.move_for_degrees(motor_pair.PAIR_1, int(20*degrees_per_cm), 0, velocity= -default_movement_speed)

async def driving_around_old():
    motor_pair.pair(motor_pair.PAIR_1, port.C, port.D)
    runloop.sleep_ms(1000)
    motion_sensor.reset_yaw(0)
    motor_pair.move(motor_pair.PAIR_1, 100, velocity= default_movement_speed)
    runloop.until(lambda: motion_sensor.tilt_angles()[0]<-890)
    motor_pair.stop(motor_pair.PAIR_1)
'''