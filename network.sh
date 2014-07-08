#!/bin/bash
sleep 120
cd /home/pi/
./run.sh
while true ; do
   if ifconfig wlan0 | grep -q "inet addr:" ; then
        echo "all ok"
      sleep 60
   else
      echo "Network connection down! Attempting reconnection."
        reboot
   fi
done