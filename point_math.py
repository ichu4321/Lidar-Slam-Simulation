import math
import cv2

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

if __name__ == "__main__":
	# odom test
	print("Odom Check: ");
	print(getOdom([0, 0, 0, 20], [0, 5, 0, 0]));

	# map load test
	mask = loadMap("Maps/map.png");
	cv2.imshow("Map", mask);
	cv2.waitKey(0);

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