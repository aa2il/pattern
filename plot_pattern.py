#! /usr/bin/python3 -u
###############################################################################
#
# Script to plot antenna pattern meaurements
#
# 
#    plot_pattern.py PATTERN_2m_6x6_OWA_Yagi.DAT -nec owa_yagi_6el_circ.out
#
###############################################################################

import os
import sys
from fileio import read_csv_file
from datetime import datetime
import time
import numpy as np
import matplotlib.pyplot as plt
import argparse
import matplotlib.pyplot as plt

###############################################################################

RMIN=-30
#DIR_NAME = '~/.wine/drive_c/4nec2/out'
DIR_NAME = './'

###############################################################################

# Get file name from command line
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("fname", help="CSV file with measurements",
                      type=str,default=None)   #,nargs='*')    # '+'
arg_proc.add_argument("-nec", help="4Nec2 Output File",
                      type=str,default=None)
args = arg_proc.parse_args()

################################################################################

# Function to locate next line containing a string
def find_next(fp,str):
    while True:
        line = fp.readline()
        if not line or str in line:
            return line

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

# Function to read the NEC output file
def read_nec(fname):
    
    print('fname=',fname)
    first_time=True
    with open(fname) as fp:
        while True:
            line = find_next(fp,'- - - - - - FREQUENCY - - - - - -')
            if not line:
                break
            
            line = find_next(fp,'- - - RADIATION PATTERNS - - -')
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()

            theta=[]
            phi=[]
            gain=[]
            vgain=[]
            hgain=[]
            line = fp.readline()
            a=line.split()
            gain_max=-1e38
            while len(a)>0:
                print(a)
                t=float(a[0])
                theta.append(t)
                p=float(a[1])                
                phi.append(p)
                g=max(float(a[2]),-15)
                vgain.append(g)
                g=max(float(a[3]),-15)
                hgain.append(g)
                g=float(a[4])
                gain.append(g)
                if g>gain_max:
                    gain_max=g
                    theta_best=t
                    phi_best=p

                line = fp.readline()
                a=line.split()
                
            print('\nMax Gain=',gain_max,'\tat Theta=',theta_best,'\tPhi=',phi_best,'\n')

            theta2=[]
            gain2=[]
            hgain2=[]
            vgain2=[]
            phi_best2=np.mod(phi_best+180.,360.)
            print(phi_best,phi_best2)
            for i in range(len(gain)):
                if phi[i]==phi_best:
                    theta2.append(np.mod(theta[i]+90,360.)*np.pi/180.)
                    gain2.append(gain[i]-gain_max)
                    hgain2.append(hgain[i])
                    vgain2.append(vgain[i])
                    print(i,theta[i],phi[i],gain[i])
                elif phi[i]==phi_best2:
                    theta2.append(np.mod(theta[i]+90-180,360.)*np.pi/180.)
                    gain2.append(gain[i]-gain_max)
                    hgain2.append(hgain[i])
                    vgain2.append(vgain[i])
                    print(i,theta[i],phi[i],gain[i])

    return np.array(theta2) , np.array(gain2)

###############################################################################

print("\n\n***********************************************************************************")
print("\nPlot Pattern  ...")

if args.nec:
    fname_nec = os.path.expanduser(DIR_NAME+'/'+args.nec)
    theta2,gain2=read_nec(fname_nec)
else:
    gain2=[]

fname=args.fname
print('fname=',fname)
#sys.exit(0)

# Read the measuremnt data
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
if len(gain2)>0:
    ax.plot(theta2, gain2,color='green')

fig, ax = plt.subplots()
ax.plot(az,db,color='red')
ax.plot(x,y,color='blue')
#if len(gain2)>0:
#    ax.plot(theta2*180./np.pi, gain2,color='green')
ax.grid(True)

plt.show()
