#!/bin/bash
# Aliases for LArBo system commands
# Usage:
#   source env.sh

export LARBO_DIR="/home/pi/larbo/"
export LARBO_DATA_DIR="${LARBO_DIR}/data/$(date +%Y_%m_%d)"

mkdir -p $LARBO_DATA_DIR
echo "Data directory: ${LARBO_DATA_DIR}"

# Camera
alias camera-capture=". ${LARBO_DIR}/larbo-cam/capture.sh ${LARBO_DATA_DIR}"
alias camera-preview=". ${LARBO_DIR}/larbo-cam/preview.sh"
# LEDs
# alias front-led=". ${LARBO_DIR}/larbo-led/front_led.sh"
# Pressure gauge
alias pg-run="python3 ${LARBO_DIR}/larbo-pressure/collect-data.py ${LARBO_DATA_DIR}"
# RTDs
alias rtd-run="python3 ${LARBO_DIR}/larbo-rtd/collect-data.py ${LARBO_DATA_DIR}"
# Level sensor
alias levelsensor-run='python3 ${LARBO_DIR}/levelsensor/log_arduino.py -o $LARBO_DATA_DIR/LS_$(date +%Y-%m-%d_%H-%M-%S).h5'
# ADC
alias adc-run='python3 ${LARBO_DIR}/larbo-adc/collect-data.py ${LARBO_DATA_DIR}'

# Monitor
alias monitor-run='python3 ${LARBO_DIR}/larbo-monitor/monitor.py ${LARBO_DATA_DIR}'
