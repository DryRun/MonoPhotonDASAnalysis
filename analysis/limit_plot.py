import os
import sys
import array
import ROOT

# ROOT style stuff
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetPadTickX(1)
ROOT.gStyle.SetPadTickY(1)

# Fill in the results from combine here
masses = [1000, 2000, 3000]
limits = {
	1000:{
		"obs":1.,
		"exp_m2":0.2,
		"exp_m1":0.5,
		"exp":1.,
		"exp_p1":2.,
		"exp_p2":5.,
	},
	2000:{
		"obs":1.e-1,
		"exp_m2":0.2e-1,
		"exp_m1":0.5e-1,
		"exp":1.e-1,
		"exp_p1":2.e-1,
		"exp_p2":5.e-1,
	},
	3000:{
		"obs":1.e-2,
		"exp_m2":0.2e-2,
		"exp_m1":0.5e-2,
		"exp":1.e-2,
		"exp_p1":2.e-2,
		"exp_p2":5.e-2,
	}
}

add_xs = {
	1000.:0.4084,
	2000.:0.0515,
	3000.:0.01089,
}

x = array.array("d", [])
obs = array.array("d", [])
exp_m2 = array.array("d", [])
exp_m1 = array.array("d", [])
exp = array.array("d", [])
exp_p1 = array.array("d", [])
exp_p2 = array.array("d", [])
theory = array.array("d", [])

for i in xrange(3):
	x.append(masses[i])
	obs.append(add_xs[x[i]] * limits[x[i]]["obs"])
	exp_m2.append(add_xs[x[i]] * limits[x[i]]["exp_m2"])
	exp_m1.append(add_xs[x[i]] * limits[x[i]]["exp_m1"])
	exp.append(add_xs[x[i]] * limits[x[i]]["exp"])
	exp_p1.append(add_xs[x[i]] * limits[x[i]]["exp_p1"])
	exp_p2.append(add_xs[x[i]] * limits[x[i]]["exp_p2"])
	theory.append(add_xs[x[i]])

# Make graphs
tg_theory = ROOT.TGraph(3, x, theory)
tg_obs = ROOT.TGraph(3, x, obs)
tg_exp = ROOT.TGraph(3, x, exp)

# Green (+/-1 sigma) and yellow (+/-2 sigma) graphs are polygons defined by the edge of the band
x_expbands = array.array("d", [])
exp_pm1 = array.array("d", [])
for i in xrange(3):
	x_expbands.append(masses[i])
	exp_pm1.append(exp_m1[i])
for i in xrange(3):
	x_expbands.append(masses[2-i])
	exp_pm1.append(exp_p1[2-i])
tg_exp_pm1 = ROOT.TGraph(6, x_expbands, exp_pm1)

exp_pm2 = array.array("d", [])
for i in xrange(3):
	exp_pm2.append(exp_m2[i])
for i in xrange(3):
	exp_pm2.append(exp_p2[2-i])
tg_exp_pm2 = ROOT.TGraph(6, x_expbands, exp_pm2)

# Draw canvas
canvas = ROOT.TCanvas("limits", "limits", 800, 600)
canvas.SetLogy()
frame = ROOT.TH1F("frame", "frame", 100, 500., 3500.)
frame.GetXaxis().SetTitle("MD [GeV]")
frame.GetYaxis().SetTitle("95% CL upper limit on #sigma [pb]")
frame.SetMinimum(1.e-3)
frame.SetMaximum(1.)
frame.Draw()

tg_exp_pm2.SetFillColor(ROOT.kOrange)
tg_exp_pm2.SetFillStyle(1001)
tg_exp_pm2.SetLineWidth(0)
tg_exp_pm2.SetMarkerSize(0)
tg_exp_pm2.Draw("f")

tg_exp_pm1.SetFillColor(ROOT.kGreen+1)
tg_exp_pm1.SetFillStyle(1001)
tg_exp_pm1.SetLineWidth(0)
tg_exp_pm1.SetMarkerSize(0)
tg_exp_pm1.Draw("f")

tg_exp.SetLineWidth(1)
tg_exp.SetLineStyle(2)
tg_exp.Draw("l")

tg_obs.SetLineWidth(1)
tg_obs.SetLineStyle(1)
tg_obs.Draw("l")

tg_theory.SetLineWidth(1)
tg_theory.SetLineStyle(9)
tg_theory.SetLineColor(ROOT.kBlue+2)
tg_theory.Draw("l")

legend = ROOT.TLegend(0.54, 0.7, 0.85, 0.85)
legend.SetBorderSize(0)
legend.SetFillColor(0)
legend.SetFillStyle(0)
legend.AddEntry(tg_theory,"Theoretical prediction","l")
legend.AddEntry(tg_obs,"Observed limit","l")

# Make dummy TGraphs for exp+/-1 and +/-2 sigma, so they have both a fill and a dotted line
tg_exp_pm1_dummy = ROOT.TGraph(3)
tg_exp_pm1_dummy.SetLineWidth(1)
tg_exp_pm1_dummy.SetLineStyle(2)
tg_exp_pm1_dummy.SetFillColor(ROOT.kGreen+1)
tg_exp_pm1_dummy.SetFillStyle(1001)
legend.AddEntry(tg_exp_pm1_dummy,"Expected limit #pm 1#sigma","lf");

tg_exp_pm2_dummy = ROOT.TGraph(3)
tg_exp_pm2_dummy.SetLineWidth(1)
tg_exp_pm2_dummy.SetLineStyle(2)
tg_exp_pm2_dummy.SetFillColor(ROOT.kOrange)
tg_exp_pm2_dummy.SetFillStyle(1001)
legend.AddEntry(tg_exp_pm2_dummy,"Expected limit #pm 2#sigma","lf");

legend.Draw()

# Redraw frame so ticks are on top
frame.Draw("axis same")

canvas.SaveAs("$CMSSW_BASE/../data/plots/limit_plot.pdf")
