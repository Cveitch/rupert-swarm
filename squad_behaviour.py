# Conan Veitch, 2017
#
# Squads arrange themselves into a triangular pattern.
# Behaviour model:
# 1. Lowest MAC address is the top of the triangle, next lowest is
#    left corner, remaining is right corner.
# 2. Squad moves forward in the direction of the top of the triangle.
# 3. Members travel forward until they break formation, or get somewhere.
# 4. If member breaks formation, all members stop.
# 5. Lowest MAC stays stationary.  Next lowest gets in range of lowest.
# 6. Last Rupert gets in range of both.
# 7. Now that formation is back, they get a bearing.



from mobility import drive
from mobility import turn
from mobility import Direction
from mobility import Bearing
from wireless_control import broadcast
from wireless_control import receive
from wireless_control import get_mac
import math
import time
import _thread


forw = Direction.FORWARD
back = Direction.BACKWARD
right = Direction.RIGHT
left = Direction.LEFT
stop = Direction.STOP
fortyfive = Bearing.FORTY_FIVE
ninety = Bearing.NINETY


def update_angles():
    # Use law of cosines to get all angles.
    global dist_b
    global dist_c
    global dist_bc
    b = dist_bc
    c = dist_b
    bc = dist_c
    arc_a = (-(bc*bc) + b*b + c*c) / (2*b*c)
    arc_b = (bc*bc - b*b + c*c) / (2*bc*c)
    arc_c = (bc*bc + b*b - c*c) / (2*bc*b)
    global angle_a
    global angle_b
    global angle_c
    angle_a = math.acos(arc_a)
    angle_b = math.acos(arc_b)
    angle_c = math.acos(arc_c)


def check_formation():
    # Check angle, if angle is approx. 60 deg, move forward.
    # If angle not approx. 60, stop.  Alert the others.
    global in_formation
    update_angles()
    if angle_a < 50 or angle_a > 70:
        drive(stop, 0)
        in_formation = False
    else:
        drive(forw, 0.5)
        in_formation = True


def form_up(mac_num):
    # If out of formation, this is how we get back.
    # Actions depend on mac address of the Rupert.
    global dist_b
    global dist_c
    global range_ceiling
    global range_floor
    global in_formation
    if mac_num == 0:
        drive(stop, 0)
    elif mac_num == 1 and (dist_c < range_floor or dist_c > range_ceiling):
        turn(right, fortyfive)
        drive(forw, 0.5)
    elif mac_num == 2 and (dist_b < range_floor or dist_b > range_ceiling or
                                   dist_c < range_floor or dist_c > range_ceiling):
        turn(right, fortyfive)
        drive(forw, 0.5)
    # If all these are satisfied, we are back in formation.
    else:
        in_formation = True

def get_bearing():
    # Once back in formation, we need the Ruperts to be facing
    # the same direction.
    global angle_a
    update_angles()
    forward_bearing = False
    # If we aren't pointing in the correct direction,
    # turn and try again.
    while not forward_bearing:
        drive(forw, 2)
        update_angles()
        drive(back, 2)
        if angle_a < 65:
            turn(fortyfive)
        else:
            forward_bearing = True




# Run Squad Behaviour functions.
time.sleep(2)

# Get our mac address.
mac = get_mac()
# Boolean to see if we are in formation or not.
in_formation = False
# This is the distance in cm we require between Ruperts for the formation.
node_range = 40
range_ceiling = node_range + 10
range_floor = node_range - 10

# We consider our Rupert to be a, but b and c depend on mac address.
# If this Rupert is 0, then b is 1, and c is 2.
# If this Rupert is 1, then b is 2, and c is 0.
# If this Rupert is 2, then b is 0, and c is 1.
dist_b = 0      # distance from a to b
dist_c = 0      # distance from a to c
dist_bc = 0     # distance from b to c, taken from b and c.

angle_a = 60    # angle bac
angle_b = 60    # angle abc
angle_c = 60    # angle bca

_thread.start_new_thread(receive)
_thread.start_new_thread(broadcast(1))

time.sleep(2)

while 1:
    check_formation()
    if not in_formation:
        while not in_formation:
            form_up(mac)
        get_bearing(mac)



