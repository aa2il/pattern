#! /usr/bin/python3

#    Program to digest output file from 4nec2

################################################################################

import sys
import datetime
import argparse
import time
import csv
from math import log10
import matplotlib.pyplot as plt
import numpy as np
import os

################################################################################

# User params
DIR_NAME = '~/.wine/drive_c/4nec2/out'
Zo=50

################################################################################

# Function to locate next line containing a string
def find_next(fp,str):
    while True:
        line = fp.readline()
        if not line or str in line:
            return line

################################################################################

# Process command line args
arg_proc = argparse.ArgumentParser()
arg_proc.add_argument("-i", help="4Nec2 Output File",
                      type=str,default="owa_yagi_6el_circ.out")
arg_proc.add_argument('-swr', action='store_true',
                      help='Find SWR Info')
arg_proc.add_argument('-pattern', action='store_true',
                      help='Find PATTERN Info')
args = arg_proc.parse_args()

fname = os.path.expanduser(DIR_NAME+'/'+args.i)

################################################################################

print("\n\n***********************************************************************************")
print("\nStarting 4NEC2 reader  ...")

# Open output CSV file
fp1=open('nec.csv','w')
writer = csv.writer(fp1)
writer.writerow(['4NEC2 Output file:',fname])
writer.writerow(['Zo:',Zo])
writer.writerow([])

# Read the NEC output file
print('fname=',fname)
first_time=True
with open(fname) as fp:
    while True:
        line = find_next(fp,'- - - - - - FREQUENCY - - - - - -')
        if not line:
            break

        print(line.strip())
        line = fp.readline()
        line = fp.readline()
        a=line.strip().split()
        frq = float(a[1])
        print(a,frq)
            
        if args.swr:
            #          1         2         3         4         5         6         7         8         9
            #012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
            #     2    61 1.00000E+00 0.00000E+00 2.10772E-02 4.54485E-03 4.53366E+01-9.77586E+00 2.10772E-02 4.54485E-03 1.05386E-02
            line = find_next(fp,'- - - ANTENNA INPUT PARAMETERS - - -')
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            Z=complex( float(line[60:72]) , float(line[72:84]) )
            print(line,Z)

            # Compute SWR
            Gamma = (Z-Zo) / (Z+Zo)           # Reflection coeff
            G     = abs(Gamma)
            SWR   = (1+G)/(1-G)               # VSWR
            RL    = -20*log10(G)              # Return loss = Pwr Incident - Pwr Reflected

            # Write out CSV file
            if first_time:
                writer.writerow(['Freq (MHz)','Re Z','Im Z','VSWR','RL (dB)'])
                first_time=False
            writer.writerow([frq,Z.real,Z.imag,SWR,RL])

        if args.pattern:
            line = find_next(fp,'- - - RADIATION PATTERNS - - -')
            line = fp.readline()
            line = fp.readline()
            line = fp.readline()
            writer.writerow(line.split())
            line = fp.readline()
            writer.writerow(line.split())

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
                writer.writerow(a)

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
                    gain2.append(gain[i])
                    hgain2.append(hgain[i])
                    vgain2.append(vgain[i])
                    print(i,theta[i],phi[i],gain[i])
                elif phi[i]==phi_best2:
                    theta2.append(np.mod(theta[i]+90-180,360.)*np.pi/180.)
                    gain2.append(gain[i])
                    hgain2.append(hgain[i])
                    vgain2.append(vgain[i])
                    print(i,theta[i],phi[i],gain[i])

fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})

#ax.plot(theta2, hgain2,color='red')
#ax.plot(theta2, vgain2,color='blue')
ax.plot(theta2, gain2,color='green')

plt.show()
                    
print("\nThat's all folks!")

                                                
