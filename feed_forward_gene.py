import json
import random

CONST_SLICE_NUMBER = 2
FIRST_SLS_ID = 50
FLOWS = 35
REPEAT = 1

previos_links = list()
used_sw = set()
first = frozenset([1,2,3])
med = frozenset([4,5,6,7])
last = frozenset([8,9,10])

def create_links():
    while True :
        lk1 = random.randint(1, 7)
        if lk1 in med:
            lk2 = random.randint(8, 10)
        else :
            lk2 = random.randint(4, 7)
        used_sw.add(lk1)
        used_sw.add(lk2)
        if [lk1, lk2] not in previos_links:
            break
    previos_links.append([lk1, lk2])
    return previos_links

def correct_path(links, path) :
    for i in range(len(path) - 1):
        if [path[i], path[i+1]] not in links :
            return False
    return True

def add_path(links, path) :
    path_list = [path]
    v = [path[len(path) - 1]]
    vertex = [v]
    while vertex != list() :
        elem = vertex.pop(0)
        for lk in links:
            if elem[0] == lk[1] :
                new_elem = [lk[0]]
                new_elem.extend(elem)
                vertex.append(new_elem)
                path_list.append(new_elem)
    return path_list


def create_path(links):
    sw1_s = min(used_sw.intersection(first.union(med)))
    sw1_f = max(used_sw.intersection(first.union(med)))
    while True:
        sw1 = random.randint(sw1_s, sw1_f)
        path = [sw1]
        if sw1 in med and used_sw.intersection(last):
            sw2_s1 = min(used_sw.intersection(last))
            sw2_f1 = max(used_sw.intersection(last))
            sw2 = random.randint(sw2_s1, sw2_f1)
            path.append(sw2)
        else:
            third = random.randint(0,1)
            if third and used_sw.intersection(last):
                sw3_s = min(used_sw.intersection(med))
                sw3_f = max(used_sw.intersection(med))
                sw3 = random.randint(sw3_s, sw3_f)
                sw2_s1 = min(used_sw.intersection(last))
                sw2_f1 = max(used_sw.intersection(last))
                sw2 = random.randint(sw2_s1, sw2_f1)
                path.append(sw3)
                path.append(sw2)
            else :
                sw2_s2 = min(used_sw.intersection(med))
                sw2_f2 = max(used_sw.intersection(med))
                sw2 = random.randint(sw2_s2, sw2_f2)
                path.append(sw2)
        if correct_path(links, path) :
            break
    path_list = add_path(links, path)
    #print("path: ", path_list)
    return path_list


for rep in range(1, REPEAT+1) :
    for bond in range(1,25) :
        rep_str = str(rep).zfill(len(str(REPEAT)))
        bond_str = str(bond).zfill(2)
        file_name = "ff_input/test_rep"+ rep_str + "_lk" + bond_str +".json"
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

        sw_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        links_list = create_links()
        #print(links_list)

        switches = "\t\"switches\" : " + str(sw_list) + ",\n"
        links = "\t\"links\" : " + str(links_list) + ",\n"
        file.write('\"topology\" : {\n' + switches + links + queue + '},\n')

        rate = "\t\"rate\" : 10,\n"
        priority = "\t\"priority\" : " + str(len(slices_id)+1) + ",\n"
        routs_list = ""
        coma = False

        path_list = create_path(links_list)
        index = 0
        while index < FLOWS :
            path = path_list[index % len(path_list)]
            if coma :
                routs_list += ",\n"
            route = "\t{\n\t\t\"path\" : " + str(path) +",\n"
            route += "\t\t\"epsilon\" : 0.01,\n"
            route += "\t\t\"rho_a\" : " + str(10.0 / FLOWS * 0.9) + ",\n"
            route += "\t\t\"b_a\" : 1\n\t}"
            routs_list += route
            coma = True
            index += 1

        routes = "\t\"routes\" : [\n" + routs_list + "\n\t]\n"
        file.write("\"slice\" : {\n" + rate + priority + routes + "}\n")

        file.write('}')
        file.close()
    previos_links = []
    used_sw = set()
        
