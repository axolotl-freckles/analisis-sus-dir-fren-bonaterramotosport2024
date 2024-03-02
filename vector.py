import numpy as np

def angle_vect(vec: np.ndarray):
	return np.arctan2(vec[1], vec[0])

def to_vect(magnitude, angle:float, out: np.ndarray=None):
	if out is None:
		return np.array([
			magnitude*np.cos(angle),
			magnitude*np.sin(angle)
		])
	else:
		out[0] = magnitude*np.cos(angle)
		out[1] = magnitude*np.sin(angle)
