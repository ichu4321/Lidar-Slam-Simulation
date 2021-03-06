import cv2
import numpy as np

from vehicle import Vehicle
from solution import RandomParticles

import noise
import point_math as pm

def simulate():
	# create vehicles
	ground_truth = Vehicle();
	noisy_odom = Vehicle();
	slam_car = Vehicle();

	# set noise params
	turn_noise = 0.10;
	move_noise = 0.10;

	# load playback file
	bg, grid, poses, scans = pm.loadPlayback("PLAYBACK.xz");
	height, width = bg.shape[:2];

	# set initial position
	ground_truth.setPose(poses[0]);
	noisy_odom.setPose(poses[0]);
	slam_car.setPose(poses[0]);

	# set up slam solution
	solver = RandomParticles(height, width, poses[0]);

	# run simulation
	done = False;
	index = 1;
	freeze = False;
	while not done:
		# refresh display
		display = np.copy(bg);

		# get scan
		scan = scans[index];

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
			x,y,angle = solver.update([turn1, move, turn2], scan);
			slam_car.pos = [x,y];
			slam_car.angle = angle;

		# draw scan
		x,y = slam_car.pos;
		angle = slam_car.angle;
		pm.updateMap(bg, [x,y,angle], scan, (0,200,0), display = display);

		# draw cars
		ground_truth.draw(display);
		noisy_odom.draw(display, color = (0,0,150));
		slam_car.draw(display, color = (0,150,0));

		# show
		cv2.imshow("Display", display);
		cv2.imshow("Solution", solver.grid);
		key = cv2.waitKey(100);

		# update index
		# freeze = True;
		index += 1;
		if index >= len(poses):
			index = len(poses) - 1;
			freeze = True;
			done = True;

		# process keys
		done = key == ord('q');
	cv2.imwrite("slam_map.png", solver.grid);

if __name__ == "__main__":
	# run simulation
	simulate();

# 1578, -65