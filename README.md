FermBot
=======

This is the code for my home fermentation IR bubble sensor. 

There are three files in the project:

* OpticBubble.py - A script for counting the bubbles by the sensor and reporting them to the different logs.
* Tweet.py - A script that posts the bubbles every 15 minutes to twitter.
* Runner.py - A script that will check that OpticBubble and Tweet are running and run them again if necessery.

In order to run the system you need to have a raspberry pi with all the hardware connected to it (Comming soon):
* I2C enabled - https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c
* Twitter account with developer app - http://www.makeuseof.com/tag/how-to-build-a-raspberry-pi-twitter-bot/
* Connect to the raspberri pi with ssh and:
** Run mkdir ~/Fermentation
** Run mkdir ~/Fermentation/stats2
** Put all the files in the Fermentation library
** Set variables for twitter consumer key, consumer secret, etc. and the temprature probe id.

Now you need to run the system, connect to the raspberry pi with ssh and:
* Run sudo python Fermentation/OpticBubble.py
* Wait for 5 minutes to get one file in the stats2 directory
* Run python Fermentation/Tweet.py
* Run sudo python Fermentation/Runner.py

Now there will be many files for the PID, stdout and stderr for every process in the home directory and inside the Fernetation directory there will be three files for the logs for one, five and fifteen minute intervals. You can downlad those files after the fermentaiton is done and analyse the data in excel or any app of your choise.


