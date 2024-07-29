#!/bin/bash
cd /home/pi/home-PRD
git pull origin main
python3 /home/pi/home-PRD/ip_addr.py
#python3 app.py