import cv2
import numpy as np

import math


class randomSlam:
	def __init__(self, num_particles = 100, num_iters = 5):
		# search parameters
		self.num_particles = num_particles;
		self.num_iters = num_iters;

		self.map = None;
		self.internal = None; # internal representation of the map

	# update map and return new position
	def update(self, pos, scan):
		pass;

