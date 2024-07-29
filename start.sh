#!/bin/sh
mpg321 -q /home/pi/home-PRD/audio/start.mp3

# Start the application
cd /home/pi/home-PRD
git pull origin main
python3 app.py