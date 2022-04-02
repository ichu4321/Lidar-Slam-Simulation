import cv2
import time
import numpy as np

from vehicle import Vehicle

import lzma
import pickle

import point_math as pm



def main():
	# open the recording
	filename = "record.txt";
	file = open("Records/" + filename, 'r');

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
	scans =  pickle.load(lzma.open("PICKLE.xz", 'rb'));

	# create dummy vehicle
	car = Vehicle();

	# play back recording
	filenum = 0; # gif
	is_new = True; # gif
	last = time.time();
	elapsed = 0.0;
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
		# index = 0;
		ts,x,y,angle = poses[index];
		scan = scans[index];

		# update car
		car.pos = [x,y];
		car.angle = angle;

		# draw scan
		for point in scan:
			deg, dist = point;
			if dist < 0.01:
				continue;
			x,y = pm.hitPoint(dist, deg, car.pos, car.angle);
			if x >= 0 and x < width and y >= 0 and y < height:
				bg[y,x] = (0,0,255);
				blank[y,x] = (0,0,255);

				# draw temporary line
				cx, cy = car.pos;
				cv2.line(display, (int(cx), int(cy)), (x,y), (100,100,100), 1);

		# draw car
		car.draw(display);

		# show
		cv2.imshow("Display", display);
		key = cv2.waitKey(1);

		# DEBUG - save to folder for gif
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