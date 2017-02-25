# Conan Veitch, 2017
#
# Lowest MAC address in the squad is nominated as squad leader.
# Squad leader moves towards destination, squad follows.
#
# Step by step process below:
#
# 1) Leader checks if squad members are within n cm.
# 2) If yes, leader moves forward.
# 3) Squad members stay within x cm, outside of y cm of one another.
# 4) If a squad member is outside of x cm from the leader, stop.
# 5) If a squad leader is outside of x cm from another member, stop.
# 6) When within range of all squad members, begin moving again.
#
#
#

from mobility import drive
from mobility import turn
from mobility import Direction
from mobility import Bearing
from wireless_control import broadcast
from wireless_control import receive_rssi
from wireless_control import get_mac
from threading import Thread
from threading import RLock
from kalman_filter import KalmanFilter
from time import sleep
import math

# Enum variables
forw = Direction.FORWARD
back = Direction.BACKWARD
right = Direction.RIGHT
left = Direction.LEFT
stop = Direction.STOP
fortyfive = Bearing.FORTY_FIVE
ninety = Bearing.NINETY

lock = RLock()

# Rupert specific variables
is_leader = False
in_formation = None
mac = None
d = None            # Desired distances between Ruperts
d_error = None      # Error tolerance for distance between Ruperts
dist_a = None       # distance from squad member 1/squad leader
dist_b = None       # distance from squad member 2

init_rss = None     # Kalman Filter initial rssi value
init_var = None     # Kalman Filter initial variance
sens_var = None     # Kalman Filter sensor variance
rssi_var = None     # Kalman Filter system variance

cal_dist = None     # RSSI to distance calibration distance
rssi_cal = None     # RSSI to distance calibration RSSI
ref_dist = None     # RSSI to distance reference distance
rssi_ref = None     # RSSI to distance reference RSSI

mac_rssi = {}       # keeps mac address rssi pairings
mac_filt = {}       # keeps mac address Kalman filter pairings
mac_dist = {}       # keeps mac address distance pairings


def main():
    # Run Squad Behaviour functions.
    sleep(1)
    initialize_rupert(50, 10, 0, 900, 5, 10, 50, 50, 100, 56)
    # This sleep allows some rssi data to build up in the Kalman filter.
    sleep(3)
    while 1:
        check_distance()
        if in_formation:
            # NOTE: THIS IS TEMPORARY.  WHEN IR SENSORS WORK, REMOVE THIS.
            if not dist_b < d - d_error:
                if mac == 1:
                    turn(left, fortyfive)
                if mac == 2:
                    turn(right, fortyfive)
            drive(forw, 0.25)
        elif not in_formation:
            while not in_formation:
                form_up()
            get_bearing()


def initialize_rupert(dist, dist_err, x0, p, r, q, dc, rdc, d0, rd0):
    global is_leader, in_formation, mac, d, d_error, init_rss, init_var, \
        sens_var,rssi_var, cal_dist, rssi_cal, ref_dist, rssi_ref
    in_formation = True     # Ruperts may assume they begin in formation
    mac = get_mac()         # Get our mac address, and check if we are the leader.
    if mac == 0:            # Set if this Rupert is the squad leader
        is_leader = True
    d = dist                # Initialize distance between Ruperts
    d_error = dist_err      # initialize distance error tolerance
    init_rss = x0           # Initialize Kalman Filter parameters
    init_var = p            # Initialize Kalman Filter parameters
    sens_var = r            # Initialize Kalman Filter parameters
    rssi_var = q            # Initialize Kalman Filter parameters
    cal_dist = dc           # Initialize RSSI-to-distance parameters
    rssi_cal = rdc          # Initialize RSSI-to-distance parameters
    ref_dist = d0           # Initialize RSSI-to-distance parameters
    rssi_ref = rd0          # Initialize RSSI-to-distance parameters

    # Begin broadcasting data and receiving distances
    Thread(target=broadcast, args=5)
    Thread(target=receive_distances())

    # THESE VALUES ARE DUMMY VALUES FOR TESTING WITHOUT ACTUAL RSSI VALUES
    global dist_a, dist_b
    dist_a = 5
    dist_b = 5


def receive_distances():
    global dist_a, dist_b
    # get a (mac address, rssi value) tuple from another feather, extract
    rssi_tuple = receive_rssi()
    rec_mac = rssi_tuple[0]
    rec_rssi = rssi_tuple[1]
    lock.acquire()
    if rec_mac in mac_rssi:  # get mac-rssi key pairs, put them in mac_rssi.
        mac_rssi[rec_mac] = rec_rssi
    else:        # Key a Kalman filter and an rssi tuple to the mac address.
        mac_rssi[rec_mac] = rec_rssi
        mac_filt[rec_mac] = KalmanFilter(init_rss, init_var, sens_var, rssi_var)
    mac_filt[rec_mac].predict()
    mac_filt[rec_mac].update(rec_rssi)
    f_rssi = mac_filt[rec_mac].x
    mac_dist[rec_mac] = rssi_to_distance(cal_dist, rssi_cal, ref_dist, rssi_ref, f_rssi)

    # This is ugly code that I hate, but I'll figure out a better way later:
    if is_leader and rec_mac == 1:
        dist_a = mac_dist[rec_mac]
    elif is_leader and rec_mac == 2:
        dist_b = mac_dist[rec_mac]
    elif (not is_leader) and rec_mac == 0:
        dist_a = mac_dist[rec_mac]
    else:
        dist_b = mac_dist[rec_mac]



def check_distance():
    global in_formation
    # Leader checks if it is out of range of both Ruperts.
    if is_leader and (dist_a > d + d_error or dist_b > d + d_error):
        drive(stop, 0)
        in_formation = False
    # Other ruperts check to see if they are out of range of leader.
    elif not is_leader and (dist_a > d + d_error or dist_a < d - d_error):
        drive(stop, 0)
        in_formation = False


def form_up():
    # If out of formation, this is how we get back.
    # Actions depend on mac address of the Rupert.
    global dist_a,dist_b, in_formation
    if is_leader:   # Leader doesn't move, it's at the top of the triangle.
        drive(stop, 0)

    else:           # Otherwise, other Ruperts get in range of the leader
        if dist_a > d + d_error or dist_a < d - d_error \
                or dist_b < d - d_error - d_error:
            turn(right, fortyfive)
            drive(forw, 0.25)


def get_bearing():
    global dist_a
    correct_bearing = False
    while not correct_bearing:
        last_d = dist_a
        drive(forw, 0.75)
        sleep(0.25)
        if last_d < dist_a:
            correct_bearing = True
        else:
            turn(right, ninety)


def rssi_to_distance(dc, rdc, d0, rd0, rssi):
    nu = (rdc - rd0) / (10 * float((math.log((dc / d0), 10))))     # Path loss Constant
    distance = ref_dist * math.pow(10, (rssi - rssi_ref) / (10 * nu))
    return distance


main()


