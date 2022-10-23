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

RMIN=-30

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
print(db)

for i in range(len(db)):
    db[i]=max(db[i],RMIN)

# Fit a parabola to peak to determine where max is and how much we need to rotate plot by
n2=6
idx=np.argmax(db)
print('idx=',idx)
idx2=range( (idx-n2),(idx+n2) )
print('idx2=',idx2)
x=az[idx2]
p=np.polyfit(x,db[idx2],2)
print('p=',p)
y=p[0]*x*x + p[1]*x + p[2]
az0=-0.5*p[1]/p[0]
print('az0=',az0)
    
###############################################################################

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

theta=(az-az0)*np.pi/180.
ax.plot(theta, db,color='red')

fig, ax = plt.subplots()
ax.plot(az,db,color='red')
ax.plot(x,y,color='green')
ax.grid(True)

plt.show()
