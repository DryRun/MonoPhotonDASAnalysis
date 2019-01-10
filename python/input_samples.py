# Paths to ntuples
# When run as an executable, globs the list of input files from EOS. This abuses the FUSE mount, so try not to do this...
# When loaded as a module, provides the paths of input ntuples as a dictionary.

# Nomenclature:
# - samples = top-level process names, i.e. the processes shown in the legends of the plots.
# - subsamples = actual MC samples. For GJets, this means the HT-binned samples; for others, it's just the sample name.

import os
import sys
from glob import glob

background_samples = ["WGJets", "ZLLGJets", "ZNuNuGJets", "WToMuNu", "WToTauNu", "GJets"] # WToENu
signal_samples = ["ADD1", "ADD2", "ADD3"]
all_samples = ["data"] + background_samples + signal_samples

# Subsamples: often a given process is split into subsamples, e.g. different data periods, or HT-binned MC
subsamples = {
	"ADD1":["ADD1"],
	"ADD2":["ADD2"],
	"ADD3":["ADD3"],
	"WGJets":["WGJets"],
	"ZLLGJets":["ZLLGJets"],
	"ZNuNuGJets":["ZNuNuGJets"],
	#"WToENu":["WToENu"],
	"WToMuNu":["WToMuNu"],
	"WToTauNu":["WToTauNu"],
	"GJets":["GJets_HT-100to200","GJets_HT-200to400","GJets_HT-400to600","GJets_HT-40to100","GJets_HT-600toInf"]
}
# Data is split into many subjobs, to facilitate pipelining on condor
subsamples["data"] = []
for i in xrange(22):
	subsamples["data"].append("Data_2015D_subjob{}".format(i))

def get_input_txt(subsample):
	return os.path.expandvars("$CMSSW_BASE/src/MonoPhoton/DASAnalysis/analysis/inputs/{}.txt".format(subsample))

prefix = "root://cmseos.fnal.gov//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls"
subsample_files = {}
for sample in all_samples:
	for subsample in subsamples[sample]:
		subsample_files[subsample] = []
		input_txt = get_input_txt(subsample)
		if os.path.isfile(input_txt):
			with open(input_txt, 'r') as f:
				for line in f:
					subsample_files[subsample].append(line.strip())



if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Tools for managing input ntuples')
	parser.add_argument('--glob_inputs', action='store_true', help='Glob the input files. Note that this makes use of the FUSE mount, which is strongly discouraged! Don\'t do this often.')
	args = parser.parse_args()

	if args.glob_inputs:
		subsample_folders = {}
		subsample_folders["Data_2015D_v3"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/Data_2015D_v3"
		subsample_folders["Data_2015D_v3_0"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/Data_2015D_v3_0"
		subsample_folders["Data_2015D_v4_1"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/Data_2015D_v4_1"
		subsample_folders["Data_2015D_v4_0"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/Data_2015D_v4_0"
		subsample_folders["Data_2015D_v4_2"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/Data_2015D_v4_2"
		subsample_folders["ADD1"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/ADDmonoPhoton_MD-1_d-3"
		subsample_folders["ADD2"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/ADDmonoPhoton_MD-2_d-3"
		subsample_folders["ADD3"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/ADDmonoPhoton_MD-3_d-3"
		subsample_folders["WGJets"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/WGJets_MonoPhoton_PtG-130_TuneCUETP8M1_13TeV-madgraph"
		subsample_folders["ZLLGJets"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/ZLLGJets_MonoPhoton_PtG-130_TuneCUETP8M1_13TeV-madgraph"
		subsample_folders["ZNuNuGJets"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/ZNuNuGJets_MonoPhoton_PtG-130_TuneCUETP8M1_13TeV-madgraph"
		subsample_folders["WToENu"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/WToENu_M-100_TuneCUETP8M1_13TeV-pythia8"
		subsample_folders["WToMuNu"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/WToMuNu_M-100_TuneCUETP8M1_13TeV-pythia8"
		subsample_folders["WToTauNu"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/WToTauNu_M-100_TuneCUETP8M1_13TeV-pythia8"
		subsample_folders["GJets_HT-100to200"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/GJets_HT-100to200"
		subsample_folders["GJets_HT-200to400"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/GJets_HT-200to400"
		subsample_folders["GJets_HT-400to600"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/GJets_HT-400to600"
		subsample_folders["GJets_HT-40to100"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/GJets_HT-40to100"
		subsample_folders["GJets_HT-600toInf"] = "/eos/uscms//store/user/cmsdas/2018/long_exercises/MonoPhoton/ggNtpls/GJets_HT-600toInf"

		for sample in all_samples:
			for subsample in subsamples[sample]:
				input_files = glob("{}/*root*".format(subsample_folders[subsample]))
				with open(get_input_txt(subsample), 'w') as input_txt:
					for input_file in input_files:
						input_txt.write("{}\n".format(input_file.replace("/eos/uscms/", "root://cmseos.fnal.gov/")))


