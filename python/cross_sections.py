import os

# Loads cross sections from data/cross_sections.txt into a dictionary
cross_sections = {}
with open(os.path.expandvars("$CMSSW_BASE/src/MonoPhoton/DASAnalysis/data/cross_sections.txt")) as f:
	for line in f:
		if line[0] == "#":
			continue
		contents = line.split()
		subsample = contents[0]
		xs = float(contents[4])
		cross_sections[subsample] = xs
