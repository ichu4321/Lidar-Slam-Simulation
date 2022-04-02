import cv2
import math
import time
import keyboard as kb
import numpy as np

from vehicle import Vehicle



def main():
	# create display
	perm = np.zeros((800,800,3), np.uint8);
	display = np.zeros_like(perm);

	# load map
	filename = "map.png";
	map_img = cv2.imread("Maps/" + filename);
	map_img = cv2.resize(map_img, (800,800));
	perm = map_img;

	# create a vehicle
	car = Vehicle([100,400], 0);

	# define stats
	move_spd = 100.0; # pixels per second
	turn_spd = 90.0; # degrees per second
	move = 0.0; # in pixels
	turn = 0.0; # in degrees

	# record time
	record_dt = 1.0 / 10; # record position N times per second
	record_timer = 0.0;
	record = [];

	# display loop
	done = False;
	last = time.time();
	elapsed = 0.0;
	while not done:
		# refresh display
		display = np.copy(perm);

		# update timestep
		now = time.time();
		dt = now - last;
		last = now;
		elapsed += dt;

		# update car
		car.update(move * dt, turn * dt);
		move = 0.0;
		turn = 0.0;

		# draw car
		car.draw(display);

		# record position
		record_timer += dt;
		if record_timer >= record_dt:
			record_timer = 0.0;
			x, y = car.pos;
			angle = car.angle;
			record.append([elapsed,x,y,angle]);

		# show
		cv2.imshow("Display", display);
		key = cv2.waitKey(1);

		# process keys
		done = key == ord('q');
		# move
		if kb.is_pressed('w'):
			move = move_spd;
		if kb.is_pressed('s'):
			move = -move_spd;
		# turn
		if kb.is_pressed('d'):
			turn = turn_spd;
		if kb.is_pressed('a'):
			turn = -turn_spd;

	# make record of position
	file = open("record.txt", 'w');
	file.write("Maps/" + filename + "\n");
	for item in record:
		outstr = "";
		for elem in item:
			outstr += str(elem) + " ";
		outstr = outstr.strip() + "\n";
		file.write(outstr);
	file.close();




if __name__ == "__main__":
	main();