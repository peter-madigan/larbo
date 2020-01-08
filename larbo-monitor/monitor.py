
from h5py import File
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as md
from glob import glob
import os
import datetime
import time
import json
import numpy as np
from fnmatch import fnmatch

from data_logging import file_locking

def get_most_recent(directory, matching='*'):
    files = glob(os.path.join(directory, matching))
    if files:
        modified = list(map(os.path.getmtime, files))
        recent_file = max(enumerate(files), key=lambda x: modified[x[0]])
        return recent_file[1]
    return None

@file_locking
def plot_ls_disc(filename, thresholds=None):
    x = []
    y = []
    with File(filename,'r') as infile:
        x = infile['timestamp'][:]
        y = infile['dP0P1_v'][:]
    fig = plt.figure('Discrete LS')
    if not len(x) or not len(y):
        return fig
    fig.clf()

    fig, ax = plt.subplots(1,1,num='Discrete LS')
    loc = md.AutoDateLocator()
    fmt = md.AutoDateFormatter(loc)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)

    x = list(map(datetime.datetime.fromtimestamp, x))
    ax.plot(x, y, 'b.')
    ax.grid(b=True, which='major', alpha=0.75)
    ax.grid(b=True, which='minor', alpha=0.25)
    ax.set_ylabel('Bias voltage [V]')
    fig.tight_layout()

    if thresholds:
        for threshold in thresholds:
            ax.plot(x, [threshold]*len(x), 'r--')

    plt.draw()
    return fig

@file_locking
def plot_pg(filename):
    x = []
    y = []
    y_max = []
    y_min = []
    with File(filename,'r') as infile:
        x = infile['timestamp'][:]
        y = infile['pressure'][:]
        y_max = infile['pressure_max'][:]
        y_min = infile['pressure_min'][:]
    fig = plt.figure('Pressure gauge')
    fig.clf()
    if not len(x) or not len(y):
        return fig
    fig, ax = plt.subplots(1,1,num='Pressure gauge')
    loc = md.AutoDateLocator()
    fmt = md.AutoDateFormatter(loc)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)

    x = list(map(datetime.datetime.fromtimestamp, x))
    ax.plot(x, y, 'b.')
    ax.plot(x, y_max, 'b--', alpha=0.2)
    ax.plot(x, y_min, 'b--', alpha=0.2)
    ax.grid(b=True, which='major', alpha=0.75)
    ax.grid(b=True, which='minor', alpha=0.25)
    ax.set_ylabel('Chamber pressure [psi]')
    fig.tight_layout()

    plt.draw()
    return fig

@file_locking
def plot_rtd(filename):
    x = []
    y = []
    with File(filename,'r') as infile:
        x = infile['timestamp'][:]
        y = infile['temperature'][:]
    fig = plt.figure('RTD')
    fig.clf()
    if not len(x) or not len(y):
        return fig
    fig, ax = plt.subplots(1,1,num='RTD')
    loc = md.AutoDateLocator()
    fmt = md.AutoDateFormatter(loc)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)

    x = list(map(datetime.datetime.fromtimestamp, x))
    ax.plot(x, y, 'r.')
    ax.grid(b=True, which='major', alpha=0.75)
    ax.grid(b=True, which='minor', alpha=0.25)
    ax.set_ylabel('RTD temperature [C]')
    fig.tight_layout()

    plt.draw()
    return fig

def plot_ls(filename, filter=1100, calib=None):
    x = []
    y = []
    yerr = []
    with File(filename,'r') as infile:
        x = infile['measurements'][:,0]
        y = infile['measurements'][:,1]
        yerr = infile['measurements'][:,2]
    if filter:
        good_data = (y < filter)
        x = x[good_data]
        y = y[good_data]
        yerr = yerr[good_data]
    fig = plt.figure('Level sensor')
    fig.clf()
    if not len(x) or not len(y) or not len(yerr):
        return fig
    fig, ax = plt.subplots(1,1,num='Level sensor')
    loc = md.AutoDateLocator()
    fmt = md.AutoDateFormatter(loc)
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(fmt)

    x = list(map(datetime.datetime.fromtimestamp, x))
    ax.errorbar(x, y, yerr, fmt='g.')
    ax.grid(b=True, which='major', alpha=0.75)
    ax.grid(b=True, which='minor', alpha=0.25)
    ax.set_ylabel('RC rise time [$\mu$s]')

    if calib:
        ax2 = ax.twinx()
        ax2.set_ylabel('Liquid level [cm]')
        ax2.plot(x, list(map(lambda x: (x - calib[0])*calib[1], y)), alpha=0)

    fig.tight_layout()
    plt.draw()
    return fig

def update_plot(directory, matches, last_updated, plot_method, filename=None, **kwargs):
    if not filename or not fnmatch(filename, matches):
        filename = get_most_recent(directory, matches)
    else:
        filename = os.path.join(directory, filename)
    if not filename:
        return None
    if not last_updated or last_updated < os.path.getmtime(filename):
        print('Updating from {}...'.format(filename))
        plot_method(filename=filename, **kwargs)
    return os.path.getmtime(filename)

def refresh_plots(interval):
    manager = plt._pylab_helpers.Gcf.get_active()
    if manager is not None:
        canvas = manager.canvas
        if canvas.figure.stale:
            canvas.draw_idle()
        canvas.start_event_loop(interval)
    else:
        time.sleep(interval)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', help='The data directory to monitor')
    parser.add_argument('--file','-f', default=None, help='''File to load within directory (optional)''')
    parser.add_argument('--refresh_rate', type=float, default=5, help='How often to check '
        'for updated data files in sec')
    parser.add_argument('--ls_calib_0', type=float, default=963, help='Calibration offset '
        'for level sensor')
    parser.add_argument('--ls_calib_1', type=float, default=0.153, help='Calibration scale '
        'for level sensor')
    parser.add_argument('--ls_disc_thresholds', type=json.loads, default=[1.466,1.489,1.509,1.528], help='''Thresholds for discrete level sensor (json formatted list)''')

    args = parser.parse_args()
    plt.ion()

    last_updated = {
        'LS': None,
        'LS_DISC': None,
        'RTD': None,
        'PG': None,
    }
    while True:
        last_updated['LS_DISC'] = update_plot(args.dir, 'ADC*.h5', last_updated['LS_DISC'],plot_ls_disc, filename=args.file, thresholds=args.ls_disc_thresholds)
        try:
            last_updated['LS'] = update_plot(args.dir, 'LS*.h5', last_updated['LS'], plot_ls, filename=args.file, calib=(args.ls_calib_0, args.ls_calib_1))
        except:
            pass
        last_updated['RTD'] = update_plot(args.dir, 'RTD*.h5', last_updated['RTD'], plot_rtd, filename=args.file)
        last_updated['PG'] = update_plot(args.dir, 'PG*.h5', last_updated['PG'], plot_pg, filename=args.file)

        print('Last checked: {}'.format(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),end='\r')
        refresh_plots(args.refresh_rate)

