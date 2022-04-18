import cv2
import time
import numpy as np

from vehicle import Vehicle

import lzma
import pickle

import point_math as pm

import noise




def main():
	# open the recording
	filename = "record.txt";
	file = open(filename, 'r');

	# get the map name
	map_file = file.readline().strip();

	# get the positions
	poses = [];
	for line in file:
		# parse the line
		timestamp, x, y, angle = [float(a) for a in line.strip().split(' ')];
		poses.append([timestamp,x,y,angle]); # just to remember the order

	# load map
	bg = cv2.imread(map_file);
	height, width = bg.shape[:2];
	blank = np.zeros_like(bg);

	# load the scans file
	scans = pickle.load(lzma.open("PLAYBACK.xz", 'rb'));

	# create dummy vehicle
	car = Vehicle();

	# DEBUG DEBUG DEBUG
	# create odom vehicle
	odom_car = Vehicle();

	# SAVING FOR GIF
	filenum = 0; # gif
	is_new = True; # gif
	save_for_gif = True;

	# play back recording
	last = time.time();
	elapsed = poses[0][0]; # first timestamp
	done = False;
	index = 0;
	while not done:
		# refresh display
		display = np.copy(blank);

		# update time
		now = time.time();
		dt = now - last;
		last = now;
		elapsed += dt;

		# get position
		if elapsed > poses[index+1][0]:
			index += 1;
			is_new = True; # DEBUG - gif
			if index >= len(poses)-1:
				index = len(poses)-2; # to allow for +1 comparison
				break; # DEBUG - break for gif

		# get current stuff
		scan = scans[index];
		scan = noise.sensorNoiseProp(scan, 0.0);

		# update ground truth car
		car.setPose(poses[index]);

		# update odometry car
		if is_new:
			if index > 0:
				# calculate current odometry
				lastPos = poses[index - 1];
				currPos = poses[index];
				turn1, move, turn2 = pm.getOdom(lastPos, currPos);

				# add noise
				turn1, move, turn2 = noise.odomNoise(turn1, move, turn2, 0.10, 0.15);

				# update odom car
				odom_car.updateOdom([turn1, move, turn2]);
			else:
				# set to starting position
				odom_car.setPose(poses[index]);

		# draw scan
		# for point in scan:
		# 	deg, dist = point;
		# 	if dist < 0.01:
		# 		continue;
		# 	x,y = pm.hitPoint(dist, deg, car.pos, car.angle);
		# 	if x >= 0 and x < width and y >= 0 and y < height:
		# 		bg[y,x] = (0,0,255);
		# 		blank[y,x] = (0,0,255);

		# 		# draw temporary line
		# 		cx, cy = car.pos;
		# 		cv2.line(display, (int(cx), int(cy)), (x,y), (100,100,100), 1);
		x,y = car.pos;
		angle = car.angle;
		pm.updateMap(blank, [x,y,angle], scan, (0,0,255), display = display);


		# draw car
		car.draw(display);
		odom_car.draw(display, color = (255,255,255));

		# show
		cv2.imshow("Display", display);
		key = cv2.waitKey(1);

		# DEBUG - save to folder for gif
		if save_for_gif:
			if is_new:
				is_new = False;
				filename = "Images/" + str(filenum).zfill(6) + ".jpg";
				filenum += 1;
				cv2.imwrite(filename, display);

		# process keys
		done = key == ord('q');
		if key == ord('d'):
			elapsed += 5.0;
		if key == ord('a'):
			elapsed -= 5.0;



if __name__ == "__main__":
	main();