import glob
import re
import matplotlib.pyplot as plot

InputFiles = glob.glob('output/*')
InputFiles.sort()

fig, ax = plot.subplots()

x = list(i for i in range(1,51))
res_25 = []
res_20 = []
res_30 = []

for file in InputFiles:
    input_file = open(str(file), "r")
    a = re.findall("[0-9]+",str(file))
    line_list = input_file.readlines()
    if len(line_list) < 8:
        continue
    leng = len(line_list)
    all_con = re.findall("[0-9]+", line_list[leng-2])
    all_time = re.findall("[0-9]+", line_list[leng-1])
    if int(a[0]) == 20 :
        res_20.append(float(all_time[0]))
    if int(a[0]) == 25 :
        res_25.append(float(all_time[0]))
    if int(a[0]) == 30 :
        res_30.append(float(all_time[0]))
    


plot.xlabel('Количество потоков')
plot.ylabel('Время вычисления задержки, (с)')
ax.plot(x, res_30, c = 'green', label = '30 обработчиков', linestyle=':', marker='.')
ax.plot(x, res_25, c = 'blue', label = '25 обработчиков', linestyle='--', marker='.')
ax.plot(x, res_20, c = 'red', label = '20 обработчиков', linestyle='-', marker='.')
ax.legend(loc='best')
#ax.set_xscale('log')
#plot.scatter(x, res, c = 'blue', s = 5)
#plot.scatter(t, arival2, c = 'green', s = 5)
#plot.scatter(t, service, c = 'red', s = 5)
plot.savefig('time_of_const_10_20_30.png', dpi=300)
plot.show()
