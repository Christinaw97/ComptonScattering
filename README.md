# ComptonScattering


## run experiment
``` sudo python run_experiment [target angle in degree]```
The code will ask if you want to zero the position of the linear stage, reset the angle of rotary head at the two ends and mid point of the linear stage. The 3 angles of rotary head can solve for the entire system, including distance between stage and SNSPD. The calibration only needs to be run once. 


```data/config.ini``` stores information of the linear stage, rotary head, and source. ```run_experiment.py``` reads the information.
