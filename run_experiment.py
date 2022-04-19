import argparse
import sys
from scipy.optimize import fsolve
import math
import numpy as np
sys.path.append('/home/lab-cpt03/LinearStageRemoteControl/utilities/')
import motor_tools
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



def equations(p):
    a,b,c = p
    t1 = deg2radian(theta1)
    t2 = deg2radian(theta2)

    return ( np.sqrt(a**2+b**2-2*a*b*math.cos(t1))-stage_length/2.,\
   	     np.sqrt(a**2+c**2-2*a*c*math.cos(t2))-stage_length,\
   	     np.sqrt(b**2+c**2-2*b*c*math.cos(t2-t1))-stage_length/2.)
def deg2radian(deg): return deg/180.*math.pi
def radian2deg(rad): return rad/math.pi*180

def shift_calc(t_angle):
    # Since the zero-position is the left of the linear stage, the rotator must move counterclockwise
    target_rad = deg2radian(t_angle)
    theta1_rad = deg2radian(theta1)
    theta2_rad = deg2radian(theta2)
    a,b,c=  fsolve(equations, (15.,15., 15.))
    theta0=math.asin(b*math.sin(theta1_rad)/stage_length*2.)
    x = a*math.sin(target_rad)/math.sin(theta0+target_rad) #absolute distance for linear stage in cm
    return x

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
    linear_config = config['linear_30']
    rotary_config = config['rotary']

    stage_length = float(linear_config['stage_length'])
    theta1 = float(config['angle']['theta1'])
    theta2 = float(config['angle']['theta2'])
    print('previously measured angle theta1 theta2 (deg): ', theta1, theta2)

    # establish connection and initialization
    linear, rotary = motor_tools.Connection(str(linear_config['sn']),str(rotary_config['sn'])).connect_to_ports()
    linear.main(acceleration = 51200, max_vel = 100000, init_vel = 200, cm_per_rev = float(linear_config['cm_per_rev']), isLinear = True)
    rotary.main(acceleration = 51200, max_vel = 100000, init_vel = 200, cm_per_rev = 360./float(rotary_config['gear_ratio']), isLinear = False) #degree per rev, 90 is gear ratio
    
    #prompt for recalibration of zero position and realigning the source
    linear_calibration_prompt()
    rotary_calibration_prompt(homing = True, position = 0)
    
    #measure angle at mid point
    theta1_temp = rotary_calibration_prompt(homing = False, position = stage_length/2.0)
    if not theta1_temp == None: theta1 = abs(theta1_temp)
    #measure angle at the farthest edge
    theta2_temp = rotary_calibration_prompt(homing = False, position = stage_length)
    if not theta2_temp == None:  theta2 = abs(theta2_temp)
    
    print('updated measured angle theta1 and theta2 (deg): ', theta1, theta2)
    config.set('angle', 'theta1',str(theta1))
    config.set('angle', 'theta2',str(theta2))

    # start taking data at target angle
    lin_move = shift_calc(target_deg)
    print("moving to target angle "+ str(target_deg)+" deg and position " + str(round(lin_move,2))+" cm")
    linear.move_absolute(lin_move)
    rotary.move_absolute(-1*target_deg)
    print("ready to take data at target angle "+ str(target_deg)+" deg and position " + str(round(lin_move,2))+" cm")
