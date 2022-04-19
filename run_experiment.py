import argparse
import sys
import os
from scipy.optimize import fsolve
import math
import numpy as np
sys.path.append(os.getcwd() + '/utilities/')
import motor_tools
import helper
from helper import *

import configparser

def linear_calibration_prompt():
    print('current position of linear stage: %s cm' %linear.CurrentPos)
    return_home = raw_input("""\n**** Do you want the reset zero position for linear stage ? ****
You should enter 'yes', if this is your first experimental run. If you are repeating an experiment then you likely
do not need to re-reference the home location (yes/no). : """)
    if return_home == 'yes':
        # return motors to home limit switches
        linear.return_home()
    elif return_home == 'no':
        return
    else:
        print "You did not enter 'yes' or 'no' ."
        linear_calibration_prompt()

def rotary_calibration_prompt(homing, position):
    print('current position of rotary stage: %s deg' %rotary.CurrentPos)
    if homing: return_home = raw_input("""\n**** Do you want to reset zero position for rotary motor? (yes/no) **** : """)
    else: return_home = raw_input("""\n**** Do you want to realign detector when linear stage is at position %s cm (yes/no) **** : """ %position)
    if return_home == 'yes':
        # return motors to home limit switches
	linear.move_absolute(position)
	return rotary.angle_scan(homing)
    elif return_home == 'no':
        return
    else:
        print "You did not enter 'yes' or 'no' ."
	rotary_calibration_prompt(homing, position)



if __name__ == '__main__':

# parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("target_deg", type=float, help="target angle")
    args = parser.parse_args()
    target_deg = args.target_deg
    print('Target angle is '+ str(target_deg) + 'deg')

    
    # parse config file
    config = configparser.ConfigParser()
    config.read('data/config.ini')
    source_energy = float(config['source']['energy'])

    print('Target energy is '+ str(target_energy(source_energy, 20)) + 'deg')
    print('Tag energy is '+ str(target_energy(source_energy, 20)) + 'deg')

    # stage configuration
    linear_config = config['linear_30']
    rotary_config = config['rotary']
    stage_length = float(linear_config['stage_length'])

    # previous calibration
    theta1 = float(config['angle']['theta1'])
    theta2 = float(config['angle']['theta2'])
    print('previously measured angle theta1 theta2 (deg): ', theta1, theta2)


    # establish connection and initialization the MDrives
    linear, rotary = motor_tools.Connection(str(linear_config['sn']),str(rotary_config['sn'])).connect_to_ports()
    linear.main(acceleration = 51200, max_vel = 100000, init_vel = 200, cm_per_rev = float(linear_config['cm_per_rev']), isLinear = True)
    rotary.main(acceleration = 51200, max_vel = 100000, init_vel = 200, cm_per_rev = 360./float(rotary_config['gear_ratio']), isLinear = False) #degree per rev, 90 is gear ratio
    
    # prompt for recalibration of zero position and realigning the source
    linear_calibration_prompt()
    rotary_calibration_prompt(homing = True, position = 0)
    
    # prompt to measure angle at mid point
    theta1_temp = rotary_calibration_prompt(homing = False, position = stage_length/2.0)
    if not theta1_temp == None: theta1 = abs(theta1_temp)

    # prompt measure angle at the farthest edge
    theta2_temp = rotary_calibration_prompt(homing = False, position = stage_length)
    if not theta2_temp == None:  theta2 = abs(theta2_temp)
    
    print('updated measured angle theta1 and theta2 (deg): ', theta1, theta2)
    config.set('angle', 'theta1',str(theta1))
    config.set('angle', 'theta2',str(theta2))

    # move to target position and start taking data at target angle
    lin_move = shift_calc(target_deg)
    print("moving to target angle "+ str(target_deg)+" deg and position " + str(round(lin_move,2))+" cm")
    linear.move_absolute(lin_move)
    rotary.move_absolute(-1*target_deg)
    print("ready to take data at target angle "+ str(target_deg)+" deg and position " + str(round(lin_move,2))+" cm")
