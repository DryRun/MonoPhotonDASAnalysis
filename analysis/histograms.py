import os
import sys
import array
import math
import time
import datetime

from ROOT import *

# Load C++ libraries (for the ntuple reader class)
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMonoPhotonDASAnalysis.so"))

# Load our python modules
from MonoPhoton.DASAnalysis import input_samples

# Configure ROOT defaults
gROOT.SetBatch(kTRUE);
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)

class MonoPhotonHistogrammer:
	def __init__(self, tree_name="ggNtuplizer/EventTree", is_data=True):
		self._input_tree = TChain(tree_name)
		self._is_data = is_data

	def start(self):
		print "[MonoPhotonHistogrammer::start] INFO : In start()."

		self._selections = [] # [selection_name]
		self._histograms = {} # {selection_name : {histogram_name : histogram}}
		self._data = NtupleData(self._input_tree)
		self._data.isData(self._is_data)

		# Define selections and histograms
		self._selections.append("trigger_numerator")
		self._selections.append("trigger_denominator")
		self._selections.append("sr")

		pt_bins = array.array("d", [0., 75.0, 100.0, 125.0, 145., 155., 165., 175., 190.,250., 400., 700.0,1000.0])
		met_bins = array.array("d", [0., 130., 150., 170., 190., 250., 400., 700.0, 1000.0])
		for selection in self._selections:
			self._histograms[selection] = {}

			self._histograms[selection]["photon_pt"] = TH1D("{}_photon_pt".format(selection), "{}_photon_pt".format(selection), 100, 0., 1000.)
			self._histograms[selection]["photon_pt"].GetXaxis().SetTitle("#gamma p_{T} [GeV]")

			self._histograms[selection]["photon_eta"] = TH1D("{}_photon_eta".format(selection), "{}_photon_eta".format(selection), 40, -1.4442, 1.4442)
			self._histograms[selection]["photon_eta"].GetXaxis().SetTitle("#gamma #eta")

			self._histograms[selection]["photon_SCeta"] = TH1D("{}_photon_SCeta".format(selection), "{}_photon_SCeta".format(selection), 40, -1.4442, 1.4442)
			self._histograms[selection]["photon_SCeta"].GetXaxis().SetTitle("#gamma #eta_{SC}")

			self._histograms[selection]["photon_phi"] = TH1D("{}_photon_phi".format(selection), "{}_photon_phi".format(selection), 100, -2.*math.pi, 2.*math.pi)
			self._histograms[selection]["photon_phi"].GetXaxis().SetTitle("#gamma #phi")

			self._histograms[selection]["photon_SCphi"] = TH1D("{}_photon_SCphi".format(selection), "{}_photon_SCphi".format(selection), 100, -2.*math.pi, 2.*math.pi)
			self._histograms[selection]["photon_SCphi"].GetXaxis().SetTitle("#gamma #phi_{SC}")

			self._histograms[selection]["pfmet"] = TH1D("{}_photon_pfmet".format(selection), "{}_photon_pfmet".format(selection), 100, 0., 1000.)
			self._histograms[selection]["pfmet"].GetXaxis().SetTitle("PF MET [GeV]")

			self._histograms[selection]["dphi_photon_met"] = TH1D("{}_dphi_photon_met".format(selection), "{}_dphi_photon_met".format(selection), 100, -2.*math.pi, 2.*math.pi)
			self._histograms[selection]["dphi_photon_met"].GetXaxis().SetTitle("#Delta#phi(#gamma, PF MET)")

			self._histograms[selection]["njets"] = TH1D("{}_njets".format(selection), "{}_njets".format(selection), 21, -0.5, 20.5)
			self._histograms[selection]["njets"].GetXaxis().SetTitle("n_{jets}")

			self._histograms[selection]["leading_jet_pt"] = TH1D("{}_leading_jet_pt".format(selection), "{}_leading_jet_pt".format(selection), 50, 0., 1000.)
			self._histograms[selection]["leading_jet_pt"].GetXaxis().SetTitle("Leading jet p_{T} [GeV]")

			self._histograms[selection]["leading_jet_eta"] = TH1D("{}_leading_jet_eta".format(selection), "{}_leading_jet_eta".format(selection), 50, -5., 5.)
			self._histograms[selection]["leading_jet_eta"].GetXaxis().SetTitle("Leading jet #eta")

		self._events_processed = 0
		print "[MonoPhotonHistogrammer::start] INFO : Done with start()."


	def run(self, max_events=-1, first_event=0, nprint=-1):
		print "[MonoPhotonHistogrammer::run] INFO : In run()."

		total_entries = self._input_tree.GetEntries()
		if max_events > 0:
			limit_nevents = min(max_events, total_entries)
		else:
			limit_nevents = total_entries

		n_checkpoints = 20
		print_every = int(math.ceil(1. * limit_nevents / n_checkpoints))

		self.start_timer()
		for i in xrange(limit_nevents):
			self.print_progress(i, first_event, limit_nevents, print_every)
			self._data.GetEntry(i)
			self._events_processed += 1

			event_weight = 1.

			# Photon selection
			selected_photon = -1
			for i in xrange(self._data.nPho):
				if abs(self._data.phoSCEta[i]) < 1.4442 and self._data.phoID(i):
					selected_photon = i
					break

			# Skip events without a selected photon
			if selected_photon < 0:
				continue

			# Event selections
			selection_results = {}
			pass_backup_triggers = (
				self._data.photonTriggerResult(NtupleData.kHLT_Photon75)
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon90) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon120)
			)
			pass_signal_triggers = (
				self._data.photonTriggerResult(NtupleData.kHLT_Photon175) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon250_NoHE) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon300_NoHE) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon500) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon600) 
				or self._data.photonTriggerResult(NtupleData.kHLT_Photon165_HE10)
				or self._data.photonTriggerResult(NtupleData.kHLT_DoublePhoton60)
			)
			selection_results["trigger_denominator"] = pass_backup_triggers and self._data.pfMET > 140.
			selection_results["trigger_numerator"] = selection_results["trigger_denominator"] and pass_signal_triggers
			selection_results["sr"] = (
				pass_signal_triggers
				and (self._data.metFilters == 0)
				and (self._data.phoEt[selected_photon] > 175.)
			)

			# Histograms
			for selection in self._selections:
				if selection_results[selection]:
					self._histograms[selection]["photon_pt"].Fill(self._data.phoEt[selected_photon], event_weight)
					self._histograms[selection]["photon_eta"].Fill(self._data.phoEta[selected_photon], event_weight)
					self._histograms[selection]["photon_SCeta"].Fill(self._data.phoSCEta[selected_photon], event_weight)
					self._histograms[selection]["photon_phi"].Fill(self._data.phoPhi[selected_photon], event_weight)
					self._histograms[selection]["photon_SCphi"].Fill(self._data.phoSCPhi[selected_photon], event_weight)
					self._histograms[selection]["pfmet"].Fill(self._data.pfMET, event_weight)
					self._histograms[selection]["dphi_photon_met"].Fill(math.acos(math.cos(self._data.phoPhi[selected_photon] - self._data.pfMETPhi)), event_weight)
					self._histograms[selection]["njets"].Fill(self._data.nJet, event_weight)
					self._histograms[selection]["leading_jet_pt"].Fill(self._data.jetPt[0], event_weight)
					self._histograms[selection]["leading_jet_eta"].Fill(self._data.jetEta[0], event_weight)
		print "[MonoPhotonHistogrammer::run] INFO : In run()."

	def finish(self):
		print "[MonoPhotonHistogrammer::finish] INFO : In finish()."
		if not self._output_path:
			self._output_path = "output_{}.root".format(time.time())
			print "[MonoPhotonHistogrammer::finish] WARNING : No output path specified! Saving to {}".format(self._output_path)
		output_file = TFile(self._output_path, "RECREATE")
		for selection in self._selections:
			for histogram in sorted(self._histograms[selection].values(), key=lambda x: x.GetName()):
				histogram.Write()
		output_file.Close()
		print "[MonoPhotonHistogrammer::finish] INFO : Done with finish()."


	# Utilities
	def add_file(self, filename):
		self._input_tree.Add(filename)

	def set_output_path(self, output_path):
		self._output_path = output_path
		os.system("mkdir -pv {}".format(os.path.dirname(self._output_path)))

	def start_timer(self):
		self._ts_start = time.time()
		print "[MonoPhotonHistogrammer::start_timer] INFO : Start time: {}".format(datetime.datetime.fromtimestamp(self._ts_start).strftime('%Y-%m-%d %H:%M:%S'))

	def print_progress(self, this_event, first_event, last_event, print_every):
		if this_event % print_every == 0:
			print "[MonoPhotonHistogrammer::print_progress] INFO : Processing event {} / {}".format(this_event + 1, last_event)
			if this_event != first_event:
				if self._ts_start > 0 :
					elapsed_time = time.time() - self._ts_start
					estimated_completion = self._ts_start + (1. * elapsed_time * (last_event - first_event) / (this_event - first_event))
					m, s = divmod(elapsed_time, 60)
					h, m = divmod(m, 60)
					print "[MonoPhotonHistogrammer::print_progress] INFO : \tElapsed time: {} : {} : {:.3}".format(int(round(h, 0)), int(round(m, 0)), s)
					print "[MonoPhotonHistogrammer::print_progress] INFO : \tEstimated finish time: {}".format(datetime.datetime.fromtimestamp(estimated_completion).strftime('%Y-%m-%d %H:%M:%S'))
				else:
					print "[MonoPhotonHistogrammer::print_progress] INFO : \tFor time estimates, call self.start_timer() right before starting the event loop"




if __name__ == "__main__":
	# Command line arguments
	import argparse
	parser = argparse.ArgumentParser(description='Make histograms for monophoton analysis')
	input_group = parser.add_mutually_exclusive_group()
	input_group.add_argument('--samples', type=str, help='Run over a list of samples (comma-separated)')
	input_group.add_argument('--all', action='store_true', help='Run over all samples')
	parser.add_argument('--max_events', type=int, default=-1, help='Limit number of events processed')
	args = parser.parse_args()

	# Create list of input samples
	if args.samples:
		samples = args.samples.split(",")
	elif args.all:
		samples = input_samples.samples
	subsamples = []
	for sample in samples:
		subsamples.extend(input_samples.subsamples[sample])

	for subsample in subsamples:
		histogrammer = MonoPhotonHistogrammer(is_data=("data" in subsample.lower()))
		for input_file in input_samples.subsample_files[subsample]:
			histogrammer.add_file(input_file)
		histogrammer.set_output_path("./histograms_{}.root".format(subsample))

		histogrammer.start()
		histogrammer.run(max_events=args.max_events)
		histogrammer.finish()
