import subprocess
import glob
import os
import argparse


'''files = glob.glob('input/*')
for f in files:
    os.remove(f)

files = glob.glob('output/*')
for f in files:
    os.remove(f)

args_gene = ["python3", "generation_linear.py"]

process_gene = subprocess.call(args_gene)'''

parser = argparse.ArgumentParser()
parser.add_argument('size', nargs='?', default='0')
step = parser.parse_args()

InputFiles = glob.glob('input/*')
InputFiles.sort()

index = int(step.size)

#for file in InputFiles :
while index < len(InputFiles) :
	file = str(InputFiles[index])
	print(file)
	args = ["python3", "diploma.py", file, step.size]
	number = file[10:len(file)-5]
	output_name = "output/res" + number + ".txt"
	output_file = open(output_name, "w")
	process = subprocess.Popen(args, stdout=output_file)
	process.wait()
	output_file.close()
	index += 19

	
