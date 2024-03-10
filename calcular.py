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
