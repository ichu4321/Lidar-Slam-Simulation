import math

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