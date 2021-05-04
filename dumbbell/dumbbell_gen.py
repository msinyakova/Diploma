import json
import random
import os
import glob

CONST_SLICE_NUMBER = 2
FIRST_SLS_ID = 50
FLOWS = 30
ITERATIONS = 20

def add_path(last) :
    sw_1 = random.randrange(4, last+1, 2)
    sw_2 = random.randrange(5, last+1, 2)
    return [1,sw_1,2,sw_2,3]

def base_path(last):
    path = []
    used_sw = set([1,2,3])
    sw = 4
    while sw <= last :
        sw_2 = random.randrange(5, last+1, 2)
        path.append([1,sw,2,sw_2,3])
        used_sw.add(sw)
        used_sw.add(sw_2)
        sw += 2
    for sw in range(1, last+1):
        if sw in used_sw :
            continue
        sw_1 = random.randrange(4, last+1, 2)
        path.append([1,sw_1,2,sw,3])
    return path

files = glob.glob('dumbbell_input/*')
for f in files:
    os.remove(f)

links_list = [[1,4], [4,2],[2,5], [5,3]]
path_list = [[1,4,2,5,3]]
sw_list = [1,2,3,4,5]
first_topo = True
for sw in range(5, ITERATIONS+1) :
    sw_str = str(sw).zfill(len(str(ITERATIONS)))
    file_name = "dumbbell_input/test_sw" + sw_str +".json"
    file = open(file_name, "w")
    file.write('{\n')

    file.write("\"critical_value\" : 0.01,\n")
    file.write("\"chi_square\" : [249.4, 6.6, 9.2, 11.3, 13.3, 15.1, 16.8, 18.5, 20.1],\n")

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

    if not first_topo :
        sw_list.append(sw)
        if sw % 2 == 0:
            links_list.append([1,sw])
            links_list.append([sw,2])
        else:
            links_list.append([2,sw])
            links_list.append([sw,3])

    switches = "\t\"switches\" : " + str(sw_list) + ",\n"
    links = "\t\"links\" : " + str(links_list) + ",\n"
    file.write('\"topology\" : {\n' + switches + links + queue + '},\n')

    rate = "\t\"rate\" : 10,\n"
    priority = "\t\"priority\" : " + str(len(slices_id)+1) + ",\n"
    routs_list = ""
    coma = False

    path_list = base_path(sw)
    leng = len(path_list)
    for i in range(leng, FLOWS):
        path_list.append(add_path(sw))

    for path in path_list :
        if coma :
            routs_list += ",\n"
        route = "\t{\n\t\t\"path\" : " + str(path) +",\n"
        route += "\t\t\"epsilon\" : 0.01,\n"
        route += "\t\t\"rho_a\" : " + str(10.0 / FLOWS * 0.9) + ",\n"
        route += "\t\t\"b_a\" : 1\n\t}"
        routs_list += route
        coma = True

    routes = "\t\"routes\" : [\n" + routs_list + "\n\t]\n"
    file.write("\"slice\" : {\n" + rate + priority + routes + "}\n")

    file.write('}')
    file.close()
    first_topo = False
