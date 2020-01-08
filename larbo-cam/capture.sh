#!/bin/bash
# This script automatically takes N full quality images separated by T
# milliseconds
# Usage:
#  . capture.sh <outdir> <N> <T>

N_IMAGES="${2}"
DT="${3}"
DATA_DIR=${1}/img_$(date +%H_%M_%S)/
extra_args=''
if [ ! -z "$4" ]; then
    extra_args="$4"
fi

echo 'Prepping for capture...'
mkdir -p $DATA_DIR

raspistill -o ${DATA_DIR}/%d.jpg -bm -tl $DT -t $(( DT * N_IMAGES )) -v -drc high -a $(( 12+512+1024 )) -mm matrix $extra_args

echo 'Done with capture!'
