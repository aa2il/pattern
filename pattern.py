#! /usr/bin/python3 -u
################################################################################
#
# pattern.py - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
#    Program kto measure beam pattern.
#
################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
################################################################################

from __future__ import print_function
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer
import argparse
from pprint import pprint
import rig_io.socket_io as socket_io
from rig_io.ft_tables import CONNECTIONS,RIGS
import functools
import time
import datetime;
  
################################################################################

# Structure to contain processing params
class PARAMS:
    def __init__(self):

        # Process command line args
        # Can add required=True to anything that is required
        arg_proc = argparse.ArgumentParser()
        arg_proc.add_argument("-rig", help="Connection Type",
                              type=str,default=["ANY"],nargs='+',
                              choices=CONNECTIONS+['NONE']+RIGS)
        arg_proc.add_argument("-port", help="Rig connection Port",
                              type=int,default=0)
        arg_proc.add_argument("-rotor", help="Rotor connection Type",
                      type=str,default="NONE",
                      choices=['HAMLIB','NONE'])
        arg_proc.add_argument("-port2", help="Rotor onnection Port",
                              type=int,default=0)
        args = arg_proc.parse_args()

        self.RIG_CONNECTION   = args.rig[0]
        if len(args.rig)>=2:
            self.RIG       = args.rig[1]
        else:
            self.RIG       = None
            
        self.PORT             = args.port
        if self.PORT==0 and self.RIG_CONNECTION=="FLRIG" and self.RIG=="IC9700":
            self.PORT=12346
        
        self.ROTOR_CONNECTION = args.rotor
        self.PORT2            = args.port2
        if self.ROTOR_CONNECTION=='HAMLIB' and self.PORT2==0:
            self.PORT2        = 4533

################################################################################

# User params
THRESH=5
START=-180
STOP=180
STEP=10

################################################################################

if __name__ == '__main__':
    print("\n\n***********************************************************************************")
    print("\nStarting beam pattern measurement  ...")
    P=PARAMS()
    print("\nP=",end=' ')
    pprint(vars(P))

    # Open connection to rig
    print('\nOpening rig ...')
    P.sock = socket_io.open_rig_connection(P.RIG_CONNECTION,0,P.PORT,0,'RIG',rig=P.RIG)
    if not P.sock.active and P.sock.connection!='NONE':
        print('*** No connection available to rig ***')
        sys.exit(0)
    else:
        print('Opened socket to',P.sock.rig_type,P.sock.rig_type1,\
              P.sock.rig_type2)

    # Open connection to rotor
    print('\nOpening rotor...')
    P.sock2 = socket_io.open_rig_connection(P.ROTOR_CONNECTION,0,P.PORT2,0,'ROTOR')
    if not P.sock2.active and P.sock2.connection!='NONE':
        print('*** No connection available to rotor ***')
        sys.exit(0)
    else:
        print('Opened socket to',P.sock2.rig_type,P.sock2.rig_type1,\
              P.sock2.rig_type2)

    # Open output file
    fp=open('PATTERN.DAT','w')
    fp.write('# Azimuth Pattern Measurements\n')
    fp.write('# \n')
    fp.write('# \n')
    fp.write('# Time Stamp: '+str( datetime.datetime.now())+'\n' )
    fp.write('# Rig: '+P.sock.rig_type1+P.sock.rig_type2+'\n')
    fp.write('# Rig Connection: '+P.RIG_CONNECTION+'\n')
    fp.write('# \n')
    fp.write('Theta\tAz\tEl\ts\tdb\tS\n')
    
    # Check where the rotor is & try to inimize initial ovement
    pos=P.sock2.get_position()
    az=pos[0]
    if az!=None:
        if az>180:
            az-=360
        if abs(az-STOP)<abs(az-START):
            tmp=START
            START=STOP
            STOP=tmp
            STEP=-STEP

    print(az,START,STOP,STEP)
    #sys.exit(0)

    # Loop over all angles
    for theta in range(START,STOP+STEP,STEP):
        #theta=0

        # Set the number of tries for this step
        if theta==START:
            ntries=60              # It can take 1 minute to come completely round
        else:
            ntries=10              # Should take only a couple of seconds afer that
        
        if theta<-179:
            theta=-179
        elif theta>179:
            theta=179

        # Set rotor position
        P.sock2.set_position([theta,0])
        
        # Make sur rotor is stable & get its position
        for i in range(ntries):
            time.sleep(1)
            pos=P.sock2.get_position()
            az=pos[0]
            if az!=None and az>180:
                az-=360
            el=pos[1]
            print(i,'\ttheta=',theta,'\tpos=',pos)

            if az==None or (abs(az-theta)<THRESH and abs(el-0)<THRESH):
                break
        
        # Read S-meter
        # Flrig processes the raw number read from the rigs
        # It returns the dB above S0. So 0 for S0 and 54 for S9.
        s=0
        N=10
        for i in range(N):
            time.sleep(1)
            s+=P.sock.read_meter('S')
            print(i,s)
        s/=N

        # Convert to dB
        if P.RIG_CONNECTION=='DIRECT':
            #db=float(s)*114./255.-54.
            db=float(s)*100./256
        elif P.RIG_CONNECTION=='FLRIG':
            db=s
            
        if db>54:
            plus=db-54
            S=9
        else:
            plus=0
            S=db/6
        print('theta=',theta,'\tS=',s,db,S)

        # Save measurement
        if az==None:
            az=-999
        if el==None:
            el=-999
        fp.write('%f\t%f\t%f\t%f\t%f\t%f\n' % (theta,az,el,s,db,S))
        fp.flush()
        
        #break

    fp.close()
