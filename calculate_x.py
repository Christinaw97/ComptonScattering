from scipy.optimize import fsolve
import math
import numpy as np

L = 20.0 #half length of linear stage in cm
theta1=50.0/180*math.pi #measurement of angle wrt 0 at half length
theta2=100.0/180*math.pi #measurement of angle wrt 0 at the end

theta=110./180*math.pi # target angle

def equations(p):
    a,b,c = p
    return ( np.sqrt(a**2+b**2-2*a*b*math.cos(theta1))-L,\
            np.sqrt(a**2+c**2-2*a*c*math.cos(theta2))-2*L,\
            np.sqrt(b**2+c**2-2*b*c*math.cos(theta2-theta1))-L,\
    )

a,b,c=  fsolve(equations, (15.,15., 15.))
#print(a,b,c)
theta0=math.asin(b*math.sin(theta1)/L)

#print(theta0/math.pi*180)
x = a*math.sin(theta)/math.sin(theta0+theta)
print("target angle: " + str(int(theta/math.pi*180)) + " degree")
print("target length: " + str(round(x,2)) + " cm")




