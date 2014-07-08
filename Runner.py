__author__ = 'omer'

import os
import sys
import subprocess
import traceback
import time
from Daemon import Daemon
from Logger import Logger

class Runner(Daemon):
    TWEET_PID_NAME = "Tweet_PID"
    BUBBLE_PID_NAME = "OpticBubble_PID"
    
    def __init__(self):
        Daemon.__init__(self, pidfile="Runner_PID", stdout="runner_stdout.txt", stderr="runner_stderr.txt")
        self.logger = Logger("Runner", ".", "runner.log")
        
    def getTweetPID(self):
        try:
            tf = open(Runner.TWEET_PID_NAME, 'r')
            self.tweet_pid = int(tf.read())
            tf.close()
        except Exception:
            self.logger.log(3, "Get tweet pid failed. %s"%(traceback.format_exc()))
            return False

    def getBubblePID(self):
        try:
            tf = open(Runner.BUBBLE_PID_NAME, 'r')
            self.bubble_pid = int(tf.read())
            tf.close()
        except Exception:
            self.logger.log(3, "Get bubble pid failed. %s"%(traceback.format_exc()))
            return False
        
    def is_process_running(self, process_id):
        try:
            os.kill(process_id, 0)
            return True
        except OSError:
            return False
        
    def run(self):
        while True:
            try:
                self.getBubblePID()
                if self.bubble_pid:
                    if self.is_process_running(self.bubble_pid):
                        pass
                    else:
                        self.logger.log(1, "Bubble is not working, running again.")
                        subprocess.call(["rm", "-rf", "OpticBubble_PID"])
                        subprocess.call(["sudo", "python", "Fermentation/OpticBubble.py"])
                        
                self.getTweetPID()
                if self.tweet_pid:
                    if self.is_process_running(self.tweet_pid):
                        pass
                    else:
                        self.logger.log(1, "Tweet is not working, running again.")
                        subprocess.call(["rm", "-rf", "Tweet_PID"])
                        subprocess.call(["python", "Fermentation/Tweet.py"])
                time.sleep(30)
            except Exception:
                self.logger.log(3, "Got exception in run: %s"%traceback.format_exc())
                
                

if __name__ == "__main__":
    runner = Runner()
    runner.start()