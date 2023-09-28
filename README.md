# python translator
For Spike Prime 
* Library of word blocks & python functions
* Use to easily turn word block programs to python

## Why I made this translator
Spike Prime transitioned from version 2 to version 3 in the summer of 2023. The python in version 3 is a lot less intuitive than than how it is written in version 2, and there aren't many tutorials on how to write using Spike Prime's python in version 3. So, I created this translator to hopefully allow python to be more accessible to anyone using Spike Prime.

## How to use

| Word Block | Python |
|---|---|
| ![run_for](./images/run_for.png) | ` run_for(port.A, motor.CLOCKWISE, 1, unit.ROTATIONS)`|
| ![go_to_position](./images/go_to_position.png) | ` go_to_absolute_position(port.A, motor.SHORTEST_PATH, 0)`|
| ![start_motor](./images/start_motor.png) | ` start_motor(port.A,motor.CLOCKWISE)`|
| ![stop_motor](./images/stop_motor.png) | ` stop_motor(port.A)`|
| ![set_speed_to](./images/set_speed_to.png) | `set_speed_to(port.A,75)`|
| ![absolute_position](./images/absolute_position.png) | `absolute_position(port.A)`|
| ![motor_speed](./images/motor_speed.png) | `motor_speed(port.A)`|
| ![move_for](./images/move_for.png) | `move_for(direction.FORWARD, 10, unit.ROTATIONS)`|
| ![steer_for](./images/steer_for.png) | `move_for(30, 10, unit.ROTATIONS)`|
| ![start_moving](./images/start_moving.png) | `start_moving(direction.FORWARD)`|
| ![start_steering](./images/start_steering.png) | `start_moving(30)`|
| ![stop_moving](./images/stop_moving.png) | `stop_moving()`|
| ![set_movement_speed_to](./images/set_movement_speed_to.png) | `set_movement_speed_to(50)`|
| ![set_movement_motors_to](./images/set_movement_motors_to.png) | `set_movement_motors_to(port.A, port.B)`|
| ![set_1_motor_rotation_to_cm](./images/set_1_motor_rotation_to_cm.png) | `set_1_motor_rotation_to_cm(17.5)`|
| ![play_beep_for_seconds](./images/play_beep_for_seconds.png) | `play_beep_for_seconds(60, 0.2)`|
| ![wait_seconds](./images/wait_seconds.png) | `wait_seconds(1)`|
| ![wait_until](./images/wait_until.png) | `wait_until(lambda: expression)`|
| ![is_color](./images/is_color.png) | `is_color(port.A, color.RED)`|
| ![get_color](./images/get_color.png) | `get_color(port.A)`|
