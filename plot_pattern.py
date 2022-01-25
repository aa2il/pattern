#! /usr/bin/python3 -u
###############################################################################

# Script to plot antenna pattern meaurements

from fileio import read_csv_file
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import argparse

###############################################################################

#fname='PATTERN1.DAT'
#fname='PATTERN2.DAT'
#fname='PATTERN3.DAT'
#fname='PATTERN4.DAT'

###############################################################################

def get_values(x,key,typ=None):
    if typ==None:
        vals=[d[key] for d in data];
    elif typ=='seconds':
        vals=[d[key] for d in data];
        times=[]
        t0=None
        for t in vals:
            t=time.mktime(datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple())
            if not t0:
                t0=t
            times.append(t-t0)
        return times

    elif typ==bool:
        vals=[d[key]=='True' for d in data];
    else:
        vals=[typ(d[key]) for d in data];

    return np.array( vals )

###############################################################################

# Get file name from command line
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("fname", help="CSV file with measurements",
                      type=str,default=None)   #,nargs='*')    # '+'
args = arg_proc.parse_args()

#print('Hey1!')
fname=args.fname
print('fname=',fname)
#sys.exit(0)

# Read the data
data,hdr=read_csv_file(fname,'\t')
if 0:
    #print('')
    #print(data)
    print('')
    print('0:',data[0])
    print('')
    print('1:',data[1])
    sys.exit(0)

keys=data[0].keys()
print('\nkeys=',keys)
#print('\ndata=',data[0])
#sys.exit(0)

az = get_values(data,'Az',float)
print('az=',az[0:3])

db = get_values(data,'db',float)
print('db=',db[0:3])
db=db-max(db)

###############################################################################

fig, ax = plt.subplots()

rads=az*np.pi/180.
plt.axes(projection = 'polar')
plt.polar(rads, db,color='red')



#fig = Figure()
#ax = fig.add_subplot(111)
#ax2 = ax.twinx()
#fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True)

if 0:
    # Polar axis for sky track plot
    self.ax2 = self.fig2.add_subplot(111, projection='polar')
    self.ax2.set_rmax(90)
    self.ax2.set_yticks([0,30, 60, 90])          # Less radial ticks
    self.ax2.set_yticklabels(['90','60','30','0'])
    #self.ax2.set_rlabel_position(-22.5)  # Move radial labels away from plotted line
    self.ax2.grid(True)
    xtics = ['E','','N','','W','','S','']
    self.ax2.set_xticklabels(xtics) 

if 0:    
    # db vs az
    ax.plot(az, db,color='red')
    ax.set_xlabel('Az (deg)')
    ax.set_ylabel('db (dB)')
    fig.suptitle('Antenna Pattern Measurements')
    ax.grid(True)
    
plt.show()
