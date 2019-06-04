import json
import math
import random
import os
import glob

CONST_FLOW_NUMBER = 10
CONST_SWITCH_NUMBER = 10
CONST_SLICE_NUMBER = 2
FIRST_SLS_ID = 50

files = glob.glob('input/*')
for f in files:
    os.remove(f)

#zero_number = len(str(CONST_FLOW_NUMBER * CONST_SWITCH_NUMBER))
#number = 1
for flow_number in range(1, CONST_FLOW_NUMBER + 1) :
	for sw_number in range(1, CONST_SWITCH_NUMBER + 1) :
		#index = str(number).zfill(zero_number)
		sw_str = str(sw_number).zfill(len(str(CONST_SWITCH_NUMBER)))
		flow_str = str(flow_number).zfill(len(str(CONST_FLOW_NUMBER)))
		file_name = "input/test_sw"+ sw_str + "_f" + flow_str +".json"
		file = open(file_name, "w")
		file.write('{\n')

		file.write("\"critical_value\" : 0.01,\n")
		file.write("\"chi_square\" : [249.4, 6.6, 9.2, 11.3, 13.3, 15.1, 16.8, 18.5, 20.1, 21.7, 23.2, 24.7, 26.2, 27.7, 29.1, 30.6, 32.0, 33.4, 34.8, 36.2, 37.6],\n")

		slices_id = list()
		slice_list = ""
		coma = False
		for i in range(CONST_SLICE_NUMBER) :
			if coma :
				slice_list += ",\n"
			slices_id.append(FIRST_SLS_ID + i)
			slice_elem = "\t{ \"id\" : " + str(FIRST_SLS_ID + i) + ", \"rate\" : 10}"
			slice_list += slice_elem
			coma = True

		file.write("\"slices\" : [\n" + slice_list + "\n],\n")

		file.write("\"bandwidth\" : 100,\n")

		random.shuffle(slices_id)
		queue = "\t\"queue\" : " + str(slices_id) + "\n"
		sw_list = list()
		sw_list.append(1)
		links_list = list()
		for i in range(1, sw_number) :
			sw_list.append(i+1)
			links_list.append([i, i+1])
		switches = "\t\"switches\" : " + str(sw_list) + ",\n"
		links = "\t\"links\" : " + str(links_list) + ",\n"
		file.write('\"topology\" : {\n' + switches + links + queue + '},\n')

		rate = "\t\"rate\" : 10,\n"
		priority = "\t\"priority\" : " + str(len(slices_id)+1) + ",\n"
		routs_list = ""
		coma = False
		for i in range(flow_number) :
			if coma :
				routs_list += ",\n"
			route = "\t{\n\t\t\"path\" : " + str(sw_list) +",\n"
			route += "\t\t\"epsilon\" : 0.01,\n"
			route += "\t\t\"rho_a\" : " + str(10.0 / flow_number * 0.9) + ",\n"
			route += "\t\t\"b_a\" : 1\n\t}"
			routs_list += route
			coma = True

		routes = "\t\"routes\" : [\n" + routs_list + "\n\t]\n"
		file.write("\"slice\" : {\n" + rate + priority + routes + "}\n")

		file.write('}')
		file.close()
		#number += 1
