#!/bin/bash
# This script starts running the camera in preview mode
# Connect to vnc (drizzle.local:5900) to view
# crtl-C to exit
# Usage:
#  . preview.sh <zoom, optional>

w=1
h=1
x=0
y=0
if [ ! -z $1 ]; then
	zoom=$1
	scale="scale=scale(0.0001);"
	w=$(echo "$scale 1/$zoom" | bc)
	h=$(echo "$scale 1/$zoom" | bc)
	x=$(echo "$scale (1-$w)/2" | bc)
	y=$(echo "$scale (1-$h)/2" | bc)
	echo "using roi $x,$y,$w,$h"
fi
extra_args=''
if [ ! -z "$2" ]; then
        extra_args="$2"
fi

echo "ctl-C to exit"
eval raspivid -t 0 -k -f -roi $x,$y,$w,$h -drc high -a $(( 12+512+1024 )) -mm matrix "$extra_args"
