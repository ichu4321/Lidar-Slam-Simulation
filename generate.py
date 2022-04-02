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
def main():
	# load file
	filename = "record.txt";
	file = open("Records/" + filename, 'r');
	map_name = file.readline().strip();
	poses = [];
	for line in file:
		ts,x,y,angle = [float(a) for a in line.strip().split(' ')];
		poses.append([x,y,angle]);

	# load map
	map_img = cv2.imread(map_name, cv2.IMREAD_GRAYSCALE);

	# DEBUG CAST
	# raycast((400,400), 0, 400, map_img);
	
	# laser angles
	angles = [];
	for deg in range(0,360,2):
		angles.append(deg);

	# loop through positions
	scans = [];
	counter = 0;
	for pose in poses:
		# DEBUG DEBUG DEBUG
		# copy = np.copy(map_img);

		# progress check
		counter += 1;
		print(str(counter) + " of " + str(len(poses)));

		# do a scan
		scan = [];
		x,y,angle = pose;
		for deg in angles:
			dist = raycast((int(x),int(y)), angle + deg, 400, map_img);
			scan.append([deg, dist]);

			# DEBUG DEBUG DEBUG
			# px,py = pm.hitPoint(dist, deg, [x,y], angle);
			# copy[py,px] = 100;

		scans.append(scan);

		# DEBUG DEBUG
		# cv2.imshow("Debug", copy);
		# cv2.waitKey(0);

	# save pickle
	pickle.dump(scans, lzma.open("PICKLE.xz", 'wb'));

	# load pickle and check
	# loaded_scans = pickle.load(lzma.open("PICKLE.xz", 'rb'));

if __name__ == "__main__":
	main();