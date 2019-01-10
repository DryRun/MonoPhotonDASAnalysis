# Split up the data input txt file into subjobs of 40 files each
import os
import sys
import math

input_files = []
with open("Data_2015D_all.txt", 'r') as f:
	for line in f:
		input_files.append(line)

files_per_job = 100
n_subjobs = int(math.ceil(1. * len(input_files) / files_per_job))
for i_subjob in xrange(n_subjobs):
	with open("Data_2015D_subjob{}.txt".format(i_subjob), 'w') as f:
		for di_file in xrange(files_per_job):
			i_file = i_subjob * files_per_job + di_file
			if i_file >= len(input_files):
				break
			f.write(input_files[i_file])
