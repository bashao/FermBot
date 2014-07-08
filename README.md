FermBot
=======

This is the code for my home fermentation IR bubble sensor. 

There are three files in the project:

* OpticBubble.py - A script for counting the bubbles by the sensor and reporting them to the different logs.
* Tweet.py - A script that posts the bubbles every 15 minutes to twitter.
* Runner.py - A script that will check that OpticBubble and Tweet are running and run them again if necessery.

