#!/bin/bash
# This script updates the led installed on the mezzanine for the raspberry pi
# Usage:
#   . front_led.sh [on, off, 0-100]
PIN=12

VALUE=$1

if [ $VALUE == "on" ]; then
    gpio -g mode $PIN out
    gpio -g write $PIN 1
elif [ $VALUE == "off" ]; then
    gpio -g mode $PIN out
    gpio -g write $PIN 0
else
    gpio -g mode $PIN pwm
    gpio -g pwm $PIN $(( VALUE * 1023 / 100 ))
fi
