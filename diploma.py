#!/usr/bin/python3

import json
import math
import subprocess
import itertools

def rewrite_services(file_from, file_to) :
    for line in file_from :
        file_to.write(line)

def my_sort(sorted_list, according_list) :
    new_list = []
    index_list = []
    for elem in sorted_list :
        index_list.append(according_list.index(elem))
    index_list.sort()
    for index in index_list :
        new_list.append(according_list[index])
    return new_list

class Route :
    def __init__(self, path_, epsilon, rate_, number_) :
        self.path = path_
        self.eps = epsilon
        self.rate = rate_
        self.number = number_

    def defineDistribution(self, stats, chi_square) :
        sum_f = sum_xf = 0
        f = []
        for it in stats :
            f.append(it['value'])
            sum_f += it['value']
            sum_xf += it['time'] * it['value']
        lambda_medium = sum_xf / sum_f
        K = r = 0
        for i in range(len(f)) :
            if f[i] < lambda_medium :
                r += 1
            p_i = lambda_medium ** i * math.exp(-lambda_medium) / math.factorial(i)
            K += (f[i] - sum_f * p_i) ** 2 / (sum_f * p_i)
        freedom_degree = len(f) - 2 - r
        print('K_критическое = ', chi_square[freedom_degree], ' K_наблюдаемое = ', K)
        if (chi_square[freedom_degree] >= K) :
            print('Poisson distribution with lambda = ', lambda_medium)
            self.rho_a = lambda_medium
# TODO: как оптимизировать b_a по theta и что считать за sigma_a?
            sigma_a = 0
            theta = 1
            self.b_a = sigma_a - 1/theta * (math.log(self.eps) + math.log(1 - math.exp(-theta*(self.rate - self.rho_a))))
            print('rho_a = ', self.rho_a, ' b_a = ', self.b_a)
        else :
            print('Not poisson distribution')       


class Slices :
    def __init__(self, id_, speed, queue_sz) :
        self.sls_id = id_
        self.rate = speed
        self.queue_size = queue_sz

    def delay(self) :
        return self.queue_size / self.rate


class Topology :
    def __init__(self, switches_, links_, queue_) :
        self.switches = switches_
        self.links = links_
        self.queue = queue_
        self.time = ['0']

    def defineServiceCurve(self, slice_list, slice_rate, slice_priority) :
        b_s_ = 0
        for i in range(len(self.queue)) :
            if i < slice_priority :
                b_s_ += slice_list[self.queue[i]].delay()
            else :
                break
        self.rho_s = slice_rate
        self.b_s = b_s_
        print('rho_s = ', self.rho_s, ' b_s = ', self.b_s)

    def correct_route(self, route) :
#TODO проверка на корректность потока
        print("correct_route")

    def create_time_intervals(self, routes_list) :
        for route in routes_list :
            self.correct_route(route)
            previous = ''
            for i in reversed(route.path) :
                previous = str(i) + previous
                if previous not in self.time :
                    self.time.append(previous)

    def create_corresponding_variables(self, routes_list) :
        self.routes_dict = dict()
        number = 1
        for route in routes_list :
            one_route = dict()
            input_variables = list()
            for sw in self.switches :
                if sw not in route.path :
                    continue
                one_switch = list()
                for t in self.time:
                    if t[0] != str(sw) :
                        continue
                    one_switch.append(t)
                    if t not in input_variables :
                        input_variables.append(t)
                    if t[1:] in self.time :
                        one_switch.append(t[1:])
                        if t[1:] not in input_variables :
                            input_variables.append(t[1:])
                    elif t[1:] == '':
                        one_switch.append('0')
                        if '0' not in input_variables :
                            input_variables.append('0')
                one_route[str(sw)] = one_switch
            one_route['0'] = input_variables
            self.routes_dict[number] = one_route
            number += 1

    def start_serv(self, time, elem) :
        equal_start = dict()
        for i in range(len(time)) :
            if time[i] != elem and time[i][0] == elem[0] :
                equal_start[i] = time[i]
        return equal_start

    def equal_time(self, time, pos1, pos2) :
        sub_pos1 = time.index(time[pos1][1:])
        sub_pos2 = time.index(time[pos2][1:])
        if sub_pos1 <= pos1 or sub_pos1 <= pos2:
            return False
        if sub_pos2 <= pos1 or sub_pos2 <= pos2 :
            return False
        return True

    def different_time(self, time, pos1, pos2) :
        if (pos1 > pos2) :
            pos1, pos2 = pos2, pos1
        sub_pos1 = time.index(time[pos1][1:])
        sub_pos2 = time.index(time[pos2][1:])
        if sub_pos1 > pos1 and sub_pos1 < pos2 and sub_pos2 > pos2 :
            return True 
        return False    

    def correct_time(self, time) :
        swap = list()
        for i in range(len(time)) :
            if time[len(time) - 1] != '0' :
                return False
            if time[i][1:] == '' :
                continue
            if time.index(time[i][1:]) <= i :
                return False
            position = self.start_serv(time, time[i])   
            for key in position.keys() :
                equal = self.equal_time(time, i, key)
                if not equal and not self.different_time(time, i, key) :
                    return False
                if equal and i < key and time[i][1] > time[key][1] :
                    swap.append(tuple((i,key)))
        for it in swap :
            time[it[0]], time[it[1]] = time[it[1]], time[it[0]]     
        return True

    def create_temporal_constraints(self) :
        self.temporal_constraints = dict()
        number = 1
        for key in self.routes_dict.keys() :
            route_time_constraints = list()
            time = self.routes_dict[key]['0']
            for it in itertools.permutations(time, len(time)) :
                constraints = list(it)
                if self.correct_time(constraints) :
                    if constraints not in route_time_constraints :
                        route_time_constraints.append(constraints)
                        print(constraints)
            print('-----------------------------')
            '''topo.temporal_constraints: словарь с ключом - номер потока, 
            значение - список из всевозможных задач ЛП, которые подходят для данного потока'''
            self.temporal_constraints[number] = route_time_constraints
            number += 1         

    def generateTime(self, routes_list) :
        self.create_time_intervals(routes_list)
        self.create_corresponding_variables(routes_list)
        self.create_temporal_constraints()

    def expression_sign(self, task, i):
        if task[i][0] == task[i + 1][0] :
            return ' = '
        return ' <= '

    def generateLP(self, task, file, route) :
        #time
        path = route.number
        for i in range(len(task)-1) :
            elem1 = 'u' if task[i] == 'u' else "t_"+task[i]
            elem2 = 'u' if task[i+1] == 'u' else "t_"+task[i+1]
            file.write(elem1 + self.expression_sign(task, i) + elem2 + ';\n')

        for sw in self.routes_dict[path] :
            time = my_sort(self.routes_dict[path][sw], task) if sw != '0' else task
            for i in range(len(time)-1) :
                #non_decreasing functions
                file.write('F_'+sw+'_'+str(path)+'_t_'+time[i])
                file.write(self.expression_sign(task, i))
                file.write('F_'+sw+'_'+str(path)+'_t_'+time[i+1]+';\n')
                if sw == '0' :
                    continue
                #start_backlog
                if sw == time[i][0] :
                    file.write('F_'+str(int(sw)-1)+'_'+str(path)+'_t_'+time[i]+' =')
                    file.write(' F_'+sw+'_'+str(path)+'_t_'+time[i]+';\n')
                #flow_contains
                else :
                    file.write('F_'+sw+'_'+str(path)+'_t_'+time[i]+' <=')
                    file.write(' F_0_'+str(path)+'_t_'+time[i]+';\n')
        
        #arrival
        for it in itertools.combinations(reversed(task), 2) :
            if it[0] == it[1] :
                continue
            file.write('F_0_'+str(path)+'_t_'+it[0]+' - F_0_'+str(path)+'_t_'+it[1])
            file.write(' <= '+str(route.rho_a)+' * t_'+it[0]+' - '+str(route.rho_a)+' * t_'+it[1]+' + '+str(route.b_a)+';\n')

    def unite_time(self) :
        all_time = []
        for key in self.temporal_constraints.keys() :
            for elem in self.temporal_constraints[key][0] :
                if elem not in all_time :
                    all_time.append(elem)
        return all_time 

    def generateServer(self, file_name) :
        all_time = self.unite_time()
        for sw in self.switches :
            for time in all_time :
                if time == '0' :
                    continue
                if time[0] != str(sw) :
                    continue
                t = '0' if time[1:] == '' else time[1:]
                self.one_server(t, sw, file_name, '+')
                file_name.write(' - ')
                self.one_server(time, sw, file_name, '-')
                file_name.write(' >= '+str(self.rho_s)+' * t_'+t+' - ')
                file_name.write(str(self.rho_s)+' * t_'+time+' - '+str(self.b_s)+';\n')

    def one_server(self, time, sw, file_name, elem) :
        flag = False
        for key in self.temporal_constraints.keys() :
            if time not in self.temporal_constraints[key][0] :
                continue
            if flag : 
                file_name.write(' '+elem+' ')
            file_name.write('F_'+str(sw)+'_'+str(key)+'_t_'+time+'')
            flag = True

    def addDelay(self) :
        for key in self.temporal_constraints.keys() :
            size = len(self.temporal_constraints[key])
            for index in range(size) :
                pos = 1
                length = len(self.temporal_constraints[key][index])
                while pos < length :
                    help_list = self.temporal_constraints[key][index].copy()
                    help_list.insert(pos, 'u')
                    self.temporal_constraints[key].append(help_list)
                    pos += 1


#______________________MAIN______________________
input_file = open("input.json", "r")
web = json.load(input_file)

tp_help = web['topology']
topo = Topology(tp_help['switches'],tp_help['links'], tp_help['queue'])

slice_list = {}
sls_help = web['slices']
for curr in sls_help :
    slice_list[curr['id']] = Slices(curr['id'], curr['rate'], curr['queue_size'])

slice_info = web['slice']
slice_rate = slice_info['rate']
slice_priority = slice_info['priority']
topo.defineServiceCurve(slice_list, slice_rate, slice_priority)

routes_list = []
i = 0
for curr in slice_info['routes'] :
    routes_list.append(Route(curr['path'], curr['epsilon'], slice_rate, i + 1))
    if 'rho_a' not in curr :
        routes_list[i].defineDistribution(curr['statistic'], web['chi_square'])
    else :
        routes_list[i].rho_a = curr['rho_a']
        routes_list[i].b_a = curr['b_a']
        print('rho_a = ', routes_list[i].rho_a, ' b_a = ', routes_list[i].b_a)
    i += 1

topo.generateTime(routes_list)
service_file = open("help.txt", "w")
topo.generateServer(service_file)
service_file.close()
topo.addDelay()
for key in topo.temporal_constraints.keys() :
    for task in topo.temporal_constraints[key] :
        LP_file = open("lp_file.txt", "w")
        LP_file.write('max: t_0 - u;\n')
        service_file = open("help.txt", "r")
        rewrite_services(service_file, LP_file)
        service_file.close()
        topo.generateLP(task, LP_file, routes_list[key-1])
        LP_file.close()
        args = ["./../lp_solve_5.5.2.5_exe_ux64/lp_solve", "lp_file.txt"]
        process = subprocess.Popen(args, stdout=subprocess.PIPE)
        data = process.communicate()
        print(data[0])
        #Выбор максимума из полученных значений


input_file.close()
