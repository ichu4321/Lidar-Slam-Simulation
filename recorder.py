import cv2
import math
import time
import keyboard as kb
import numpy as np

from vehicle import Vehicle



def record(mapfile):
	# load map;
	map_img = cv2.imread(mapfile);
	perm = map_img;

	# create display
	display = np.zeros_like(perm);

	# create a vehicle
	car = Vehicle([100,400], 0);

	# define stats
	move_spd = 100.0; # pixels per second
	turn_spd = 90.0; # degrees per second
	move = 0.0; # in pixels
	turn = 0.0; # in degrees

	# record time
	record_dt = 1.0 / 20; # record position N times per second
	record_timer = 0.0;
	record = [];

	# display loop
	recording = False;
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
		if recording:
			color = (0,200,0);
		else:
			color = (0,0,200);
		car.draw(display, color = color);

		# record position
		if recording:
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
		# toggle recording
		if kb.is_pressed('r'):
			recording = True;

	# make record of position
	file = open("positions.txt", 'w');
	file.write(mapfile + "\n");
	for item in record:
		outstr = "";
		for elem in item:
			outstr += str(elem) + " ";
		outstr = outstr.strip() + "\n";
		file.write(outstr);
	file.close();

	# close opencv windows
	cv2.destroyAllWindows();




if __name__ == "__main__":
	record("Maps/scribbles.png");