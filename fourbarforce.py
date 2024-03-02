import numpy  as np
import vector as vec

def to_coordinates(l:np.ndarray, theta:np.ndarray):
	rel_coordinates = vec.to_vect(l, theta)
	abs_coordinates = np.cumsum(rel_coordinates, axis=1)
	return rel_coordinates, abs_coordinates

def get_middle_com(rel_coordinates:np.ndarray):
	com_prev = np.zeros_like(rel_coordinates)
	com_next = np.zeros_like(rel_coordinates)

	com_prev = -rel_coordinates / 2
	com_next =  rel_coordinates / 2

	return com_prev, com_next

def sum_rel_vect_to_abs(
		theta:np.ndarray,
		vec_magnitude:float,
		vec_rel_angle:float,
		base_element:int,
		abs_coordinates:np.ndarray=None
):
	rel_offset = vec.to_vect(vec_magnitude, theta[base_element] + vec_rel_angle)

	if abs_coordinates is None:
		return rel_offset
	
	abs_offset = abs_coordinates[:, base_element-1] + rel_offset

	return rel_offset, abs_offset

def get_geo_mtx(com_r:np.ndarray, torque_element:int=1) -> np.ndarray:
	com_prv = com_r[0]
	com_nxt = com_r[1]
	geo_mtx = np.array([
		[          1.0,          0.0,           1.0,           0.0,           0.0,           0.0,           0.0,           0.0, 0.0],
		[          0.0,          1.0,           0.0,           1.0,           0.0,           0.0,           0.0,           0.0, 0.0],
		[-com_prv[1,1], com_prv[0,1], -com_nxt[1,1],  com_nxt[0,1],           0.0,           0.0,           0.0,           0.0, 0.0],
		[          0.0,          0.0,          -1.0,           0.0,           1.0,           0.0,           0.0,           0.0, 0.0],
		[          0.0,          0.0,           0.0,          -1.0,           0.0,           1.0,           0.0,           0.0, 0.0],
		[          0.0,          0.0,  com_prv[1,2], -com_prv[0,2], -com_nxt[1,2],  com_nxt[0,2],           0.0,           0.0, 0.0],
		[          0.0,          0.0,           0.0,           0.0,          -1.0,           0.0,           1.0,           0.0, 0.0],
		[          0.0,          0.0,           0.0,           0.0,           0.0,          -1.0,           0.0,           1.0, 0.0],
		[          0.0,          0.0,           0.0,           0.0, -com_prv[1,3], -com_prv[0,3], -com_nxt[1,3], com_nxt[0,3], 0.0]
	])

	if torque_element is not None or torque_element != 0:
		geo_mtx[torque_element*3 - 1, -1] = 1.0

	return geo_mtx
