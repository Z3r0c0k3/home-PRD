#!/bin/bash
cd /home/pi/home-PRD
git restore .
git pull origin main
python3 /home/pi/home-PRD/ip_addr.py
python3 /home/pi/home-PRD/nuclear.py
#python3 app.py