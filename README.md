# Lidar-Slam-Simulation
A simple simulator for learning/testing SLAM concepts. 

SLAM is a class of algorithms used to construct maps of unknown environments based on sensor data. This simulator allows the use of arbitrary maps (I drew mine in Paint) and will save playback files so that various SLAM algorithms can be tested and tweaked to see how they perform. The playback program allows noise to be added to the odometry and sensor data during playback to help test the robustness of the algorithms used.

Blue is ground-truth, red is ded reckoning with noisy odometry, green is the SLAM-corrected position

https://user-images.githubusercontent.com/15332250/164997964-375461f9-d551-4374-9038-3d584d919bb4.mp4

# How to Use
## Generate a Playback File
Edit the "map_file" name in "make_playback.py" to match the path to the map image you want to use.
run "make_playback.py"
  - use WASD to drive the vehicle
  - press 'r' to start recording movement
  - press 'q' to end the recording
The program will run through the recorded positions and generate lidar scans for each position. Once it is finished, everything will be saved to "PLAYBACK.xz"

## Test SLAM
run "test_slam.py" to test out the slam algorithm against the playback file.
This will run with whatever the current slam algorithm is set to and will generate a "slam_map.png" image at the end representing the map it created.

## Test Localization-only
SLAM algorithms can trade off accuracy for speed. For environments that don't change too much; it can be acceptable to run a slow, expensive SLAM algorithm offline to generate a map and then run a faster localization algorithm while guiding a vehicle. This is especially useful on embedded systems where the available CPU is limited. 

In this case, the localization algorithm can be tested by running "test_localization.py" and it can be supplied the map generated from "test_slam.py"

# Trying Your Own Algorithms
The currently supplied SLAM algorithm is just a random walk (a very simple gradient descent). It is very simple and easy to adjust for either greater accuracy or speed which made it easy to use for both the slam and localization test. That being said, this is just a simple example to show the framework and I wouldn't recommend using it for SLAM (though it's surprisingly good for localization). The base class "SLAMMER" is in "solution.py" along with the random walk algorithm. Implementing a new class that inherits from SLAMMER is enough for it to be directly swappable in "test_slam.py" and "test_localization.py". The class must implement the update function which should return the new position of the vehicle and update its internal representation of the map.
