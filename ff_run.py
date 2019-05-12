import subprocess
import glob
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('size', nargs='?', default='0')
step = parser.parse_args()

InputFiles = glob.glob('ff_input/*')
InputFiles.sort()

index = int(step.size)

#for file in InputFiles :
while index < len(InputFiles) :
	file = str(InputFiles[index])
	print(file)
	args = ["python3", "diploma.py", file, step.size]
	number = file[10:len(file)-5]
	output_name = "ff_output/res" + number + ".txt"
	output_file = open(output_name, "w")
	process = subprocess.Popen(args, stdout=output_file)
	process.wait()
	output_file.close()
	index += 1

	
