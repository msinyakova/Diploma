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
        self.lengthLP = 0

    def defineServiceCurve(self, slice_list, slice_rate, slice_priority) :
        b_s_ = 0
        for i in range(len(self.queue)) :
            if i < slice_priority :
                b_s_ += slice_list[self.queue[i]].delay()
            else :
                break
        self.rho_s = slice_rate
        self.b_s = 0.1
        #self.b_s = b_s_
        print('rho_s = ', self.rho_s, ' b_s = ', self.b_s)

    def formRouteTime(self, route) :
        end = route.path[len(route.path) - 1]
        time = list()
        time.append(str(end))
        vertex = list()
        vertex.append(str(end))
        while vertex != list() :
            elem = vertex[0]
            for lk in self.links:
                if elem[0] == str(lk[1]) :
                    new_elem = str(lk[0]) + elem
                    time.append(new_elem)
                    vertex.append(new_elem)
            vertex.remove(elem)
        time.append('0')
        #print(time)
        return time

    def formSwitchesTime(self, time, routes_list) :
        routes_dict = dict()
        number = 1
        for route in routes_list :
            one_route = dict()
            input_variables = list()
            for sw in self.switches :
                if sw not in route.path :
                    continue
                one_switch = list()
                for t in time:
                    if t[0] != str(sw) :
                        continue
                    one_switch.append(t)
                    if t not in input_variables :
                        input_variables.append(t)
                    if t[1:] in time :
                        one_switch.append(t[1:])
                        if t[1:] not in input_variables :
                            input_variables.append(t[1:])
                    elif t[1:] == '':
                        one_switch.append('0')
                        if '0' not in input_variables :
                            input_variables.append('0')
                one_route[str(sw)] = one_switch
            one_route['0'] = input_variables
            routes_dict[number] = one_route
            number += 1
        #print(routes_dict)
        return routes_dict 


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

    def timeConstraints(self, time) :
        route_time_constraints = list()
        for it in itertools.permutations(time, len(time)) :
            constraints = list(it)
            if self.correct_time(constraints) :
                if constraints not in route_time_constraints :
                    route_time_constraints.append(constraints)
                    #print(constraints)
        #print('-----------------------------')
        return route_time_constraints

    def createLP(self, task, routes_dict, file, routes_list) :
        file.write('//time\n')
        topo.write_time(task, file)
        for route in routes_list :
            file.write("\n//flow "+str(route.number)+'\n')
            topo.generate_constraints(task, routes_dict, file, route)
            file.write("\n//arrival "+str(route.number)+"\n")
            topo.generate_arrival(task, routes_dict, file, route)
        file.write("\n//servers\n")
        topo.generate_servers(task, routes_list, file)

    def expression_sign(self, task, i):
        if task[i][0] == task[i + 1][0] :
            return ' = '
        return ' <= '

    def write_time(self, task, file) :
        for i in range(len(task)-1) :
            file.write('t'+ task[i] + self.expression_sign(task, i)+'t'+task[i+1]+ ';\n')
            self.lengthLP += 1

    def generate_constraints(self, task, routes_dict, file, route) :
        path = route.number
        for sw in routes_dict[path] :
            time = my_sort(routes_dict[path][sw], task) if sw != '0' else task
            file.write('//sw '+str(sw)+'\n')
            pos = 0
            for i in range(len(time)-1) :
                #non_decreasing functions
                file.write('F'+str(path)+'s'+sw+'t'+time[i])
                file.write(self.expression_sign(task, i))
                file.write('F'+str(path)+'s'+sw+'t'+time[i+1]+';\n')
                self.lengthLP += 1
                if sw == '0' :
                    continue
                #start_backlog
                if sw == time[i][0] :
                    previos_pos = route.path.index(int(sw))
                    previos_sw = '0' if previos_pos == 0 else str(route.path[previos_pos - 1])
                    file.write('F'+str(path)+'s'+previos_sw+'t'+time[i]+' = ')
                    file.write('F'+str(path)+'s'+sw+'t'+time[i]+';\n')
                    self.lengthLP += 1
                #flow_contains
                else :
                    file.write('F'+str(path)+'s'+sw+'t'+time[i]+' <= ')
                    file.write('F'+str(path)+'s0t'+time[i]+';\n')
                    self.lengthLP += 1
                pos = i
            if sw != '0' and (pos + 1) < len(time):
                file.write('F'+str(path)+'s'+sw+'t'+time[pos+1]+' <= ')
                file.write('F'+str(path)+'s0t'+time[pos+1]+';\n')
                self.lengthLP += 1

    def generate_arrival(self, task, routes_dict, file, route) :
        path = route.number
        for it in itertools.combinations(reversed(task), 2) :
            if it[0] == it[1] :
                continue
            file.write('F'+str(path)+'s0t'+it[0]+' - F'+str(path)+'s0t'+it[1])
            file.write(' <= '+str(route.rho_a)+' * t'+it[0]+' - '+str(route.rho_a)+' * t'+it[1]+' + '+str(route.b_a)+';\n')
            self.lengthLP += 1

    def choose_routes(self, sw, routes_list) :
        routes_in_sw = list()
        for route in routes_list :
            if sw in route.path :
                routes_in_sw.append(route.number)
        return routes_in_sw

    def generate_servers(self, task, routes_list, file) :
        for sw in self.switches :
            eq_start = list()
            previos = 0
            routes_in_sw = self.choose_routes(sw, routes_list)
            for time in task :
                if time == '0' :
                    continue
                if time[0] != str(sw) :
                    continue
                t = '0' if time[1:] == '' else time[1:]
                self.one_server(routes_in_sw, t, sw, file, '+')
                file.write(' - ')
                self.one_server(routes_in_sw, time, sw, file, '-')
                file.write(' >= '+str(self.rho_s)+' * t'+t+' - ')
                file.write(str(self.rho_s)+' * t'+time+' - '+str(self.b_s)+';\n')
                self.lengthLP += 1
                if eq_start == list() :
                    eq_start.append(time)
                    previos = task.index(time)
                elif task.index(time) - previos <= 1:
                    eq_start.append(time)
                    previos = task.index(time)
            self.servers_equal_start_time(eq_start, sw, routes_in_sw, file)

    def servers_equal_start_time(self, eq_start, sw, routes_in_sw, file) :
        for it in itertools.combinations(eq_start, 2) :
            self.one_server(routes_in_sw, it[1][1:], sw, file, '+')
            file.write(' - ')
            self.one_server(routes_in_sw, it[0][1:], sw, file, '-')
            file.write(' >= '+str(self.rho_s)+' * t'+it[1][1:]+' - ')
            file.write(str(self.rho_s)+' * t'+it[0][1:]+' - '+str(self.b_s)+';\n')
            self.lengthLP += 1

    def one_server(self, routes_in_sw, time, sw, file_name, elem) :
        flag = False
        for route in routes_in_sw :
            if flag : 
                file_name.write(' '+elem+' ')
            file_name.write('F'+str(route)+'s'+str(sw)+'t'+time)
            flag = True

    def writeDelayConstraints(self, task, pos, route, file) :
        file.write('max: t0-u;\n\n')
        file.write('t'+task[pos-1]+' <= u;\n'+'u <= t'+task[pos]+';\n\n')
        file.write('F'+str(route.number)+'s'+str(route.path[len(route.path)-1])+'t0 <= F'+str(route.number)+'s0u;\n')
        self.lengthLP += 2
        file.write('\n//arrival delay \n')
        for time in task :
            elem1 = elem2 = '0'
            if (pos > task.index(time)) :
                file.write('F'+str(route.number)+'s0u - F'+str(route.number)+'s0t'+time)
                elem1 = 'u'
                elem2 = 't'+time
            else:
                file.write('F'+str(route.number)+'s0t'+time+' - F'+str(route.number)+'s0u')
                elem1 = 't'+time
                elem2 = 'u'
            file.write(' <= '+str(route.rho_a)+' * '+elem1+' - '+str(route.rho_a)+' * '+elem2+' + '+str(route.b_a)+';\n')
            self.lengthLP += 1
        file.write('\n')


#______________________MAIN______________________

input_file = open("test.json", "r")
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
    if 'statistic' in curr :
        routes_list[i].defineDistribution(curr['statistic'], web['chi_square'])
    elif 'rho_a' in curr and 'b_a' in curr :
        routes_list[i].rho_a = curr['rho_a']
        routes_list[i].b_a = curr['b_a']
        print('rho_a = ', routes_list[i].rho_a, ' b_a = ', routes_list[i].b_a)
    else :
        print('Not enof information about route ', i + 1)
        exit(0)
    i += 1

route_time = dict()
time_routes_switches = dict()
for i in range(len(routes_list)) :
    #создаем множество времен для потока, который вычисляем
    main_time = topo.formRouteTime(routes_list[i])
    #создаем множества времен для каждого потока и внутри для каждого свитча
    time_routes_switches[i] = topo.formSwitchesTime(main_time, routes_list) #аналог generateTime
    #формируем список возможных задач для вычисляеого потока
    route_time[i] = topo.timeConstraints(main_time)

max_delay = 0.0
for key in route_time.keys() :
    flow_max_delay = 0.0
    #для одного и того же потока перебираем варианты задач
    for task in route_time[key] :
        #создаем все неравенства без учета положения задержки для одной задачи
        service_file = open("help.txt", "w")
        topo.createLP(task, time_routes_switches[key], service_file, routes_list)
        service_file.close()
        #перебираем позицию для задержки
        for i in range(1, len(task)) :
            #print(task, ' pos u = ', i)
            LP_file = open("lp_file.txt", "w")
            #вписываем в файл всю информацию о задержке
            topo.writeDelayConstraints(task, i, routes_list[key], LP_file)
            service_file = open("help.txt", "r")
            #переписываем остальные неравенства для данной задачи
            rewrite_services(service_file, LP_file)
            service_file.close()
            LP_file.close()
            #отправляем на вычислени в lp_solver
            args = ["./../lp_solve_5.5.2.5_exe_ux64/lp_solve", "lp_file.txt"]
            process = subprocess.Popen(args, stdout=subprocess.PIPE)
            data = process.communicate()
            words = data[0].split()
            if words[0] == "This" :
                print('flow = ', key,' : ', data[0])
                continue
            if float(words[4]) > flow_max_delay :
                flow_max_delay = float(words[4])      
    print("For flow ", routes_list[key].number, " max delay = ", flow_max_delay)
    if flow_max_delay > max_delay :
        max_delay = flow_max_delay
print("Max delay in slice - ", max_delay)
print("Number of linear constraints : ", topo.lengthLP)
input_file.close()
