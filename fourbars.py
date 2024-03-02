import numpy as np

def get_A_B(l1, l2, theta1, theta2):
	A = l1*np.cos(theta1) + l2*np.cos(theta2)
	B = l1*np.sin(theta1) + l2*np.sin(theta2)
	return A, B

def get_C_D(l3, l4, A, B):
	C = (l4**2 - l3**2 - A**2 - B**2) / (2*l3)
	D = (l3**2 - l4**2 - A**2 - B**2) / (2*l4)
	return C, D

def get_theta_3_4(A, B, C, D):
	theta3 = 2*np.arctan( (B-np.sqrt(A**2+B**2-C**2)) / (C+A) )
	theta4 = 2*np.arctan( (B+np.sqrt(A**2+B**2-D**2)) / (D+A) )
	return theta3, theta4

def get_abs_theta(l:np.ndarray, theta2, theta1=0.0) -> np.ndarray:
	a,      b      = get_A_B(l[0], l[1], theta1, theta2)
	c,      d      = get_C_D(l[2], l[3], a, b)
	theta3, theta4 = get_theta_3_4(a, b, c, d)

	theta = None
	if type(theta2) is np.ndarray:
		theta = np.ones((4, theta2.shape[0]))
	else:
		theta = np.ones(4)
	theta[0] *= theta1
	theta[1] *= theta2
	theta[2] *= theta3
	theta[3] *= theta4
	return theta

def get_internal_angles(theta:np.ndarray) -> np.ndarray:
	alpha = np.ones_like(theta)

	max_it = alpha.shape[0]
	for i in range(max_it):
		alpha[i] = np.abs(np.pi - np.abs(theta[(i+1)%max_it] - theta[i]))

	# alpha[0] = np.abs(np.pi - np.abs(theta[1] - theta[0]))
	# alpha[1] = np.abs(np.pi - np.abs(theta[2] - theta[1]))
	# alpha[2] = np.abs(np.pi - np.abs(theta[3] - theta[2]))
	# alpha[3] = np.abs(np.pi - np.abs(theta[0] - theta[3]))

	return alpha
