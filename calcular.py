import sys
import glob

import numpy             as np
import pandas            as pd
import numpy.linalg      as lag
# import matplotlib.pyplot as plt

import vector            as vec
import fourbars          as fba
import fourbarforce      as fbf

# from matplotlib import ticker

g = -9.80665

gravity = np.array([0.0, g])

all_tasks = {
	'geo',
	'rest_sim',
	'dyn_sim',
	'all'
}

directorio_resultados = './resultados'
directorio_parametros = './parámetros'

dict_param = {
	'geo': '/SUS_GEO.csv',
	'sim': '/SUS_DATA.csv'
}

tasks = set(sys.argv[1:])
# print(glob.glob(f'{directorio_resultados}/*.csv'))


if len(tasks) < 1:
	print('No se han dado tareas para ejecutar.')
	option = input('Quisiras ejecutar todas [s/n]: ')
	if option == 's':
		tasks = all_tasks
	else:
		exit()

if 'all' in tasks:
	tasks = all_tasks

'''
	CÁLCULOS DE MOVIMIENTO DE SUSPENSIÓN
'''

if 'geo' in tasks:
	print(f'{"="*20:^50}')
	print(f'{"CÁLCULOS GEOMÉTRICOS DE SUSPENSIÓN":^50}')
	print(f'{"="*20:^50}')

	RANGE   = np.deg2rad(5.0)
	STEP    = np.deg2rad(0.5)
	# N_STEPS = 2*int(RANGE/np.deg2rad(0.5))

	titulos = [
		'theta_1',
		'theta_2',
		'theta_3',
		'theta_4'
	]

	geo_data = pd.read_csv(directorio_parametros+dict_param['geo'])
	# print(geo_data.info(), end='\n\n')

	for i, name in enumerate(geo_data['name']):
		theta1 = geo_data['t1'][i]
		theta2 = geo_data['t2'][i]
		l      = np.array([
			geo_data['l1'][i],
			geo_data['l2'][i],
			geo_data['l3'][i],
			geo_data['l4'][i],
		])
		MAX_ANGLE = theta2 + RANGE
		MIN_ANGLE = theta2 - RANGE
		theta2s = np.arange(MIN_ANGLE, MAX_ANGLE, STEP)

		print(f'[{i:2d}] calculando "{name}"')
		print(f'\tl: {l}')
		print(f'\tMIN:{np.rad2deg(MIN_ANGLE):7.2f}° MAX:{np.rad2deg(MAX_ANGLE):7.2f}°')
		print(f'\tPasos: {theta2s.shape[0]}')

		theta = fba.get_abs_theta(l, theta2s, theta1)
		result_dict = {titulos[i]: theta[i] for i in range(4)}
		result_df   = pd.DataFrame(result_dict)

		result_dir = f'{directorio_resultados}/{name}.csv'
		result_df.to_csv(result_dir)
		print(f'\tGUARDADO EXITOSAMENTE EN: "{result_dir}"')
		print()

'''
	CÁLCULOS DE ESFUERZO DE LA SUSPENSIÓN
'''

if 'rest_sim' in tasks:
	print(f'{"="*20:^50}')
	print(f'{"CÁLCULOS DE ESFUERZOS EN REPOSO":^50}')
	print(f'{"="*20:^50}')

	titulos = [
		'F_12x',
		'F_12y',
		'F_32x',
		'F_32y',
		'F_43x',
		'F_43y',
		'F_14x',
		'F_14y',
		'T_b',
	]

	geo_data = pd.read_csv(directorio_parametros+dict_param['geo'])
	sim_data = pd.read_csv(directorio_parametros+dict_param['sim'])

	for i, name in enumerate(sim_data['name']):
		idx  = geo_data['name'] == name
		data = geo_data[idx]

		theta1 = data['t1'][0]
		theta2 = data['t2'][0]
		l      = np.array([
			data['l1'][0],
			data['l2'][0],
			data['l3'][0],
			data['l4'][0],
		])
		masses = np.array([
			1.0,
			sim_data['m2'][i],
			sim_data['m3'][i],
			sim_data['m4'][i],
		])
		traction = np.array([0.0, sim_data['normal'][i]])

		print(f'[{i:2d}] calculando "{name}"')

		theta = fba.get_abs_theta(l, theta2, theta1)

		rel_coordinates, abs_coordinates = fbf.to_coordinates(l, theta)
		wheel_offset   , traction_offset = fbf.sum_rel_vect_to_abs(
			theta,
			sim_data['traction_magnitude_offset'][i],
			sim_data['traction_angle_offset'][i],
			2,
			abs_coordinates=abs_coordinates
		)

		e3_com_rel_vect, e3_com_abs_vect = fbf.sum_rel_vect_to_abs(
			theta,
			sim_data['e3_com_magnitude_offset'][i],
			sim_data['e3_com_angle_offset'][i],
			2,
			abs_coordinates=abs_coordinates
		)

		com_prv, com_nxt = fbf.get_middle_com(rel_coordinates)
		com_prv[:, 2]    = abs_coordinates[:, 1] - e3_com_abs_vect
		com_nxt[:, 2]    = abs_coordinates[:, 2] - e3_com_abs_vect

		e3com_traction = traction_offset - e3_com_abs_vect

		geo_mtx = fbf.get_geo_mtx([com_prv, com_nxt], torque_element=1)
		result_mtx = np.array([
			0.0 - masses[1]*gravity[0],
			0.0 - masses[1]*gravity[1],
			0.0,
			0.0 - masses[2]*gravity[0] - traction[0],
			0.0 - masses[2]*gravity[1] - traction[1],
			0.0 - e3com_traction[0]*traction[1] + e3com_traction[1]*traction[0],
			0.0 - masses[3]*gravity[0],
			0.0 - masses[3]*gravity[1],
			0.0,
		])

		results = lag.solve(geo_mtx, result_mtx)
		results[-1] /= 1000

		result_dict = {titulos[i]: results[i] for i in range(len(results))}
		result_df   = pd.DataFrame(result_dict, index=[name])

		result_dir = f'{directorio_resultados}/SIM_STATIC_{name}.csv'
		result_df.to_csv(result_dir)
		print(f'\tGUARDADO EXITOSAMENTE EN: "{result_dir}"')
		print()
