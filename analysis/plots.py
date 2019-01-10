import os
import sys
import math
import array
import ROOT

# ROOT plotting settings
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

# Load color palettes (Color Brewer palettes, taken from seaborn python library)
from MonoPhoton.DASAnalysis.seaborn_colors import SeabornColors
colors = SeabornColors()
colors.load_palette("Blues_d")
colors.load_palette("Reds_d")
colors.load_palette("Oranges_d")
colors.load_palette("Greens_d")
colors.load_palette("Purples_d")

# One stop shop for style
style = {
	"data":{
		"marker_style":20,
		"marker_size":1,
		"marker_color":ROOT.kBlack,
	},
	"WGJets":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Purples_d", 1)
	},
	"ZLLGJets":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Oranges_d", 4)
	},
	"ZNuNuGJets":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Oranges_d", 0)
	},
	"WToENu":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Blues_d", 2)
	},
	"WToMuNu":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Reds_d", 4)
	},
	"WToTauNu":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Purples_d", 4)
	},
	"GJets":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Blues_d", 4)
	},
	"JetFakes":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Greens_d", 3)
	},
	"ElectronFakes":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Blues_d", 3)
	},
	"Small":{
		"line_width":0,
		"line_color":1,
		"line_style":1,
		"fill_style":1001,
		"fill_color":colors.get_root_color("Reds_d", 5)
	},
}

legend_entries = {
	"data":"Data 2015",
	"WGJets":"W+#gamma",
	"ZLLGJets":"Z(ll)+#gamma",
	"ZNuNuGJets":"Z(#nu#nu)+#gamma",
	"WToENu":"W#rightarrowe#nu",
	"WToMuNu":"W#rightarrow#mu#nu",
	"WToTauNu":"W#rightarrow#tau#nu",
	"GJets":"#gamma+jets",
	"JetFakes":"Jet#rightarrow#gamma misID",
	"ElectronFakes":"e#rightarrow#gamma misID",
	"Small":"#gamma+jet, W(#mu#nu), W(#tau#nu), Z(ll)#gamma"
}

os.system("mkdir -pv $CMSSW_BASE/../data/plots")

# Define plots to make
vars = ["photon_pt", "pfmet"]
x_ranges = {"photon_pt":[150., 1000.], "pfmet":[150., 1000.]}
x_titles = {"photon_pt":"Photon p_{T} [GeV]", "pfmet":"#cancel{E}_{T} [GeV]"}

# Rebinning
rebin_variable = {
	"photon_pt":array.array("d", [0., 75.0, 100.0, 125.0, 145., 155., 165., 175., 190.,250., 400., 700.0,1000.0]),
	"pfmet":array.array("d", [0., 130., 150., 170., 190., 250., 400., 700.0, 1000.0]),
}

# Get histograms
for var in vars:
	hists = {}
	for process in ["data", "ZNuNuGJets", "WGJets", "ElectronFakes", "JetFakes", "GJets", "WToMuNu", "WToTauNu", "ZLLGJets"]:
		if process in ["data", "ElectronFakes", "JetFakes"]:
			histogram_file = ROOT.TFile(os.path.expandvars("$CMSSW_BASE/../data/histograms/histograms_data.root"))
		else:
			histogram_file = ROOT.TFile(os.path.expandvars("$CMSSW_BASE/../data/histograms/histograms_{}.root".format(process)))

		if process == "ElectronFakes":
			hists[process] = histogram_file.Get("cr_electronfakes_{}".format(var))
		elif process == "JetFakes":
			hists[process] = histogram_file.Get("cr_jetfakes_{}".format(var))
		else:
			hists[process] = histogram_file.Get("sr_{}".format(var))
		if not hists[process]:
			print "ERROR : Couldn't find histogram {} in file {}".format("sr_{}".format(var), histogram_file.GetPath())
			sys.exit(1)
		hists[process].SetDirectory(0)
		histogram_file.Close()
		print "Process {} norm = {}".format(process, hists[process].Integral())

		# Some processing
		if var in rebin_variable:
			hists[process] = hists[process].Rebin(len(rebin_variable[var])-1, hists[process].GetName() + "_rebinned", rebin_variable[var])
			hists[process].SetDirectory(0)
			for xbin in xrange(1, hists[process].GetNbinsX()+1):
				bin_content = hists[process].GetBinContent(xbin)
				bin_error = hists[process].GetBinError(xbin)
				bin_width = hists[process].GetXaxis().GetBinWidth(xbin)
				hists[process].SetBinContent(xbin, bin_content / bin_width)
				hists[process].SetBinError(xbin, bin_error / bin_width)

		if "marker_style" in style[process]:
			hists[process].SetMarkerStyle(style[process]["marker_style"])
		if "marker_size" in style[process]:
			hists[process].SetMarkerSize(style[process]["marker_size"])
		if "marker_color" in style[process]:
			hists[process].SetMarkerColor(style[process]["marker_color"])
		if "line_style" in style[process]:
			hists[process].SetLineStyle(style[process]["line_style"])
		if "line_width" in style[process]:
			hists[process].SetLineWidth(style[process]["line_width"])
		if "line_color" in style[process]:
			hists[process].SetLineColor(style[process]["line_color"])
		if "fill_style" in style[process]:
			hists[process].SetFillStyle(style[process]["fill_style"])
		if "fill_color" in style[process]:
			hists[process].SetFillColor(style[process]["fill_color"])


	canvas = ROOT.TCanvas("c_sr_{}".format(var), "c_sr_{}".format(var), 1000, 1000)
	top = ROOT.TPad("top_{}".format(var), "top_{}".format(var), 0., 0.4, 1., 1.)
	top.SetBottomMargin(0.02)
	top.SetLogy()
	top.Draw()
	top.cd()

	# Draw axis
	#frame_top = ROOT.TH1F("frame_top_{}".format(var), "frame_top", 100, x_ranges[var][0], x_ranges[var][1])
	#frame_top.SetMinimum(1.e-4)
	#frame_top.SetMaximum(hists["data"].GetMaximum() * 10.)
	##frame_top.GetXaxis().SetTitle(x_titles[var])
	#frame_top.GetXaxis().SetLabelSize(0)
	#frame_top.GetXaxis().SetTitleSize(0)
	#frame_top.GetYaxis().SetTitle("Events / GeV")
	#frame_top.Draw("axis")

	# Make background histogram stack
	backgrounds = ["ZNuNuGJets", "WGJets", "ElectronFakes", "JetFakes", "GJets", "WToMuNu", "WToTauNu", "ZLLGJets"]
	# Sort backgrounds by integral
	backgrounds.sort(key=lambda x: hists[x].Integral())
	background_stack = ROOT.THStack("backgrounds_{}".format(var), "backgrounds")
	total_bkgd_hist = hists["data"].Clone() # Also make a total background histogram, for drawing a thick line on top of the stack
	total_bkgd_hist.Reset()
	total_bkgd_hist.SetLineWidth(2)
	for background in backgrounds:
		background_stack.Add(hists[background])
		total_bkgd_hist.Add(hists[background])
	# Do a dummy Draw() for the THStack... needed before styling, because the draw stuff doesn't exist otherwise >:[ 
	background_stack.Draw("hist")
	background_stack.SetMinimum(1.e-4)
	background_stack.SetMaximum(hists["data"].GetMaximum() * 50.)
	background_stack.GetXaxis().SetTitleSize(0)
	background_stack.GetXaxis().SetLabelSize(0)
	background_stack.GetYaxis().SetTitleSize(0.06)
	background_stack.GetYaxis().SetTitleOffset(0.8)
	background_stack.GetYaxis().SetLabelSize(0.06)
	if var in rebin_variable:
		background_stack.GetYaxis().SetTitle("Events / GeV")
	else:
		background_stack.GetYaxis().SetTitle("Events")
	background_stack.GetXaxis().SetRangeUser(x_ranges[var][0], x_ranges[var][1])

	background_stack.Draw("hist")
	total_bkgd_hist.Draw("hist same")
	hists["data"].Draw("p same")
	background_stack.Draw("axis same") # Redraw frame so it's always on top of histograms

	# Make legend
	legend = ROOT.TLegend(0.6, 0.55, 0.88, 0.9)
	legend.SetNColumns(2)
	legend.SetFillColor(0)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	legend.AddEntry(hists["data"], legend_entries["data"], "p")
	legend.AddEntry(total_bkgd_hist, "Total bkgd", "l")
	for background in reversed(backgrounds):
		legend.AddEntry(hists[background], legend_entries[background], "lf")
	legend.Draw()

	# Pull plot (number of standard deviation of data from prediction)
	canvas.cd()
	bottom = ROOT.TPad("bottom_{}".format(var), "bottom_{}".format(var), 0., 0., 1., 0.4)
	bottom.SetTopMargin(0.03)
	bottom.SetBottomMargin(0.25)
	bottom.Draw()
	bottom.cd()
	pull_hist = hists["data"].Clone()
	pull_hist.Reset()
	for xbin in xrange(1, pull_hist.GetXaxis().GetNbins()+1):
		if var in ["photon_pt", "pfmet"]:
			data = hists["data"].GetBinContent(xbin) * hists["data"].GetXaxis().GetBinWidth(xbin)
			bkgd = total_bkgd_hist.GetBinContent(xbin) * hists["data"].GetXaxis().GetBinWidth(xbin)
		else:
			data = hists["data"].GetBinContent(xbin)
			bkgd = total_bkgd_hist.GetBinContent(xbin)

		if bkgd > 0:
			pull = (data - bkgd) / math.sqrt(bkgd)
		else:
			pull = 0.
		pull_hist.SetBinContent(xbin, pull)
	pull_hist.SetMinimum(-3.)
	pull_hist.SetMaximum(3.)
	pull_hist.GetXaxis().SetTitleSize(0.08)
	pull_hist.GetXaxis().SetLabelSize(0.08)
	pull_hist.GetXaxis().SetTitleOffset(1.1)
	pull_hist.GetYaxis().SetTitleSize(0.08)
	pull_hist.GetYaxis().SetTitleOffset(0.6)
	pull_hist.GetYaxis().SetLabelSize(0.08)
	pull_hist.GetYaxis().SetTitle("(Data - Bkgd) / #sqrt{Bkgd}")
	pull_hist.GetXaxis().SetRangeUser(x_ranges[var][0], x_ranges[var][1])
	pull_hist.Draw("p")

	zero = ROOT.TLine(pull_hist.GetXaxis().GetXmin(), 0., pull_hist.GetXaxis().GetXmax(), 0.)
	zero.SetLineStyle(2)
	zero.SetLineColor(ROOT.kGray)
	zero.Draw()

	canvas.cd()
	canvas.SaveAs(os.path.expandvars("$CMSSW_BASE/../data/plots/{}.pdf".format(canvas.GetName())))

	# Junk necessary to prevent pyROOT from segfaulting
	ROOT.SetOwnership(top, False)
	ROOT.SetOwnership(bottom, False)
	ROOT.SetOwnership(canvas, False)
