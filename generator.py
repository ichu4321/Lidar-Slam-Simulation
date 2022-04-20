import cv2
import numpy as np

import math
import pickle
import lzma

import point_math as pm

# calculates nearest hit
def raycast(pos, angle, max_range, img):
	# create blank overlay
	blank = np.zeros_like(img);
	h,w = img.shape[:2];

	# create line
	start = pos;
	end = [max_range, 0];
	end = pm.rotate(end, angle);
	end = pm.translate(end, pos);
	# print("start: " + str(start));
	# print("end: " + str(end));

	# draw line
	cv2.line(blank, start, end, 100, 1);
	blank = cv2.add(img, blank);
	# cv2.imshow("Blank", blank);
	# cv2.waitKey(0);

	# gather hits
	hits = np.where(blank == 100);
	points = [];
	for a in range(len(hits[0])):
		x = hits[0][a];
		y = hits[1][a];
		points.append([x,y]);
	# print(points);

	# calculate squared distances
	best_distance = 0;
	best_point = None;
	for point in points:
		# squared distance
		x = (pos[0] - point[1])**2;
		y = (pos[1] - point[0])**2;
		dist = x + y;

		# compare against best
		if best_distance == 0 or best_distance > dist:
			best_distance = dist;
			best_point = point;

	return math.sqrt(best_distance);
	# return best_point;

# generates a lidar scan for each position
def generate(pixel_range, num_lasers):
	# load file
	filename = "positions.txt";
	file = open(filename, 'r');
	map_name = file.readline().strip();
	poses = [];
	for line in file:
		poses.append([float(a) for a in line.strip().split(' ')]);

	# load map
	map_img = pm.loadMap(map_name);

	# laser angles
	angles = [];
	deg = 0;
	step = 360.0 / num_lasers;
	while deg < 360.0:
		angles.append(deg);
		deg += step;

	# loop through positions
	scans = [];
	counter = 0;
	for pose in poses:
		# progress check
		counter += 1;
		print(str(counter) + " of " + str(len(poses)));

		# do a scan
		scan = [];
		ts,x,y,angle = pose;
		for deg in angles:
			dist = raycast((int(x),int(y)), angle + deg, pixel_range, map_img);
			scan.append([deg, dist]);
		scans.append(scan);

	# combine scans and poses
	color_map_img = cv2.imread(map_name);
	records = [color_map_img]; # THE FIRST ELEMENT WILL BE THE MAP IMAGE
	for a in range(len(scans)):
		scan = scans[a];
		pose = poses[a];
		records.append([pose, scan]);

	# save compressed pickle of records
	pickle.dump(records, lzma.open("PLAYBACK.xz", 'wb'));

if __name__ == "__main__":
	generate(1000, 360);