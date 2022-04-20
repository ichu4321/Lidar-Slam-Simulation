import random

import numpy as np
import point_math as pm

from vehicle import Vehicle

class SLAMMER:
	def __init__(self, width, height, initial_pose):
		# initial empty grid
		self.grid = np.zeros((height, width), np.uint8);
		self.empty_grid = True;

		# initial position 
		self.car = Vehicle();
		self.car.setPose(initial_pose);

	# update grid and return a new position (x,y,angle)
	def update(self, odometry, scan):
		raise NotImpementedError("update() function must return x,y,angle");

class RandomParticles(SLAMMER):
	def __init__(self, width, height, initial_pose, num_particles = 20, num_iters = 10):
		# initialize base
		super(RandomParticles, self).__init__(width, height, initial_pose);

		# set up particles
		self.num_parts = num_particles;
		self.iters = num_iters;
		self.particles = [];

		# set up blur patterns
		self.blur = pm.makeBlur(0,255,5);

	# uniform random position around position
	def randParticle(self, x, y, angle):
		scatter = 2.0;
		x += random.uniform(-scatter, scatter);
		y += random.uniform(-scatter, scatter);
		angle += random.uniform(-1.0, 1.0);
		return Particle([x,y,angle]);

	def update(self, odometry, scan):
		# seed the map with the first scan
		if self.empty_grid:
			self.empty_grid = False;
			x,y = self.car.pos;
			angle = self.car.angle;
			pm.updateMap(self.grid, [x,y,angle], scan, 255, max_dist = 400);
			# pm.updateMapBlur(self.grid, [x,y,angle], scan, self.blur);
			return [x,y,angle];

		# update to new position
		self.car.updateOdom(odometry);

		# generate a bunch of uniformly random Particles
		x,y = self.car.pos;
		self.particles = [self.randParticle(x, y, self.car.angle) for a in range(self.num_parts)];
		self.particles.append(Particle([x,y,self.car.angle]));

		# evaluate particles
		self.evaluate(scan);

		# do loop
		for a in range(self.iters):
			# generate new random around best
			best = self.bestParticle();
			x,y,angle = best.pos;
			self.particles = [self.randParticle(x, y, angle) for a in range(self.num_parts)];
			self.particles.append(best);

			# evaluate
			self.evaluate(scan);

		# update map with best
		best = self.bestParticle();
		pm.updateMap(self.grid, best.pos, scan, 255, max_dist = 400);
		# pm.updateMapBlur(self.grid, best.pos, scan, self.blur);

		# return final best position
		x,y,angle = best.pos;
		self.car.pos = [x,y];
		self.car.angle = angle;
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
				value += self.grid[py,px];
		return value;

	# returns the particle with the best score
	def bestParticle(self):
		best = self.particles[0];
		for particle in self.particles:
			if particle.score > best.score:
				best = particle;
		# print("Best: " + str(best.score));
		return best;

class Particle:
	def __init__(self, pos):
		self.pos = pos;
		self.score = 0;