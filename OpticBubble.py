__author__ = 'bashao'

import os
import sys
import time
import random
import pickle
import smbus
import time
from temperature import Temperature
import RPi.GPIO as GPIO
import subprocess
import traceback
from Daemon import Daemon
from Logger import Logger

class OpticBubble(Daemon):
    #Temp vars
    DEVICESDIR = "/sys/bus/w1/devices/"
    TEMP_SENSOR_FILE = os.path.join(DEVICESDIR, "28-00000589c320", "w1_slave")

    def __init__(self):
        Daemon.__init__(self, pidfile="OpticBubble_PID", stdout="bubble_stdout.txt", stderr="bubble_stderr.txt")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(17, GPIO.OUT)
        self.bus = smbus.SMBus(1)

        subprocess.call(["sudo", "modprobe", "w1-gpio"])
        subprocess.call(["sudo", "modprobe", "w1-therm"])
        self.logger = Logger("OpticBubble", ".", "bubble.log")

        self.oneTime = 0
        self.fiveTime = 0
        self.fithteenTime = 0.0
        self.oneMinStats = 0
        self.fiveMinStats = 0
        self.fithteenMinStats = 0
        self.oneT = time.time()
        self.fiveT = time.time()
        self.fithteenT = time.time()
        self.oneFile = open("Fermentation/OneMinLog.tsv", 'a')
        self.fiveFile = open("Fermentation/FiveMinLog.tsv", 'a')
        self.fithteenFile = open("Fermentation/FithteenMinLog.tsv", 'a')


    def readTempFile(self):
        try:
            sensorFile = open(OpticBubble.TEMP_SENSOR_FILE, "r")
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
        aout = 0
        t = 0
        hist = []
        rhist = []
        norm = 0
        inBubble = False

        fiveMinStats = 0
        t = time.time()
        while True:
            try:
                for a in range(0,4):
                    aout = aout + 1
                    self.bus.write_byte_data(0x48,0x40 | ((a+1) & 0x03), aout)
                    t = self.bus.read_byte(0x48)
                    if(a == 3):
                        hist.append(t)
                        rhist.append(t)
                        hist = hist[-1000:]
                        rhist = rhist[-5:]
                        norm = float(sum(hist))/len(hist)
                        rnorm = float(sum(rhist))/len(rhist)
                        if(abs(rnorm - norm) > 40) and not inBubble:
                            inBubble = True
                            print "ding " + str(abs(rnorm - norm))
                            self.fiveMinStats += 1
                            self.fithteenMinStats += 1
                            self.oneMinStats += 1
                            fiveMinStats += 1
                            GPIO.output(17, True)
                        elif abs(rnorm - norm) <= 20:
                            GPIO.output(17, False)
                            inBubble = False
                if time.time()-self.oneT >= 60:
                    temp = self.getTemp()
                    if temp:
                        temp = temp.C
                    else:
                        temp = float(-100)
                    line = "%f\t%d\t%f\n"%(self.oneTime, self.oneMinStats, temp)
                    self.logger.log(1, line)
                    self.oneFile.write(line)
                    self.oneFile.flush()
                    self.oneTime += 1
                    self.oneMinStats = 0
                    self.oneT = time.time()

                if time.time()-self.fiveT >= 300:
                    temp = self.getTemp()
                    if temp:
                        temp = temp.C
                    else:
                        temp = float(-100)
                    pklFile = "Fermentation/stats2/" + str(time.time()) + ".pkl"
                    self.logger.log(1, "Dumping %d to %s"%(self.fiveMinStats, pklFile))
                    line = "%d\t%d\t%f\n"%(self.fiveTime, self.fiveMinStats, temp)
                    pickle.dump(self.fiveMinStats,open(pklFile,'w'))
                    self.logger.log(1, "Done writing pickle, about to write to 5 min file: %s"%(line))
                    self.fiveFile.write(line)
                    self.fiveFile.flush()
                    self.fiveTime += 1
                    self.fiveMinStats = 0
                    self.fiveT = time.time()

                if time.time()-self.fithteenT >= 900:
                    temp = self.getTemp()
                    if temp:
                        temp = temp.C
                    else:
                        temp = float(-100)
                    line = "%f\t%d\t%f\n"%(self.fithteenTime, self.fithteenMinStats, temp)
                    self.logger.log(1, line)
                    self.fithteenFile.write(line)
                    self.fithteenFile.flush()
                    self.fithteenTime += 0.25
                    self.fithteenMinStats = 0
                    self.fithteenT = time.time()
            except Exception, e:
                    print "Unexpected error: ", sys.exc_info()[0]
                    self.logger.log(3, traceback.format_exc())

if __name__ == "__main__":
    bubble = OpticBubble()
    bubble.start()
