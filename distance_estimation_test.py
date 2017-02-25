# This class is exclusively for testing purposes.


import csv
from kalman_filter import KalmanFilter
from threading import RLock

file_name1 = '/home/conan/PycharmProjects/rupert-swarm/assets/testcsv.csv'
# file_name2 = '/home/conan/PycharmProjects/rupert-swarm/assets/test2.csv' #Linear Movement Test
# file_name3 = '/home/conan/PycharmProjects/rupert-swarm/assets/test3.csv' #Back and forth test
# file_name4 = '/home/conan/PycharmProjects/rupert-swarm/assets/test4.csv' #Move stop move test
#
with open(file_name1, newline = '') as input_file:
    input_reader=csv.reader(input_file)
    RSSI_input = [int(val) for x in list(input_reader) for val in x]
#
# with open(file_name2, newline = '') as input_file:
#     input_reader=csv.reader(input_file)
#     DIST_input = [float(val) for x in list(input_reader) for val in x]
#
# with open(file_name3, newline = '') as input_file:
#     input_reader=csv.reader(input_file)
#     BF_input = [float(val) for x in list(input_reader) for val in x]
#
#     with open(file_name4, newline='') as input_file:
#         input_reader = csv.reader(input_file)
#         MSM_input = [float(val) for x in list(input_reader) for val in x]
#
#
# kfilter1 = KalmanFilter(0, 900, 5, 10)
# kfilter2 = KalmanFilter(0, 900, 5, 10)
# kfilter3 = KalmanFilter(0, 900, 10, 5)
# kfilter4 = KalmanFilter(0, 900, 10, 5)
#
# for a in RSSI_input:
#     kfilter1.predict()
#     kfilter1.update(a)
#
#     kfilter2.predict(5)
#     kfilter2.update(a)
#
#     kfilter3.predict()
#     kfilter3.update(a)
#
#     kfilter4.predict(5)
#     kfilter4.update(a)

    # print(kfilter2.x, kfilter4.x)


def receive_rssi():
    # receive broadcast from another feather.
    mac_address = 0
    rssi_received = 20
    return mac_address, rssi_received


lock = RLock()
mac_filt = {}

mac_filt[0] = KalmanFilter(0, 900, 5, 10)

for a in RSSI_input:
    mac_filt[0].predict()
    mac_filt[0].update(a)
    print(mac_filt[0].x)















