#!/bin/bash

echo "==============================="
echo "|| Starting pigpio daemon... ||"
echo "==============================="
sudo killall pigpiod
sudo pigpiod

echo "============================="
echo "|| Buidling C++ Program... ||"
echo "============================="
cd /home/pi/Repos/ECE477/laser_detector/rel/build; make;

echo "==================================="
echo "|| Done! Starting Main Program...||"
echo "==================================="
#/home/pi/Repos/ECE477/laser_detector/rel/Main.py -p 9595 -r 1280 720
/home/pi/Repos/ECE477/laser_detector/rel/Main.py -p 9595 -v