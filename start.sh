#!/bin/sh
echo "Starting "

# Start the application
cd /home/pi/MAKE-AMS-pi
git pull
python3 app.py