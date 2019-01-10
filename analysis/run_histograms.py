import os
import sys
from ROOT import TFile

# Load python modules
from MonoPhoton.DASAnalysis import input_samples
from MonoPhoton.DASAnalysis.cross_sections import cross_sections
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/MonoPhoton/DASAnalysis/analysis"))
from monophoton_histogrammer import MonoPhotonHistogrammer

if __name__ == "__main__":
	# Command line arguments
	import argparse
	parser = argparse.ArgumentParser(description='Make histograms for monophoton analysis')

	input_group = parser.add_mutually_exclusive_group()
	input_group.add_argument('--samples', type=str, help='Run over a list of samples (comma-separated)')
	input_group.add_argument('--subsamples', type=str, help='Run over a list of subsamples (comma-separated)')
	input_group.add_argument('--all', action='store_true', help='Run over all samples')

	action_group = parser.add_mutually_exclusive_group()
	action_group.add_argument('--run', action='store_true', help="Run the histogrammer")
	action_group.add_argument('--condor_run', action='store_true', help="Run the histogrammer on condor")
	action_group.add_argument('--condor_dryrun', action='store_true', help="Setup the histogrammer on condor, but don't run")
	action_group.add_argument('--combine_outputs', action='store_true', help="Combine outputs (subsamples into samples, plus apply luminosity normalization factors)")

	parser.add_argument('--output_dir', type=str, default=os.path.expandvars("$CMSSW_BASE/../data/histograms/"))
	parser.add_argument('--max_events', type=int, default=-1, help='Limit number of events processed')
	args = parser.parse_args()

	# Create list of input samples and subsamples
	subsamples = []
	if args.samples:
		samples = args.samples.split(",")
		for sample in samples:
			subsamples.extend(input_samples.subsamples[sample])
	elif args.all:
		samples = input_samples.all_samples
		for sample in samples:
			subsamples.extend(input_samples.subsamples[sample])
	elif args.subsamples:
		if args.combine_outputs:
			print "[run_histograms] ERROR : For --combine_outputs, you have to specify --all or --samples <list of samples>, not --subsamples."
		samples = []
		subsamples = args.subsamples.split(",")

	# Make a working directory for temporary/intermediate files
	os.system("mkdir -pv {}".format(args.output_dir))

	if args.run:
		for subsample in subsamples:
			print "[run_histograms] INFO : Processing subsample {}".format(subsample)
			histogrammer = MonoPhotonHistogrammer(is_data=("data" in subsample.lower()))
			hEvents = None
			for input_file in input_samples.subsample_files[subsample]:
				histogrammer.add_file(input_file)

				# Keep track of the number of generated events corresponding to the MC sample file 
				f = TFile.Open(input_file, "READ")
				if not hEvents:
					hEvents = f.Get("ggNtuplizer/hEvents").Clone()
					hEvents.SetDirectory(0)
				else:
					hEvents.Add(f.Get("ggNtuplizer/hEvents"))
				f.Close()

			os.system("mkdir -pv {}".format(args.output_dir))
			histogrammer.set_output_path("{}/subsample_histograms_{}.root".format(args.output_dir, subsample))

			histogrammer.start()
			histogrammer.run(max_events=args.max_events)
			histogrammer.finish()

			# Add to the output file the histogram for keeping track of the number of input events
			# WARNING : David thinks these histograms have 2x the number of events...??? For now, used events_processed instead?
			f = TFile("{}/subsample_histograms_{}.root".format(args.output_dir, subsample), "UPDATE")
			hEvents.Write()
			f.Close()

	elif args.condor_run or args.condor_dryrun:
		# Make a tarball of the CMSSW area
		os.system("csub --tar_only --cmssw")

		# Submit one HTCondor job per subsample
		# - It would be a lot faster to split the subsamples into subjobs, too, but we'll keep things simple for the DAS exercise.
		for subsample in subsamples:
			run_script_path = "{}/run_{}.sh".format(args.output_dir, subsample)
			run_script = open(run_script_path, 'w')
			run_script.write("#!/bin/bash\n")
			run_script.write("python $CMSSW_BASE/src/MonoPhoton/DASAnalysis/analysis/run_histograms.py --run --output_dir . --subsamples {} --max_events {}\n".format(subsample, args.max_events))
			run_script.close()

			csub_script_path = "{}/csub_{}.sh".format(args.output_dir, subsample)
			csub_script = open(csub_script_path, 'w')
			csub_script.write("#!/bin/bash\n")
			csub_script.write("csub {} --cmssw --no_retar -t espresso -d {}\n".format(run_script_path, args.output_dir))
			csub_script.close()

			if args.condor_run:
				os.system("source {}".format(csub_script_path))

	elif args.combine_outputs:
		print cross_sections
		# Add up subsample histograms, and scale to luminosity
		for sample in samples:
			sample_file = TFile("{}/histograms_{}.root".format(args.output_dir, sample), "RECREATE")
			hists = {}

			for i, subsample in enumerate(input_samples.subsamples[sample]):
				subsample_file = TFile("{}/subsample_histograms_{}.root".format(args.output_dir, subsample))

				# For MC samples, get the luminosity normalization factor
				if sample != "data":
					input_nevents = subsample_file.Get("events_processed").Integral()
					lumi_sf = 2260. * cross_sections[subsample] / input_nevents
					print "For subsample {}, lumi sf = {} * {} / {} = {}".format(subsample, 2260., cross_sections[subsample], input_nevents, lumi_sf)
				else:
					lumi_sf = 1.

				# First subsample: create the output sample file, and make a list of histograms to include
				if i == 0:
					hist_names = []
					for key in subsample_file.GetListOfKeys():
						if "TH" in key.GetClassName():
							hist_names.append(key.ReadObj().GetName())
					
				for hist_name in hist_names:
					subsample_hist = subsample_file.Get(hist_name)
					if not subsample_hist:
						print "ERROR : Couldn't find histogram {} in file {}".format(hist_name, subsample_file.GetPath())
					subsample_hist.Scale(lumi_sf)
					if i == 0:
						hists[hist_name] = subsample_hist.Clone()
						hists[hist_name].SetDirectory(0)
					else:
						hists[hist_name].Add(subsample_hist)
			# End loop over subsamples

			sample_file.cd()
			for hist_name, hist in hists.iteritems():
				hist.Write()

