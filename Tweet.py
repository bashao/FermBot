from temperature import Temperature
import os
import traceback
import pickle
import time
import subprocess
from twython import Twython
from Daemon import Daemon
from Logger import Logger

class Tweet(Daemon):
    #Temp vars
    DEVICESDIR = "/sys/bus/w1/devices/"
    TEMP_SENSOR_FILE = os.path.join(DEVICESDIR, "28-00000xxxxxxx", "w1_slave")
    
    #Twitter vars   
    CONSUMER_KEY = 'xxxxxxxxxxxxxxxxxxxxx'
                       
    CONSUMER_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ACCESS_KEY = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    ACCESS_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    def __init__(self):
        Daemon.__init__(self, pidfile="Tweet_PID", stdout="tweet_stdout.txt", stderr="tweet_stderr.txt")
        self.twitter = Twython(Tweet.CONSUMER_KEY, Tweet.CONSUMER_SECRET, Tweet.ACCESS_KEY, Tweet.ACCESS_SECRET)
        self.last = ""
        self.count = 1
        subprocess.call(["sudo", "modprobe", "w1-gpio"])
        subprocess.call(["sudo", "modprobe", "w1-therm"])
        self.logger = Logger("Tweet", ".", "tweet.log")
        

    def readTempFile(self):
        try:
            sensorFile = open(Tweet.TEMP_SENSOR_FILE, "r")
            lines = sensorFile.readlines()
            sensorFile.close()
        except Exception, exc:
            self.logger.log(3, "Got exception in reading temperature file: %s"%traceback.format_exc())
            return ""
        return lines
    
    def getTemp(self):
        data = self.readTempFile()
        #the output from the tempsensor looks like this
        #f6 01 4b 46 7f ff 0a 10 eb : crc=eb YES
        #f6 01 4b 46 7f ff 0a 10 eb t=31375
        #has a YES been returned?
        if data[0].strip()[-3:] == "YES":
            #can I find a temperature (t=)
            equals_pos = data[1].find("t=")
            if equals_pos != -1:
                tempData = data[1][equals_pos+2:]
                #update temperature
                temperature = Temperature(tempData)
                #self.logger.log(1, "Temperature is %f"%(temperature.C))
                return temperature
            else:
                return False
        else:
            return False
            
    def run(self):
        lastFile = ""
        while sorted(os.walk("Fermentation/stats2/").next()[2])[-1] != lastFile:
            try:
                lastFile = sorted(os.walk("Fermentation/stats2/").next()[2])[-1]
                bubbles = map(lambda f:pickle.load(open("Fermentation/stats2/"+f)),sorted(os.walk("Fermentation/stats2/").next()[2]))
                recentFifteen = sum(bubbles[-3:])
                recentHour = float(sum(bubbles[-12:]))/4
                recentDay = float(sum(bubbles[-288:]))/(float(len(bubbles[-288:]))/3)
                hourText = (recentFifteen >= recentHour) and "+%.01f"%(recentFifteen-recentHour) or "-%.01f"%(recentHour-recentFifteen)
                dayText = (recentFifteen >= recentDay) and "+%.01f"%(recentFifteen-recentDay) or "-%.01f"%(recentDay-recentFifteen)
                temp = self.getTemp()
                if temp:
                    temp = temp.C
                    statusPub="Beer bubbled %d times in the last 15 minutes! (%s hourly, %s daily) Beer temperature is: %f. %d"%(recentFifteen, hourText, dayText, temp, self.count)
                    print statusPub
                    if self.last != statusPub:
                        self.twitter.update_status(status=statusPub)
                        self.last = statusPub
                else:
                    statusPub="Beer bubbled %d times in the last 15 minutes! (%s hourly, %s daily) Can't get temperature. %d"%(recentFifteen, hourText, dayText, self.count)
                    print statusPub
                    if self.last != statusPub:
                        self.twitter.update_status(status=statusPub)
                        self.last = statusPub
                self.count += 1
                time.sleep(15*60)
            except Exception, exc:
                print "Got exception %s"%(traceback.format_exc())
                self.twitter = Twython(Tweet.CONSUMER_KEY, Tweet.CONSUMER_SECRET, Tweet.ACCESS_KEY, Tweet.ACCESS_SECRET)
                continue
            finally:
                #tempcontrol.stopController()
                #tempcontrol.join()
                print "Done"
        
if __name__ == "__main__":
    tweet = Tweet()
    tweet.start()
