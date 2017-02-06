# Conan Veitch, 2017
# Code for Kalman filter is adapted from https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python

class KalmanFilter:

    process_vari = 0
    sensor_vari = 0
    old_val = 0

    def __init__(self, pro_var, sens_var, ol_val):
        self.process_vari = pro_var
        self.sensor_vari = sens_var
        self.old_val = ol_val

    def gaussian_multiply(self, g1, g2): #Takes two Gaussians as argument
        mu1, vari1 = g1
        mu2, vari2 = g2
        mean = (vari1 * mu2 + vari2 * mu1) / (vari1 + vari2)
        variance = (vari1 * vari2) / (vari1 + vari2)
        return (mean, variance)

    def update(self, prior, likelihood):
        posterior = self.gaussian_multiply(likelihood, prior)
        return posterior

    def predict(self, posterior, process_model):
        meanP = variP = posterior
        meanPM = variPM = process_model
        meanP = meanP + meanPM
        variP = variP + variPM
        return meanP, variP

    def k_filter(self, input):
        prior = self.predict(self.old_val, self.process_vari)
        likelihood = (input, self.sensor_vari)
        old_val = self.update(prior, likelihood)
        return old_val