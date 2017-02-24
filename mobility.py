# Conan Veitch, 2017
#
# Mobility controls for the Ruperts.
# All values are experimental.

from enum import Enum
from time import sleep

class Direction(Enum):
    RIGHT = "right"
    LEFT = "left"
    FORWARD = "forward"
    BACKWARD = "backward"
    STOP = "stop"

class Bearing(Enum):
    # Value is time taken to turn the appropriate amount.
    # Values are experimental.
    FORTY_FIVE = 0.25
    NINETY = 0.5


def drive(direction, n):
    # Check for direction argument
    if not isinstance(direction, Direction):
        raise TypeError('Must be an instance of Direction')
    if direction == Direction.FORWARD:
        1+1 # Send command to Feather to drive forward n seconds.
    elif direction == Direction.BACKWARD:
        1+1 # Send command to Feather to drive backward n seconds.
    elif direction == Direction.STOP:
        1+1 # Send command to Feather to stop moving.
    sleep(n)

def turn(direction, bearing):
    # Check for direction argument
    if not isinstance(direction, Direction):
        raise TypeError('Must be an instance of Direction')
    # Check for bearing argument
    if not isinstance(bearing, Bearing):
        raise TypeError('Must be an instance of Direction')

    if direction == Direction.RIGHT:
        1 + 1 # Send command to Feather to turn right at an angle of bearing.
    elif direction == Direction.LEFT:
        1 + 1 # Send command to Feather to turn right at an angle of bearing.
    sleep(bearing.value)
