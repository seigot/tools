#!/usr/bin/python3
#-*- coding: utf-8 -*-

# $ sudo pip3 install adafruit-ads1x15
import Adafruit_ADS1x15
import time

CHANNEL = 0
GAIN = 1

adc = Adafruit_ADS1x15.ADS1015()

while True:
    print(adc.read_adc(CHANNEL, gain=GAIN))
    time.sleep(0.5)
