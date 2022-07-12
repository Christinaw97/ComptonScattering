# plot to calculate target/tag energy for certain incoming photon energy/angle
import math
import numpy as np
import matplotlib.pyplot as plt

#angle conversions
def deg2radian(deg): return deg/180.*math.pi
def radian2deg(rad): return rad/math.pi*180

#calculate expected energy at target/tag detector given incoming photon energy and angle
def tag_energy(photon_in, theta):
    ''' incoming photon energy in keV, theta in deg '''
    return photon_in/(1+photon_in/511.0*(1-math.cos(deg2radian(theta))))

def target_energy(photon_in, theta):
	return photon_in-tag_energy(photon_in, theta)



def equations(p):
    ''' used in function shift_calc to solve for a, b, c '''
    a,b,c = p
    t1 = deg2radian(theta1)
    t2 = deg2radian(theta2)

    return ( np.sqrt(a**2+b**2-2*a*b*math.cos(t1))-stage_length/2.,\
   	     np.sqrt(a**2+c**2-2*a*c*math.cos(t2))-stage_length,\
   	     np.sqrt(b**2+c**2-2*b*c*math.cos(t2-t1))-stage_length/2.)


def shift_calc(t_angle):
    ''' given target angle, calculate the distance for linear stage to move in cm
    t_angle is in unit of degree '''
    target_rad = deg2radian(t_angle)
    theta1_rad = deg2radian(theta1)
    theta2_rad = deg2radian(theta2)
    a,b,c=  fsolve(equations, (15.,15., 15.))
    theta0=math.asin(b*math.sin(theta1_rad)/stage_length*2.)
    x = a*math.sin(target_rad)/math.sin(theta0+target_rad) #absolute distance for linear stage in cm
    return x
