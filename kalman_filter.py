# Conan Veitch, 2017
# Filters any incoming data.
# Code for the one dimensional Kalman filter is adapted from
# https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python.

class KalmanFilter:

    def __init__(self, x0, P, R, Q):
        self.x = x0  # Initializes RSSI.
        self.P = P   # Initial RSSI Variance (eg 400=20^2, so 97% confident within 60)
        self.R = R   # Sensor Variance - experimentally found
        self.Q = Q   # RSSI Variance - experimentally found

    def update(self, z):
        # Scales measurement and prior by weights: W1*mu2 + W2*mu2.
        # This is Kalman gain: W1 = K = (sigma2^2)/(sigma2^2+sigma1^2)
        self.x = (self.P * z + self.x * self.R) / (self.P + self.R)
        # The variance.  (PR)/P+R)
        self.P = 1. / (1./self.P + 1./self.R)

    def predict(self, u=0.0): # u is the movement expected.
        self.x += u
        self.P += self.Q


# In order to use, initialize, predict, then update in order to filter values.
