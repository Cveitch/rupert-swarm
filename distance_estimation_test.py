import csv
from kalman_filter import KalmanFilter


pr = 3 #variance in the process model (RSSI)
se = 5 #variance in the sensor itself
ol = 1089 # 33^2, so 97 percent confident that initial value lies within 100

file_name = '/home/conan/Desktop/testData.csv'

with open(file_name, newline = '') as input_file:
    input_reader=csv.reader(input_file)
    RSSI_input = [int(val) for x in list(input_reader) for val in x]


filter = KalmanFilter(pr, se, ol)



i = 0
for x in RSSI_input:
    print(filter.old_val, RSSI_input[i] , filter.k_filter(RSSI_input[i]))

    i = i +1