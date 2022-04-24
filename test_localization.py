import cv2
import numpy as np

from vehicle import Vehicle
from solution import RandomParticles

import noise
import point_math as pm

def localize(playback_file, slam_map = None):
	# create vehicles
	ground_truth = Vehicle();
	noisy_odom = Vehicle();

	# set noise params
	turn_noise = 0.25;
	move_noise = 0.25;

	# load playback file
	bg, grid, poses, scans = pm.loadPlayback(playback_file);
	height, width = bg.shape[:2];

	# set initial position
	ground_truth.setPose(poses[0]);
	noisy_odom.setPose(poses[0]);

	# set up slam solution
	solver = RandomParticles(height, width, poses[0], num_particles = 25, num_iters = 5);

	# seed the slam solution with the map
	if slam_map is not None:
		grid = pm.loadMap(slam_map);
	solver.grid = grid;

	# run simulation
	done = False;
	index = 1;
	freeze = False;
	while not done:
		# refresh display
		display = np.copy(bg);

		# get scan and add noise
		scan = scans[index];
		scan = noise.sensorNoiseStatic(scan, 10);

		# get current and previous poses to get odom
		currPos = poses[index];
		turn1 = move = turn2 = 0;
		if index > 0:
			lastPos = poses[index - 1];
			turn1, move, turn2 = pm.getOdom(lastPos, currPos);

		# add noise
		turn1, move, turn2 = noise.odomNoise(turn1, move, turn2, move_noise, turn_noise);

		# update position
		if not freeze:
			ground_truth.setPose(currPos);
			noisy_odom.update(move, turn1);
			noisy_odom.update(0, turn2);

			# evaluate solution
			solver.localize([turn1, move, turn2], scan);

		# draw scan
		scan = scan;
		x,y = solver.car.pos;
		angle = solver.car.angle;
		pm.updateMap(display, [x,y,angle], scan, (0,200,0), display = display);

		# draw cars
		ground_truth.draw(display);
		noisy_odom.draw(display, color = (0,0,150));
		solver.car.draw(display, color = (0,150,0));

		# show
		cv2.imshow("Display", display);
		cv2.imshow("Solution", solver.grid);
		key = cv2.waitKey(1);

		# update index
		index += 1;
		if index >= len(poses):
			index = len(poses) - 1;
			freeze = True;
			done = True;

		# process keys
		done = key == ord('q');

if __name__ == "__main__":
	# run simulation
	localize("PLAYBACK.xz");

# 1578, -65