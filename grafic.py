import glob
import re
import matplotlib.pyplot as plot
import json

OutputFiles_lbl = glob.glob('lbl_output/*')
OutputFiles_lbl.sort()
InputFiles_lbl = glob.glob('lbl_input/*')
InputFiles_lbl.sort()
OutputFiles_ff = glob.glob('ff_output/*')
OutputFiles_ff.sort()
InputFiles_ff = glob.glob('ff_input/*')
InputFiles_ff.sort()
OutputFiles_d = glob.glob('dumbbell_output/*')
OutputFiles_d.sort()
InputFiles_d = glob.glob('dumbbell_input/*')
InputFiles_d.sort()

x_ff = []
x_lbl = []
x_d = []
res_ff = []
res_lbl = []
res_d = []

fig, ax = plot.subplots()

for i in range(len(OutputFiles_lbl)):
    output_file = open(str(OutputFiles_lbl[i]), "r")
    line_list = output_file.readlines()
    if len(line_list) < 8:
        continue
    leng = len(line_list)
    all_time = re.findall("[0-9]+", line_list[leng-1])
    res_lbl.append(float(all_time[0]))
    input_file = open(str(InputFiles_lbl[i]), "r")
    js = json.load(input_file)
    x_lbl.append(len(js['topology']['links'])/len(js['topology']['switches']))


for i in range(len(OutputFiles_ff)):
    output_file = open(str(OutputFiles_ff[i]), "r")
    line_list = output_file.readlines()
    if len(line_list) < 8:
        continue
    leng = len(line_list)
    all_time = re.findall("[0-9]+", line_list[leng-1])
    res_ff.append(float(all_time[0]))
    input_file = open(str(InputFiles_ff[i]), "r")
    js = json.load(input_file)
    x_ff.append(len(js['topology']['links'])/len(js['topology']['switches']))


for i in range(len(OutputFiles_d)):
    output_file = open(str(OutputFiles_d[i]), "r")
    line_list = output_file.readlines()
    if len(line_list) < 8:
        continue
    leng = len(line_list)
    all_time = re.findall("[0-9]+", line_list[leng-1])
    res_d.append(float(all_time[0]))
    input_file = open(str(InputFiles_d[i]), "r")
    js = json.load(input_file)
    x_d.append(len(js['topology']['links'])/len(js['topology']['switches']))
    


plot.xlabel('Связность топологии')
plot.ylabel('Время вычисления задержки, (с)')
ax.plot(x_lbl, res_lbl, c='blue', linestyle='--', marker='.', label='layer-by-layer')
ax.plot(x_ff, res_ff, c='red', linestyle='-', marker='.', label='feed-forward')
ax.plot(x_d, res_d, c='green', linestyle=':', marker='.', label='dumbbell')
ax.legend(loc='best')
#plot.scatter(x, res, c = 'blue', s = 5)
#plot.scatter(t, arival2, c = 'green', s = 5)
#plot.scatter(t, service, c = 'red', s = 5)
plot.savefig('test.png')
plot.show()