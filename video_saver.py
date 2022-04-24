import cv2
import numpy as np

class VideoSaver:
	def __init__(self, video_name, fps = 20, width = 800, height = 800):
		fourcc = cv2.VideoWriter_fourcc(*'mp4v');
		self.writer = cv2.VideoWriter(video_name, fourcc, fps, (width, height));
		# self.writer = cv2.VideoWriter("HELLO.mp4", fourcc, 10, (800,800));

	# close the video file
	def close(self):
		self.writer.release();

	# write an image to the video
	def write(self, image):
		self.writer.write(image);