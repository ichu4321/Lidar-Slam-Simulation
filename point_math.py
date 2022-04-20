import math
import cv2
import numpy as np

# rotate point
def rotate(point, angle):
	# calculate angles
	rads = math.radians(angle);
	rcos = math.cos(rads);
	rsin = math.sin(rads);

	# rotate
	x,y = point;
	rx = x * rcos - y * rsin;
	ry = x * rsin + y * rcos;
	return (int(rx), int(ry));

# translate point
def translate(p1, p2):
	x = p1[0] + p2[0];
	y = p1[1] + p2[1];
	return (int(x), int(y));


# returns scan coordinates relative to car position
def hitPoint(distance, angle, car_pos, car_angle):
	# generate base point
	point = [distance, 0];

	# rotate
	point = rotate(point, angle + car_angle);

	# translate
	point = translate(point, car_pos);
	return point;

# convert map to binary
# black = empty
# anything else = occupied
def loadMap(filename):
	# load image
	img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE);

	# mask
	_, mask = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY);
	return mask;

# load the records file
def load(filename):
	# get the map
	file = open(filename, 'r');
	map_filename = file.readline().strip();
	map_mask = loadMap(map_filename);
	map_img = cv2.imread(map_filename);

	# get the poses
	poses = [];
	for line in file:
		# parse the line and save
		poses.append([float(a) for a in line.strip().split(' ')]);
	file.close();

	# double up the first position
	poses.insert(0, poses[0]);

	return map_img, map_mask, poses;

# 2d distance between 2 points
def dist2D(p1, p2):
	x1, y1 = p1;
	x2, y2 = p2;
	dx = x1 - x2;
	dy = y1 - y2;
	return math.sqrt(dx*dx + dy*dy);

# angle from vector(a,b) to vector(b,c)
# clockwise angle
def angle3P(a, b, c):
	# get vec(ab)
	ab_x = b[0] - a[0];
	ab_y = b[1] - a[1];
	vec_ab = [ab_x, ab_y];

	# get vec(bc)
	bc_x = c[0] - b[0];
	bc_y = c[1] - b[1];
	vec_bc = [bc_x, bc_y];

	# get unit vecs
	unit_ac = vec_ac / np.linalg.norm(vec_ac);
	unit_bc = vec_bc / np.linalg.norm(vec_bc);

	# get angle
	dot = np.dot(unit_ac, unit_bc);
	angle = np.arccos(dot);
	return angle;

# get the smallest relative turning angle
def smallestTurn(turn):
	turn = turn % 360.0;
	if turn > 180.0:
		turn -= 360.0;
	return turn;

# calculate relative odometry to get to new point
# turn to point, move, turn to match angle
def getOdom(currPos, nextPos):
	# unpack
	_, cx, cy, ct = currPos;
	_, nx, ny, nt = nextPos;

	# relative movement
	move = dist2D([cx, cy], [nx, ny]);

	# first turn
	dx = nx - cx;
	dy = ny - cy;
	angle_to_point = math.degrees(math.atan2(dy, dx));
	turn1 = angle_to_point - ct;

	# second turn
	turn2 = nt - angle_to_point;

	# check special case
	if move <= 0.001:
		turn1 = 0;
		turn2 = nt - ct;

	# minimize turns
	turn1 = smallestTurn(turn1);
	turn2 = smallestTurn(turn2);
	return turn1, move, turn2;

# update map with a position and a scan
def updateMap(map_img, pose, scan, color, display = None):
	# draw scan
	cx,cy,angle = pose;
	height, width = map_img.shape[:2];
	for point in scan:
		# unpack
		deg, dist = point;
		if dist < 0.01:
			continue;

		# find hit location and draw
		x,y = hitPoint(dist, deg, [cx,cy], angle);
		if x >= 0 and x < width and y >= 0 and y < height:
			map_img[y,x] = color;

		# draw temporary line
		if display is not None:
			cv2.line(display, (int(cx), int(cy)), (x,y), (100,100,100), 1);

# update map with maxBlit
def updateMapBlur(map_img, pose, scan, blur_pattern):
	# draw scan
	cx,cy,angle = pose;
	height, width = map_img.shape[:2];
	for point in scan:
		# unpack
		deg, dist = point;
		if dist < 0.01:
			continue;

		# find hit location and draw
		x,y = hitPoint(dist, deg, [cx,cy], angle);
		maxBlit(map_img, blur_pattern, [y,x]);
		# if x >= 0 and x < width and y >= 0 and y < height:
		# 	map_img[y,x] = color;


# change scale of value from [min1, max1] -> [min2, max2]
def reframe(min1, max1, min2, max2, value):
	# change frame
	value -= min1;
	value /= (max1 - min1);
	value *= (max2 - min2);
	value += min2;

	# clamp
	value = max(min2, value);
	value = min(max2, value);
	return value;


# create blur pattern
def makeBlur(min_strength, max_strength, radius):
	# make square
	length = (radius * 2) + 1;
	blank = np.zeros((length, length), np.uint8);

	# do math on pixels
	center = [radius, radius];
	for y in range(length):
		for x in range(length):
			# calculate value
			dist = dist2D(center, [x,y]);
			dist = radius - dist;
			dist = max(dist, 0);
			value = reframe(0, radius, 0, 255, dist);

			# apply to pixel
			blank[y,x] = int(value);
	return blank;

# blit onto image (using numpy.maximum)
def maxBlit(img, blit_img, center_pos):
	# unpack
	x,y = center_pos;
	height, width = img.shape[:2];
	radius = int(blit_img.shape[0] / 2); # assume square

	# expand to blit boundaries
	left = x - radius;
	right = x + radius;
	top = y - radius;
	bottom = y + radius;

	# chop boundaries
	sx = 0;
	if left < 0:
		sx = -left;
		left = 0;

	sy = 0;
	if top < 0:
		sy = -top;
		top = 0;

	ex = 2 * radius;
	xmax = width - 1;
	if right > xmax:
		ex -= right - xmax;
		right = xmax;

	ey = 2 * radius;
	ymax = height - 1;
	if bottom > ymax:
		ey -= bottom - ymax;
		bottom = ymax;

	# chop out portions
	chop1 = img[top:bottom, left:right];
	chop2 = blit_img[sy:ey, sx:ex];

	# blit
	img[top:bottom, left:right] = np.maximum(chop1, chop2);



if __name__ == "__main__":
	# blur test
	blur = makeBlur(0, 255, 25);
	cv2.imshow("Blur", blur);
	blank = np.zeros((100,100), np.uint8);
	maxBlit(blank, blur, [0,0]);
	maxBlit(blank, blur, [100,100]);
	maxBlit(blank, blur, [50,50]);
	cv2.imshow("Blit Test", blank);

	# odom test
	print("Odom Check: ");
	print(getOdom([0, 0, 0, 20], [0, 5, 0, 0]));

	# map load test
	mask = loadMap("Maps/map.png");
	cv2.imshow("Map", mask);
	cv2.waitKey(0);
