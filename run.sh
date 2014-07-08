#!/bin/bash
sleep 30
cd /home/pi/
if [  -f /home/pi/OpticBubble_PID ]
then
  echo "File does not exist. Exiting..."
  exit 1
fi

python Fermentation/OpticBubble.py
sleep 301
python Fermentation/Tweet.py
sleep 30
python Fermentation/Runner.py