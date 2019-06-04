import json
import random
import os
import glob

CONST_SLICE_NUMBER = 2
FIRST_SLS_ID = 50
FLOWS = 50
ITERATIONS = 30
last_layer_st = 11
last_layer_fn = 13
numer_layers = 4
layers = [frozenset([1,2,3,4]), frozenset([5,6,7]), frozenset([8,9,10]), frozenset([11,12,13])]

def choose_layer(sw):
    for i in range(0,len(layers)):
        if sw in layers[i]:
            return i

def previos_lk(sw, links):
    for lk in links:
        if lk[1] == sw:
            return True
    return False

def start_topo():
    links = list()
    for sw_1 in range(1,last_layer_st) :
        layer_st = choose_layer(sw_1)
        sw_2 = random.sample(layers[layer_st+1], 1)[0]
        links.append([sw_1, sw_2])
        if (not previos_lk(sw_1, links)) and (sw_1 not in layers[0]) :
            sw_prev = random.sample(layers[layer_st-1],1)[0]
            links.append([sw_prev, sw_1])
    for sw_2 in range(last_layer_st, last_layer_fn+1):
        if not previos_lk(sw_2, links) :
            sw_prev = random.sample(layers[numer_layers-2],1)[0]
            links.append([sw_prev, sw_2])
    return links

def create_links(links):
    link = []
    while True :
        layer_st = random.randint(0,numer_layers-2)
        lk1 = random.sample(layers[layer_st],1)[0]
        link = [lk1]
        lk2 = random.sample(layers[layer_st+1], 1)[0]
        link.append(lk2)
        if link not in links:
            break
    return link

def add_path(links) :
    path = []
    layer_st = 0
    sw = random.sample(layers[layer_st],1)[0]
    while True:
        path.append(sw)
        set_lk = set()
        for lk in links:
            if lk[0] == sw:
                set_lk.add(lk[1])
        sw = random.sample(set_lk, 1)[0]
        if choose_layer(sw) == (numer_layers-1) :
            break
    path.append(sw)
    return path

def create_path(links) :
    path_list = []
    for sw in layers[numer_layers-1] :
        v = [sw]
        vertex = [v]
        path_list.append(v)
        while vertex != [] :
            elem = vertex.pop(0)
            del_flag = False
            for lk in links:
                if elem[0] == lk[1] :
                    new_elem = [lk[0]]
                    new_elem.extend(elem)
                    vertex.append(new_elem)
                    path_list.append(new_elem)
                    del_flag = True
            if del_flag:
                path_list.remove(elem)
    return path_list

files = glob.glob('lbl_input/*')
for f in files:
    os.remove(f)

previos_links = list()
previos_links = start_topo()
base_path = create_path(previos_links)
print("base_l:", previos_links, "\nbase_p:", base_path)
first_topo = True
while len(previos_links) < ITERATIONS :
    bond = len(previos_links) if first_topo else len(previos_links) + 1
    bond_str = str(bond).zfill(2)
    file_name = "lbl_input/test_lk" + bond_str +".json"
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

    sw_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    links_list = previos_links.copy()
    if not first_topo :
        links_list.append(create_links(previos_links))
        #print("links:", links_list)

    switches = "\t\"switches\" : " + str(sw_list) + ",\n"
    links = "\t\"links\" : " + str(links_list) + ",\n"
    file.write('\"topology\" : {\n' + switches + links + queue + '},\n')

    rate = "\t\"rate\" : 10,\n"
    priority = "\t\"priority\" : " + str(len(slices_id)+1) + ",\n"
    routs_list = ""
    coma = False

    path_list = base_path.copy()
    leng = len(path_list)
    for i in range(leng, FLOWS):
        path_list.append(add_path(links_list))

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
    base_path = path_list.copy()
    previos_links = links_list.copy()
    first_topo = False
