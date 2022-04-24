import math
import random
import numpy as np

# generate a uniformly noisy element
def addNoiseUniform(elem, proportion):
	noise = elem * proportion;
	noise = random.uniform(-noise, noise);
	return elem + noise;

# generate a gaussian noisy element
def addNoiseNormal(elem, proportion):
	stdev = elem * proportion;
	noise = random.gauss(elem, stdev);
	return noise;

# generate random noise from odometry
def odomNoise(turn1, move, turn2, move_prop, turn_prop):
	noisy_move = addNoiseNormal(move, move_prop);
	noisy_turn1 = addNoiseNormal(turn1, turn_prop);
	noisy_turn2 = addNoiseNormal(turn2, turn_prop);
	return noisy_turn1, noisy_move, noisy_turn2;

# generate random proportional noise from sensor
# noise is proportional to range
def sensorNoiseProp(scan, proportion):
	noisy_scan = [];
	for hit in scan:
		angle, dist = hit;
		dist = addNoiseNormal(dist, proportion);
		noisy_scan.append([angle, dist]);
	return noisy_scan;

# generate random static noise from sensor
# noise is always the same
def sensorNoiseStatic(scan, noise):
	noisy_scan = [];
	for hit in scan:
		angle, dist = hit;
		dist += random.uniform(-noise, noise);
		noisy_scan.append([angle, dist]);
	return noisy_scan;
