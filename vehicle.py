import cv2
import math
import numpy as np

class Vehicle:
	def __init__(self, pos = [0,0], angle = 0):
		# vehicle position
		self.pos = pos;
		self.angle = angle;

		# create vehicle points
		self.points = [
			[20,0],
			[-5,7],
			[-5,-7]
		];
		self.color = (150,200,0);

	# integer cast a point
	def intify(self, point):
		x = int(point[0] + 0.5);
		y = int(point[1] + 0.5);
		return [x,y];

	# translate points
	def translate(self, p1, p2):
		x = p1[0] + p2[0];
		y = p1[1] + p2[1];
		return [x,y];

	# rotate points
	def rotate(self, point, angle):
		# get radian rotation
		rads = math.radians(angle);
		rcos = math.cos(rads);
		rsin = math.sin(rads);
		x, y = point;

		# rotate points
		rx = x * rcos - y * rsin;
		ry = x * rsin + y * rcos;
		return [rx, ry];

	# get a display-representation of the points
	def getPoints(self):
		display_points = [];
		for point in self.points:
			point = self.rotate(point, self.angle);
			point = self.translate(point, self.pos);
			point = self.intify(point);
			display_points.append(point);
		return display_points;

	# draw self on image
	def draw(self, img):
		# get vehicle points
		draw_points = self.getPoints();
		draw_points = np.array(draw_points);

		# draw polygon
		cv2.fillPoly(img, pts = [draw_points], color = self.color);

		# draw actual center
		x, y = self.intify(self.pos);
		cv2.circle(img, (x,y), 2, (100,0,0), -1);

	# update position (move and turn should be time-adjusted)
	def update(self, move, turn):
		# turn first
		self.angle += turn;

		# update position
		point = [move, 0];
		point = self.rotate(point, self.angle);
		self.pos = self.translate(self.pos, point);
