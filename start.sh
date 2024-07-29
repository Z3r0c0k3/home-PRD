#!/bin/bash
git pull origin main
python3 /home/pi/home-PRD/ip_addr.py
cd /home/pi/home-PRD
python3 app.py