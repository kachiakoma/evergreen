#!/usr/bin/env python

# GPIO code written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

# wind_speed def written by Adam Garcia and Jared Selby for Texas State University Project 
# Evergreen, 2017, intended for use with a Handan Qing Sheng Electronic Technology Co, Ltd 
# QS-FS-A3 wind speed sensor type 485A

import time
import os
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
DEBUG = 1

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 11 #Using t-cobbler plus -> setting pin 11 for SPICLK
SPIMISO = 9 #Using t-cobbler plus -> setting pin 9 for SPIMISO
SPIMOSI = 10 #Using t-cobbler plus -> setting pin 10 for SPIMOSI
SPICS = 8 #Using t-cobbler plus -> setting pin 8 for SPICS
 

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# This sets the value for the MCP3008 ADC Channel 0 input to be used for the anemometer signal
anemometer_adc = 0;

an2dig = 5.0/1024.0 # quantization of 5 volts reference to 2^10 bits
windSpeed = 0       # declare wind speed variable

def wind_speed():
        # read the anemometer
        anemometer = readadc(anemometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
        # experimentally derived slope coefficient
        windSpeed = (anemometer * an2dig) * 3.23198
        # if wind speed is below 0.2, the device is off
        if(windSpeed < 0.2):
            windSpeed = 0
        # return wind speed to function that called it
        return windSpeed
