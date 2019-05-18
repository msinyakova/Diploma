import glob
import re
import matplotlib.pyplot as plot

InputFiles = glob.glob('ff_output/*')
InputFiles.sort()

x = []
res = []

for file in InputFiles:
    input_file = open(str(file), "r")
    a = re.findall("[0-9]+",str(file))
    line_list = input_file.readlines()
    if len(line_list) < 8:
        continue
    x.append(int(a[1]))
    gene_time = re.findall("[0-9]+", line_list[1])
    solve_time = re.findall("[0-9]+", line_list[4])
    task_number = re.findall("[0-9]+", line_list[3])
    number_con = re.findall("[0-9]+", line_list[5])
    all_con = re.findall("[0-9]+", line_list[6])
    all_time = re.findall("[0-9]+", line_list[7])
    res.append(float(number_con[0]))
    


plot.xlabel('Количество связей в сети')
plot.ylabel('Количество ограничений для задачи ЛП')
plot.plot(x, res, c = 'red')
#plot.scatter(x, res, c = 'blue', s = 5)
#plot.scatter(t, arival2, c = 'green', s = 5)
#plot.scatter(t, service, c = 'red', s = 5)
plot.savefig('ff_con2.png')
plot.show()