#!/usr/bin/python3

import json
import math
import subprocess
import itertools
import time
import argparse
import csv
import objects


def rewrite_services(file_from, file_to):
    for line in file_from:
        file_to.write(line)


def my_sort(sorted_list, according_list):
    new_list = []
    index_list = []
    for elem in sorted_list:
        index_list.append(according_list.index(elem))
    index_list.sort()
    for index in index_list:
        new_list.append(according_list[index])
    return new_list


class Route:
    def __init__(self, path_, epsilon, rate_, number_):
        self.path = path_
        self.eps = epsilon
        self.rate = rate_
        self.number = number_
        self.rho_a = 0
        self.b_a = 0

    def define_distribution(self, stats, chi_square):
        sum_f = sum_xf = 0
        f_list = []
        time_t = 0
        for st in stats:
            it = float(st[0])
            f_list.append(it)
            sum_f += it
            sum_xf += time_t * it
            time_t += 1
        lambda_medium = sum_xf / sum_f
        k = 0
        r = 0
        for i in range(len(f_list)):
            if f_list[i] < lambda_medium:
                r += 1
            p_i = lambda_medium ** i * math.exp(-lambda_medium) / math.factorial(i)
            k += (f_list[i] - sum_f * p_i) ** 2 / (sum_f * p_i)
        freedom_degree = len(f_list) - 2 - r
        # print('K_критическое = ', chi_square[freedom_degree], ' K_наблюдаемое = ', K)
        if chi_square[freedom_degree] >= k:
            # print('Poisson distribution with lambda = ', lambda_medium)
            self.rho_a = lambda_medium
            sigma_a = 0
            theta = 100000
            self.b_a = sigma_a - 1 / theta * (
                        math.log(self.eps) + math.log(1 - math.exp(-theta * (self.rate - self.rho_a))))
            # print('rho_a = ', self.rho_a, ' b_a = ', self.b_a)
        else:
            print('Not poisson distribution')
            self.rho_a = 0.67
            self.b_a = 1


class MyTime:
    def __init__(self, string=''):
        self.elem = str(string)
        self.list = self.parsing(str(string)).copy()

    def __add__(self, string):
        if str(string) == "":
            return self
        self.elem += ('_' + str(string))
        self.list.extend(self.parsing(str(string)))
        return self

    def __getitem__(self, key):
        if type(key) == int:
            return self.list[key]
        if type(key) == slice:
            result = ""
            start = 0 if key.start is None else key.start
            stop = len(self.list) if key.stop is None else key.stop
            step = 1 if key.step is None else key.step
            flag = False
            while start < stop:
                if flag:
                    result += '_'
                result += self.list[start]
                start += step
                flag = True
            return result

    def __str__(self):
        return self.elem

    def __repr__(self):
        return self.elem

    def __call__(self):
        return self.elem

    def __eq__(self, string):
        if type(string) == str:
            return self.elem == string
        return self.elem == string.elem

    def __ne__(self, string):
        return not (self.__eq__(string))

    def parsing(self, string):
        words = list()
        elem = ''
        for char in string:
            if char != '_':
                elem += char
            else:
                words.append(elem)
                elem = ''
        words.append(elem)
        return words


class Tree:
    def __init__(self, value_, next_=None):
        self.value = value_
        self.next = next_

    def __repr__(self):
        return self.value.elem

    def __str__(self):
        return self.value.elem


class Topology:
    def __init__(self, switches_, links_, queue_):
        self.switches = switches_
        self.links = links_
        self.queue = queue_
        self.lengthLP = 0
        self.rho_s = 0
        self.b_s = 0
        self.leaves = []
        self.tree = 0
        self.route_time_constraints = []

    def define_service_curve(self, slice_list, slice_rate, slice_priority):
        b_s_ = 0
        for i in range(len(self.queue)):
            if i < slice_priority:
                b_s_ += slice_list[self.queue[i]].delay()
            else:
                break
        self.rho_s = slice_rate
        self.b_s = b_s_

    def form_route_time(self, route):
        first_tree = Tree(MyTime('0'))
        end = route.path[len(route.path) - 1]
        self.tree = Tree(MyTime(end), first_tree)
        self.leaves = [self.tree]
        time_t = list()
        time_t.append(MyTime(end))
        vertex = list()
        vertex.append(MyTime(end))
        while vertex != list():
            elem = vertex.pop(0)
            for lk in self.links:
                if elem[0] == str(lk[1]):
                    new_elem = MyTime(lk[0]) + elem
                    time_t.append(new_elem)
                    vertex.append(new_elem)

                    new_tree = Tree(new_elem, self.tree)
                    self.leaves.remove(self.tree)
                    self.leaves.append(new_tree)
                    self.tree = new_tree
        time_t.append(MyTime('0'))
        return time_t

    def form_switches_time(self, time_t, routes_list):
        routes_dict = dict()
        number = 1
        for route in routes_list:
            one_route = dict()
            input_variables = list()
            for sw in self.switches:
                if sw not in route.path:
                    continue
                one_switch = list()
                for t in time_t:
                    if t[0] != str(sw):
                        continue
                    one_switch.append(t)
                    if t not in input_variables:
                        input_variables.append(t)
                    if t[1:] in time_t:
                        one_switch.append(t[1:])
                        if t[1:] not in input_variables:
                            input_variables.append(t[1:])
                    elif t[1:] == '':
                        one_switch.append(MyTime('0'))
                        if MyTime('0') not in input_variables:
                            input_variables.append(MyTime('0'))
                one_route[str(sw)] = one_switch
            one_route['0'] = input_variables
            routes_dict[number] = one_route
            number += 1
        return routes_dict

    def start_serv(self, time_t, elem):
        equal_start = dict()
        for i in range(len(time_t)):
            if time_t[i] != elem and time_t[i][0] == elem[0]:
                equal_start[i] = time_t[i]
        return equal_start

    def equal_time(self, time_t, pos1, pos2):
        sub_pos1 = time_t.index(time_t[pos1][1:])
        sub_pos2 = time_t.index(time_t[pos2][1:])
        if sub_pos1 <= pos1 or sub_pos1 <= pos2:
            return False
        if sub_pos2 <= pos1 or sub_pos2 <= pos2:
            return False
        return True

    def different_time(self, time_t, pos1, pos2):
        if pos1 > pos2:
            pos1, pos2 = pos2, pos1
        sub_pos1 = time_t.index(time_t[pos1][1:])
        sub_pos2 = time_t.index(time_t[pos2][1:])
        if (sub_pos1 > pos1) and (sub_pos1 < pos2 < sub_pos2):
            return True
        return False

    def correct_time(self, time_t):
        swap = list()
        for i in range(len(time_t)):
            if time_t[len(time_t) - 1] != MyTime('0'):
                return False
            if time_t[i][1:] == '':
                continue
            if time_t.index(time_t[i][1:]) <= i:
                return False
            position = self.start_serv(time_t, time_t[i])
            for key in position.keys():
                equal = self.equal_time(time_t, i, key)
                if not equal and not self.different_time(time_t, i, key):
                    return False
                if equal and i < key and time_t[i][1] > time_t[key][1]:
                    swap.append(tuple((i, key)))
        for it in swap:
            time_t[it[0]], time_t[it[1]] = time_t[it[1]], time_t[it[0]]
        return True

    def build_time_constraints(self, constraints, pos):
        if self.leaves == list():
            if self.correct_time(constraints):
                if constraints not in self.route_time_constraints:
                    self.route_time_constraints.append(constraints)
        else:
            elem = self.leaves.pop(0)
            if elem.next is not None:
                self.leaves.append(elem.next)
            constraints[pos] = elem.value
            self.build_time_constraints(constraints, pos + 1)

    def time_constraints(self, time_t):
        self.route_time_constraints = list()
        constraints = list()
        pos = 0
        for i in range(len(time_t)):
            constraints.append('0')
        self.build_time_constraints(constraints, pos)
        return self.route_time_constraints

    def create_lp(self, task, routes_dict, routes_list, topo):
        help_str = '//time\n'
        help_str += topo.write_time(task)
        for route in routes_list:
            help_str += ("\n//flow " + str(route.number) + '\n')
            help_str += topo.generate_constraints(task, routes_dict, route)
            help_str += ("\n//arrival " + str(route.number) + "\n")
            help_str += topo.generate_arrival(task, route)
        help_str += "\n//servers\n"
        help_str += topo.generate_servers(task, routes_list)
        return help_str

    def expression_sign(self, task, i):
        if task[i][0] == task[i + 1][0]:
            return ' = '
        return ' <= '

    def write_time(self, task):
        help_str = ""
        for i in range(len(task) - 1):
            help_str += ('t' + task[i].elem + self.expression_sign(task, i) + 't' + task[i + 1].elem + ';\n')
            self.lengthLP += 1
        return help_str

    def generate_constraints(self, task, routes_dict, route):
        help_str = ""
        path = route.number
        for sw in routes_dict[path]:
            time_t = my_sort(routes_dict[path][sw], task) if sw != '0' else task
            help_str += ('//sw ' + str(sw) + '\n')
            pos = 0
            for i in range(len(time_t) - 1):
                # non_decreasing functions
                help_str += ('F' + str(path) + 's' + sw + 't' + time_t[i].elem)
                help_str += (self.expression_sign(task, i))
                help_str += ('F' + str(path) + 's' + sw + 't' + time_t[i + 1].elem + ';\n')
                self.lengthLP += 1
                if sw == '0':
                    continue
                # start_backlog
                if sw == time_t[i][0]:
                    previos_pos = route.path.index(int(sw))
                    previos_sw = '0' if previos_pos == 0 else str(route.path[previos_pos - 1])
                    help_str += ('F' + str(path) + 's' + previos_sw + 't' + time_t[i].elem + ' = ')
                    help_str += ('F' + str(path) + 's' + sw + 't' + time_t[i].elem + ';\n')
                    self.lengthLP += 1
                # flow_contains
                else:
                    help_str += ('F' + str(path) + 's' + sw + 't' + time_t[i].elem + ' <= ')
                    help_str += ('F' + str(path) + 's0t' + time_t[i].elem + ';\n')
                    self.lengthLP += 1
                pos = i
            if sw != '0' and (pos + 1) < len(time_t):
                help_str += ('F' + str(path) + 's' + sw + 't' + time_t[pos + 1].elem + ' <= ')
                help_str += ('F' + str(path) + 's0t' + time_t[pos + 1].elem + ';\n')
                self.lengthLP += 1
        return help_str

    def generate_arrival(self, task, route):
        help_str = ""
        path = route.number
        for it in itertools.combinations(reversed(task), 2):
            if it[0] == it[1]:
                continue
            help_str += ('F' + str(path) + 's0t' + it[0].elem + ' - F' + str(path) + 's0t' + it[1].elem)
            help_str += (' <= ' + str(route.rho_a) + ' * t' + it[0].elem + ' - ' + str(route.rho_a) + ' * t' + it[
                1].elem + ' + ' + str(route.b_a) + ';\n')
            self.lengthLP += 1
        return help_str

    def choose_routes(self, sw, routes_list):
        routes_in_sw = list()
        for route in routes_list:
            if sw in route.path:
                routes_in_sw.append(route.number)
        return routes_in_sw

    def generate_servers(self, task, routes_list):
        help_str = ""
        for sw in self.switches:
            eq_start = list()
            previos = 0
            routes_in_sw = self.choose_routes(sw, routes_list)
            for time_t in task:
                if time_t == MyTime('0'):
                    continue
                if time_t[0] != str(sw):
                    continue
                t = MyTime('0') if time_t[1:] == '' else MyTime(time_t[1:])
                help_str += self.one_server(routes_in_sw, t, sw, '+')
                help_str += ' - '
                help_str += self.one_server(routes_in_sw, time_t, sw, '-')
                help_str += (' >= ' + str(self.rho_s) + ' * t' + t.elem + ' - ')
                help_str += (str(self.rho_s) + ' * t' + time_t.elem + ' - ' + str(self.b_s) + ';\n')
                self.lengthLP += 1
                if eq_start == list():
                    eq_start.append(time_t)
                    previos = task.index(time_t)
                elif task.index(time_t) - previos <= 1:
                    eq_start.append(time_t)
                    previos = task.index(time_t)
            help_str += self.servers_equal_start_time(eq_start, sw, routes_in_sw)
        return help_str

    def servers_equal_start_time(self, eq_start, sw, routes_in_sw):
        help_str = ""
        for it in itertools.combinations(eq_start, 2):
            help_str += self.one_server(routes_in_sw, MyTime(it[1][1:]), sw, '+')
            help_str += ' - '
            help_str += self.one_server(routes_in_sw, MyTime(it[0][1:]), sw, '-')
            help_str += (' >= ' + str(self.rho_s) + ' * t' + it[1][1:] + ' - ')
            help_str += (str(self.rho_s) + ' * t' + it[0][1:] + ' - ' + str(self.b_s) + ';\n')
            self.lengthLP += 1
        return help_str

    def one_server(self, routes_in_sw, time_t, sw, elem):
        help_str = ""
        flag = False
        for route in routes_in_sw:
            if flag:
                help_str += (' ' + elem + ' ')
            help_str += ('F' + str(route) + 's' + str(sw) + 't' + time_t.elem)
            flag = True
        return help_str

    def write_delay_constraints(self, task, pos, route, file):
        file.write('max: t0-u;\n\n')
        file.write('t' + task[pos - 1].elem + ' <= u;\n' + 'u <= t' + task[pos].elem + ';\n\n')
        file.write('F' + str(route.number) + 's' + str(route.path[len(route.path) - 1]) + 't0 <= F' + str(
            route.number) + 's0u;\n')
        self.lengthLP += 2
        file.write('\n//arrival delay \n')
        for time_t in task:
            if pos > task.index(time_t):
                file.write('F' + str(route.number) + 's0u - F' + str(route.number) + 's0t' + time_t.elem)
                elem1 = 'u'
                elem2 = 't' + time_t.elem
            else:
                file.write('F' + str(route.number) + 's0t' + time_t.elem + ' - F' + str(route.number) + 's0u')
                elem1 = 't' + time_t.elem
                elem2 = 'u'
            file.write(
                ' <= ' + str(route.rho_a) + ' * ' + elem1 + ' - ' + str(route.rho_a) + ' * ' + elem2 + ' + ' + str(
                    route.b_a) + ';\n')
            self.lengthLP += 1
        file.write('\n')


# ______________________MAIN______________________

def main():
    total_time_start = time.time()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default='input.json')
    parser.add_argument('pos', nargs='?', default='0')
    input_param = parser.parse_args()
    print(input_param.file)
    input_file = open(str(input_param.file), "r")
    web = json.load(input_file)
    
    tp_help = web['topology']
    topo = Topology(tp_help['switches'], tp_help['links'], tp_help['queue'])
    
    slice_list = {}
    sls_help = web['slices']
    for curr in sls_help:
        slice_list[curr['id']] = Slices(curr['id'], curr['rate'], web["bandwidth"])
    
    slice_info = web['slice']
    slice_rate = slice_info['rate']
    slice_priority = slice_info['priority']
    topo.define_service_curve(slice_list, slice_rate, slice_priority)
    
    routes_list = []
    i = 0
    for curr in slice_info['routes']:
        routes_list.append(Route(curr['path'], curr['epsilon'], slice_rate, i + 1))
        if 'statistic' in curr:
            with open(curr['statistic'], 'r') as f:
                reader = csv.reader(f)
                stat_list = list(reader)
            routes_list[i].define_distribution(stat_list, web['chi_square'])
        elif 'rho_a' in curr and 'b_a' in curr:
            routes_list[i].rho_a = curr['rho_a']
            routes_list[i].b_a = curr['b_a']
        else:
            print('Not enough information about route ', i + 1)
            exit(0)
        i += 1
    
    time_gene_start = time.time()
    # print("Time before generation: ", time_gene_start - total_time_start)
    
    route_time = dict()
    time_routes_switches = dict()
    for i in range(len(routes_list)):
        # создаем множество времен для потока, который вычисляем
        main_time = topo.form_route_time(routes_list[i])
        # создаем множества времен для каждого потока и внутри для каждого свитча
        time_routes_switches[i] = topo.form_switches_time(main_time, routes_list)
        # формируем список возможных задач для вычисляеого потока
        route_time[i] = topo.time_constraints(main_time)
    time_gene_finish = time.time() - time_gene_start
    print("Time for generation constraints = ", time_gene_finish)
    
    all_constraints_number = 0
    max_file_constraints_number = 0
    files_number = 0
    max_delay = 0.0
    time_lp_solver_finish = 0.0
    for key in route_time.keys():
        flow_max_delay = 0.0
        # для одного и того же потока перебираем варианты задач
        for task in route_time[key]:
            # time_create_1 = time.time()
            # создаем все неравенства без учета положения задержки для одной задачи
            help_str = topo.create_lp(task, time_routes_switches[key], routes_list, topo)
            # print(task)
            based_constraints_number = topo.lengthLP
            # time_create = time.time() - time_create_1
            # print("Time for creating LP:", time_create)
            # перебираем позицию для задержки
            for i in range(1, len(task)):
                # time_write1 = time.time()
                file_lp = "LP/lp_file" + input_param.pos + ".txt"
                lp_file = open(file_lp, "w")
                files_number += 1
                # вписываем в файл всю информацию о задержке
                topo.write_delay_constraints(task, i, routes_list[key], lp_file)
                # переписываем остальные неравенства для данной задачи
                lp_file.write(help_str)
                lp_file.close()
                # time_write = time.time() - time_write1
                # print("Time for write LP_file:", time_write)
    
                # отправляем на вычислени в lp_solver
                time_lp_solver_start = time.time()
                args = ["./lp_solver/lp_solve", file_lp]
                process = subprocess.Popen(args, stdout=subprocess.PIPE)
                data = process.communicate()
                time_lp_solver_finish = max(time_lp_solver_finish, time.time() - time_lp_solver_start)
    
                # time_read_proc1 = time.time()
                words = data[0].split()
                if len(words) <= 4:
                    print('flow = ', key, ' : ', data[0])
                    continue
                if float(words[4]) > flow_max_delay:
                    flow_max_delay = float(words[4])
                all_constraints_number += topo.lengthLP
                max_file_constraints_number = max(max_file_constraints_number, topo.lengthLP)
                topo.lengthLP = based_constraints_number
                # time_read_proc = time.time() - time_read_proc1
                # print("Time after work:", time_read_proc)
                # break
            topo.lengthLP = 0
            # break
        if flow_max_delay > max_delay:
            max_delay = flow_max_delay
        # break
    # files_number = len(route_time) * len(route_time[1]) * (len(route_time[1][0])-1)
    print("Max delay in slice - ", max_delay)
    print("Number of files in linear programming : ", files_number)
    print("Time for calculating one file in lp_solver : ", time_lp_solver_finish)
    print("Max number of linear constraints in one file : ", max_file_constraints_number)
    print("Number of linear constraints in general: ", all_constraints_number)
    input_file.close()
    total_time_finish = time.time() - total_time_start
    print("Total time: ", total_time_finish)


if __name__ == "__main__":
    main()
