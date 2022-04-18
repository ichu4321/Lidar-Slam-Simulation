import random

import numpy as np
import point_math as pm

from vehicle import Vehicle

class SLAMMER:
	def __init__(self, width, height, pose):
		# initial empty grid
		self.grid = np.zeros((height, width), np.uint8);

		# initial position 
		self.car = Vehicle();
		self.car.setPose(pose);

	# update grid and return a new position (x,y,angle)
	def update(self, odometry, scan):
		raise NotImpementedError("update() function must return x,y,angle");

class RandomParticles(SLAMMER):
	def __init__(self, width, height, pose, num_particles = 50, num_iters = 3):
		# initialize base
		super(RandomParticles, self).__init__(width, height, pose);

		# set up particles
		self.num_parts = num_particles;
		self.iters = num_iters;
		self.particles = [];

	# uniform random position around position
	def randParticle(self, x, y, angle):
		scatter = 5;
		x += random.uniform(-scatter, scatter);
		y += random.uniform(-scatter, scatter);
		angle += random.uniform(-scatter, scatter);
		return Particle([x,y,angle]);

	def update(self, odometry, scan):
		# update to new position
		self.car.updateOdom(odometry);

		# generate a bunch of uniformly random Particles
		x,y = car.pos;
		self.particles = [self.randParticle(x, y, car.angle) for a in range(self.num_parts)];

		# evaluate particles
		self.evaluate(scan);

		# do loop
		for a in range(self.num_iters):
			# generate new random around best
			best = self.bestParticle();
			x,y,angle = best.pos;
			self.particles = [self.randParticle(x, y, angle) for a in range(self.num_parts)];

			# evaluate
			self.evaluate(scan);

		# update map with best
		best = self.bestParticle();
		

		# return final best position
		return best.pos;

	# give each particle a score
	def evaluate(self, scan):
		for particle in self.particles:
			particle.score = self.setScore(scan, particle.pos);

	# assign a score to the particle
	def setScore(self, scan, pos):
		# unpack
		x,y,angle = pos;
		height, width = self.grid.shape[:2];

		# evaulate each laser
		value = 0;
		for point in scan:
			deg, dist = point;
			if dist < 0.01:
				continue;

			# find hit location
			px,py = pm.hitPoint(dist, deg, [x,y], angle);
			if px >= 0 and px < width and py >= 0 and py < height:
				if grid[y,x] != 0:
					value += 1;
		return value;

	# returns the particle with the best score
	def bestParticle(self):
		best = self.particles[0];
		for particle in self.particles:
			if particle.score > best.score:
				best = particle;
		return best;

class Particle:
	def __init__(self, pos):
		self.pos = pos;
		self.score = 0;
