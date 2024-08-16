#########################################################################################
# The code implements the Unicycle model in which was a very important focus for the    #
#  research project in order to determine proper variable to measure.                   #
#                                                                                       #
#   Authors: Zarin Saifee                                                               #
#########################################################################################
import numpy as np
import math as math

def unicycleDynamics(X, U):
    """
    Args: X, U
            X = Starting point array. [X_0, Y_0, theta_0] - (x,y) and starting angle with respect to x-axis
            U = Destination Point Array. [U_x,U_y, U_theta] - (x,y), the U_theta is not relevent in this code 
            as the element is not used at any point but it needs to be included to calculate the norm 

    Return: v, w
            v = forward_velocity
            w = angular_velocity
    """
    X = np.array(X)
    U = np.array(U)
    e = U-X
    E = np.linalg.norm(e)
    dx = U[0] - X[0]
    dy = U[1] - X[1]
    phi = math.atan2(dy, dx) - X[2]
    v = E* math.cos(phi)
    w = ((math.cos(phi) + 1) * math.sin(phi))+ phi

    print(v)
    print(w)
    return v,w,phi