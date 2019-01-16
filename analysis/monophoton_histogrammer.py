import os
import sys
import array
import math
import time
import datetime

from ROOT import * # This is slightly bad practice, but saves having to type "ROOT." in front of every ROOT object

# Load C++ libraries (for the ntuple reader class)
gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMonoPhotonDASAnalysis.so"))

# Configure ROOT defaults
gROOT.SetBatch(kTRUE) # Don't open any X windows
gStyle.SetOptStat(0) # Don't draw stat boxes for histograms
gStyle.SetOptTitle(0) # Don't draw histogram title on plots

# import photon trigger enum
from MonoPhoton.DASAnalysis.photon_triggers import PhotonTriggers

class MonoPhotonHistogrammer:
    def __init__(self, tree_name="ggNtuplizer/EventTree", is_data=True):
        self._data = TChain(tree_name)
        self._is_data = is_data # True if running over real data, false if running over MC
        if self._is_data:
            print "[MonoPhotonHistogrammer::__init__] INFO : Running over DATA."
        else:
            print "[MonoPhotonHistogrammer::__init__] INFO : Running over MC."            

    ######################
    ### Main functions ###
    ######################

    # start(): performs the initial setup, such as creating histograms
    def start(self):
        print "[MonoPhotonHistogrammer::start] INFO : In start()."

        self._selections = [] # [selection_name]
        self._histograms = {} # {selection_name : {histogram_name : histogram}}

        # Make a list of the selections. We'll run multiple selections at once: one for the actual signal region, plus other selections for things like trigger efficiency estimation or control regions for validating background estimations.
        self._selections.append("trigger_numerator")
        self._selections.append("trigger_denominator")
        self._selections.append("sr")
        self._selections.append("cr_electronfakes")
        self._selections.append("cr_jetfakes")

        # Create histograms
        # Old code: it used to make coarse, variable-width histograms. Now, make fine-binned histograms here, and rebin later if needed
        #pt_bins = array.array("d", [0., 75.0, 100.0, 125.0, 145., 155., 165., 175., 190.,250., 400., 700.0,1000.0])
        #met_bins = array.array("d", [0., 130., 150., 170., 190., 250., 400., 700.0, 1000.0])
        for selection in self._selections:
            self._histograms[selection] = {}

            self._histograms[selection]["events_passed"] = TH1D("{}_events_passed".format(selection), "{}_events_passed".format(selection), 1, 0.5, 1.5)

            self._histograms[selection]["events_passed_weighted"] = TH1D("{}_events_passed_weighted".format(selection), "{}_events_passed_weighted".format(selection), 1, 0.5, 1.5)

            self._histograms[selection]["photon_pt"] = TH1D("{}_photon_pt".format(selection), "{}_photon_pt".format(selection), 200, 0., 1000.)
            self._histograms[selection]["photon_pt"].GetXaxis().SetTitle("#gamma p_{T} [GeV]")

            self._histograms[selection]["photon_eta"] = TH1D("{}_photon_eta".format(selection), "{}_photon_eta".format(selection), 60, -1.5, 1.5)
            self._histograms[selection]["photon_eta"].GetXaxis().SetTitle("#gamma #eta")

            self._histograms[selection]["photon_SCeta"] = TH1D("{}_photon_SCeta".format(selection), "{}_photon_SCeta".format(selection), 60, -1.5, 1.5)
            self._histograms[selection]["photon_SCeta"].GetXaxis().SetTitle("#gamma #eta_{SC}")

            self._histograms[selection]["photon_phi"] = TH1D("{}_photon_phi".format(selection), "{}_photon_phi".format(selection), 100, -1.1*math.pi, 1.1*math.pi)
            self._histograms[selection]["photon_phi"].GetXaxis().SetTitle("#gamma #phi")

            self._histograms[selection]["photon_SCphi"] = TH1D("{}_photon_SCphi".format(selection), "{}_photon_SCphi".format(selection), 120, -1.1 * math.pi, 1.1 * math.pi)
            self._histograms[selection]["photon_SCphi"].GetXaxis().SetTitle("#gamma #phi_{SC}")

            self._histograms[selection]["pfmet"] = TH1D("{}_pfmet".format(selection), "{}_photon_pfmet".format(selection), 100, 0., 1000.)
            self._histograms[selection]["pfmet"].GetXaxis().SetTitle("PF MET [GeV]")

            self._histograms[selection]["dphi_photon_met"] = TH1D("{}_dphi_photon_met".format(selection), "{}_dphi_photon_met".format(selection), 100, 0., math.pi)
            self._histograms[selection]["dphi_photon_met"].GetXaxis().SetTitle("#Delta#phi(#gamma, PF MET)")

            self._histograms[selection]["njets"] = TH1D("{}_njets".format(selection), "{}_njets".format(selection), 21, -0.5, 20.5)
            self._histograms[selection]["njets"].GetXaxis().SetTitle("n_{jets}")

            self._histograms[selection]["leading_jet_pt"] = TH1D("{}_leading_jet_pt".format(selection), "{}_leading_jet_pt".format(selection), 50, 0., 1000.)
            self._histograms[selection]["leading_jet_pt"].GetXaxis().SetTitle("Leading jet p_{T} [GeV]")

            self._histograms[selection]["leading_jet_eta"] = TH1D("{}_leading_jet_eta".format(selection), "{}_leading_jet_eta".format(selection), 50, -5., 5.)
            self._histograms[selection]["leading_jet_eta"].GetXaxis().SetTitle("Leading jet #eta")

        self._events_processed = 0
        print "[MonoPhotonHistogrammer::start] INFO : Done with start()."

    # run(): implements the event loop
    def run(self, max_events=-1, first_event=0, nprint=-1):
        print "[MonoPhotonHistogrammer::run] INFO : In run()."

        total_entries = self._data.GetEntries()
        if max_events > 0:
            limit_nevents = min(max_events, total_entries)
        else:
            limit_nevents = total_entries

        # Setup the progress timer
        # Print progress every 5%
        n_checkpoints = 20
        print_every = int(math.ceil(1. * limit_nevents / n_checkpoints))

        self.start_timer()
        for i in xrange(limit_nevents):
            self.print_progress(i, first_event, limit_nevents, print_every)
            self._data.GetEntry(i)
            self._events_processed += 1

            ########################
            ### Event selections ###
            ########################

            # Signal region selection
            pass_SR, i_ph_sr = self.pass_selection_SR()
            if pass_SR:
                self.fill_histograms("sr", i_ph_sr, event_weight=1.)

            # Electron fake selection: different photon selection with pixel seed required
            #pass_CR_electronfakes, i_ph_electronfakes = self.pass_selection_CR_electronfakes()
            #if pass_CR_electronfakes:
             #   r_electronfakes = 0.0184
             #   self.fill_histograms("cr_electronfakes", i_ph_electronfakes, event_weight=r_electronfakes)

            # Jet fake selection: different photon selection with very loose && !loose isolation
            #pass_CR_jetfakes, i_ph_jetfakes = self.pass_selection_CR_jetfakes()
            #if pass_CR_jetfakes:
            #   r_qcd = 0.079 + 0.00014 * self._data.phoEt[i_ph_jetfakes]
            #    self.fill_histograms("cr_jetfakes", i_ph_jetfakes, event_weight=r_qcd)

            # Trigger selections, for computing trigger efficiency
            if self.pass_backup_triggers() and self._data.pfMET > 140. and i_ph_sr >= 0:
                self.fill_histograms("trigger_denominator", i_ph_sr, event_weight=1.)

            if self.pass_backup_triggers() and self._data.pfMET > 140. and i_ph_sr >= 0 and self.pass_signal_triggers():
                self.fill_histograms("trigger_numerator", i_ph_sr, event_weight=1.)

        # Print performance
        elapsed_time = time.time() - self._ts_start
        print "[MonoPhotonHistogrammer::run] INFO : Done processing events. Processed {} events in {:.2f}s = {:.2f} Hz".format(self._events_processed, elapsed_time, self._events_processed / elapsed_time)

        print "[MonoPhotonHistogrammer::run] INFO : Done with run()."


    # finish(): saves the histograms to the output file.
    def finish(self):
        print "[MonoPhotonHistogrammer::finish] INFO : In finish()."
        if not self._output_path:
            self._output_path = "output_{}.root".format(time.time())
            print "[MonoPhotonHistogrammer::finish] WARNING : No output path specified! Saving to {}".format(self._output_path)
        output_file = TFile(self._output_path, "RECREATE")
        for selection in self._selections:
            for histogram in sorted(self._histograms[selection].values(), key=lambda x: x.GetName()):
                histogram.Write()

        # Also write a histogram containing the number of events processed
        h_nevents_processed = TH1D("events_processed", "events_processed", 1, 0.5, 1.5)
        h_nevents_processed.SetBinContent(1, self._events_processed)
        h_nevents_processed.Write()

        output_file.Close()

        print "[MonoPhotonHistogrammer::finish] INFO : Done with finish()."

    def fill_histograms(self, selection, photon_index, event_weight=1.):
        self._histograms[selection]["events_passed"].Fill(1)
        self._histograms[selection]["events_passed_weighted"].Fill(1, event_weight)
        self._histograms[selection]["photon_pt"].Fill(self._data.phoEt[photon_index], event_weight)
        self._histograms[selection]["photon_eta"].Fill(self._data.phoEta[photon_index], event_weight)
        self._histograms[selection]["photon_SCeta"].Fill(self._data.phoSCEta[photon_index], event_weight)
        self._histograms[selection]["photon_phi"].Fill(self._data.phoPhi[photon_index], event_weight)
        self._histograms[selection]["photon_SCphi"].Fill(self._data.phoSCPhi[photon_index], event_weight)
        self._histograms[selection]["pfmet"].Fill(self._data.pfMET, event_weight)
        self._histograms[selection]["dphi_photon_met"].Fill(math.acos(math.cos(self._data.phoPhi[photon_index] - self._data.pfMETPhi)), event_weight) # acos(cos(delta_phi)) is a trick to map delta_phi onto the interval [0, pi]. Think 2*pi==0 for opening angles.
        self._histograms[selection]["njets"].Fill(self._data.nJet, event_weight)
        self._histograms[selection]["leading_jet_pt"].Fill(self._data.jetPt[0], event_weight)
        self._histograms[selection]["leading_jet_eta"].Fill(self._data.jetEta[0], event_weight)


    #########################
    ### Selection helpers ###
    #########################
    def pass_signal_triggers(self):
        return (
            self.photonTriggerResult(PhotonTriggers.kHLT_Photon175) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon250_NoHE) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon300_NoHE) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon500) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon600) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon165_HE10)
            or self.photonTriggerResult(PhotonTriggers.kHLT_DoublePhoton60)
        )

    def pass_backup_triggers(self):
        return (
            self.photonTriggerResult(PhotonTriggers.kHLT_Photon75)
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon90) 
            or self.photonTriggerResult(PhotonTriggers.kHLT_Photon120)
        )

    # Signal region selection
    # - Returns (pass/fail, selected photon index)
    def pass_selection_SR(self):
        # Choose the photon of interest for the signal region.
        # The photons in the ntuple are ordered by pT, so the following logic selects the highest-pT photon satisfying the |eta| and ID requirements.
        i_ph_sr = -1
        for i in xrange(self._data.nPho):
            if abs(self._data.phoSCEta[i]) < 1.4442 and self.photon_id(i):
                i_ph_sr = i
                break
        if i_ph_sr == -1:
            return False, -1

        # Number of loose electrons, for electron veto
        n_electrons = 0
        for i in xrange(self._data.nEle):
            dR_el_ph = math.sqrt((self._data.eleEta[i] - self._data.phoEta[i_ph_sr])**2 + (math.acos(math.cos(self._data.elePhi[i] - self._data.phoPhi[i_ph_sr])))**2)
            if self.electron_id_loose(i) and self._data.elePt[i] > 10. and dR_el_ph > 0.5:
                n_electrons += 1

        # Number of loose muons, for muon veto
        n_muons = 0
        for i in xrange(self._data.nMu):
            dR_mu_ph = math.sqrt((self._data.muEta[i] - self._data.phoEta[i_ph_sr])**2 + (math.acos(math.cos(self._data.muPhi[i] - self._data.phoPhi[i_ph_sr])))**2)
            if self.muon_id_loose(i) and self._data.muPt[i] > 10. and dR_mu_ph > 0.5:
                n_muons += 1

        # Require MET away from leading 4 jets
        pass_dphi_jet_MET = True
        for i in xrange(min(4, self._data.nJet)):
            if (math.acos(math.cos(self._data.jetPhi[i] - self._data.pfMETPhi)) < 0.5) \
                and (self._data.jetPt[i] > 30.):
                    pass_dphi_jet_MET = False
                    break

        return (
            self.pass_signal_triggers()
            and (self._data.metFilters == 0)
            and (self._data.phoEt[i_ph_sr] > 175.)
            and (self._data.pfMET > 170.)
            and math.acos(math.cos(self._data.phoPhi[i_ph_sr] - self._data.pfMETPhi)) > 2.
            and n_electrons == 0
            and n_muons == 0
            and pass_dphi_jet_MET
        ), i_ph_sr

    def pass_selection_CR_electronfakes(self):
        # Construct this CR from code similar to pass_selection_SR(). 
        # For the photon selection, use self.photon_id_electrondenominator() instead of photon_id(). 

        return False, -1

    def pass_selection_CR_jetfakes(self):
        # Construct this CR from code similar to pass_selection_SR(). 
        # For the photon selection, use self.photon_id_qcddenominator() instead of photon_id(). 

        return False, -1

    # Photon ID
    # Corresponds to "SPRING15 selection 25ns" / barrel / medium WP
    # https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedPhotonIdentificationRun2Archive
    def photon_id(self, i):
        return (self._data.phoHoverE[i] < 0.05) \
            and (self._data.phoSigmaIEtaIEtaFull5x5[i] < 0.0102) \
            and (self._data.phohasPixelSeed[i] == 0) \
            and self.photon_medium_isolation(i)

    # Photon ID for electron fake denominator (same as nominal, except phohasPixelSeed == 1)
    def photon_id_electrondenominator(self, i):
        return (self._data.phoHoverE[i] < 0.05) \
            and (self._data.phoSigmaIEtaIEtaFull5x5[i] < 0.0102) \
            and (self._data.phohasPixelSeed[i] == 1) \
            and self.photon_medium_isolation(i)

    # Photon ID for the QCD denominator (fail loose iso, pass very loose iso)
    def photon_id_qcddenominator(self, i):
        return (self._data.phoHoverE[i] < 0.05) \
            and (self._data.phoSigmaIEtaIEtaFull5x5[i] < 0.0102) \
            and (self._data.phohasPixelSeed[i] == 0) \
            and not self.photon_loose_isolation(i) \
            and self.photon_veryloose_isolation(i)

    def photon_medium_isolation(self, i):
        return (max(0., self._data.phoPFChIso[i]  - self._data.rho * self.EAcharged(self._data.phoSCEta[i])) < 1.37) \
            and (max(0., self._data.phoPFNeuIso[i] - self._data.rho * self.EAneutral(self._data.phoSCEta[i])) < (1.06 + (0.014 * self._data.phoEt[i]) + (0.000019 * self._data.phoEt[i]**2))) \
            and (max(0., self._data.phoPFPhoIso[i] - self._data.rho * self.EAphoton(self._data.phoSCEta[i])) < (0.28 + (0.0053 * self._data.phoEt[i])))

    def photon_loose_isolation(self, i):
        return (max(0., self._data.phoPFChIso[i]  - self._data.rho * self.EAcharged(self._data.phoSCEta[i])) < 3.32) \
            and (max(0., self._data.phoPFNeuIso[i] - self._data.rho * self.EAneutral(self._data.phoSCEta[i])) < (1.92 + (0.014 * self._data.phoEt[i]) + (0.000019 * self._data.phoEt[i]**2))) \
            and (max(0., self._data.phoPFPhoIso[i] - self._data.rho * self.EAphoton(self._data.phoSCEta[i])) < (0.81 + (0.0053 * self._data.phoEt[i])))

    def photon_veryloose_isolation(self, i):
        photon_Et = self._data.phoEt[i]
        photon_eta = self._data.phoSCEta[i]
        maxPFCharged= min(0.20 * photon_Et, 5.0*(3.32))
        maxPFNeutral= min(0.20 * photon_Et, 5.0*(1.92 + (0.014 * photon_Et) + (0.000019 * photon_Et**2)))
        maxPFPhoton = min(0.20 * photon_Et, 5.0*(0.81 + (0.0053 * photon_Et)))

        return (max(0., self._data.phoPFChIso[i]  - self._data.rho * self.EAcharged(self._data.phoSCEta[i])) < maxPFCharged) \
            and (max(0., self._data.phoPFNeuIso[i] - self._data.rho * self.EAneutral(self._data.phoSCEta[i])) < maxPFNeutral) \
            and (max(0., self._data.phoPFPhoIso[i] - self._data.rho * self.EAphoton(self._data.phoSCEta[i])) < maxPFPhoton)


    # Effective area to be needed in PF Iso for photon ID
    # https:#indico.cern.ch/event/455258/contribution/0/attachments/1173322/1695132/SP15_253rd.pdf -- slide-5
    def EAcharged(self, eta):
        if (abs(eta) >= 0.0   and abs(eta) < 1.0):
            return 0.0456
        elif (abs(eta) >= 1.0   and abs(eta) < 1.479):
            return 0.0500
        elif (abs(eta) >= 1.479 and abs(eta) < 2.0):
            return 0.0340
        elif (abs(eta) >= 2.0   and abs(eta) < 2.2):
            return 0.0383
        elif (abs(eta) >= 2.2   and abs(eta) < 2.3):
            return 0.0339
        elif (abs(eta) >= 2.3   and abs(eta) < 2.4):
            return 0.0303
        else:
            return 0.0240

    def EAneutral(self, eta):
        if (abs(eta) >= 0.0   and abs(eta) < 1.0):
            return 0.0599
        elif (abs(eta) >= 1.0   and abs(eta) < 1.479):
            return 0.0819
        elif (abs(eta) >= 1.479 and abs(eta) < 2.0):
            return 0.0696
        elif (abs(eta) >= 2.0   and abs(eta) < 2.2):
            return 0.0360
        elif (abs(eta) >= 2.2   and abs(eta) < 2.3):
            return 0.0360
        elif (abs(eta) >= 2.3   and abs(eta) < 2.4):
            return 0.0462
        else:
            return 0.0656

    def EAphoton(self, eta):
        if (abs(eta) >= 0.0   and abs(eta) < 1.0):
            return 0.1271
        elif (abs(eta) >= 1.0   and abs(eta) < 1.479):
            return 0.1101
        elif (abs(eta) >= 1.479 and abs(eta) < 2.0):
            return 0.0756
        elif (abs(eta) >= 2.0   and abs(eta) < 2.2):
            return 0.1175
        elif (abs(eta) >= 2.2   and abs(eta) < 2.3):
            return 0.1498
        elif (abs(eta) >= 2.3   and abs(eta) < 2.4):
            return 0.1857
        else:
            return 0.2183
         
    # photonTriggerResult(): returns True if the event passed the specified trigger.
    # See the definition of the PhotonTrigger enum above
    def photonTriggerResult(self, trigName):
        return self._data.HLTPho >> trigName.value & 1

    # Electron loose ID, for electron veto
    def electron_id_loose(self, i):
        # Get effective area and isolation
        if (abs(self._data.eleSCEta.at(i)) <= 1.0):
            EA = 0.1752
        elif (1.0 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) <= 1.479):
            EA = 0.1862
        elif (1.479 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) <= 2.0):
            EA = 0.1411
        elif (2.0 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) <= 2.2):
            EA = 0.1534
        elif (2.2 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) <= 2.3):
            EA = 0.1903
        elif (2.3 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) <= 2.4):
            EA = 0.2243
        elif (2.4 < abs(self._data.eleSCEta.at(i)) and abs(self._data.eleSCEta.at(i)) < 2.5):
            EA = 0.2687
        else:
            # Electron SCEta > 2.5: just return false, we don't care about these
            return False
        EAcorrIso = (self._data.elePFChIso.at(i) + max(0., self._data.elePFNeuIso.at(i) + self._data.elePFPhoIso.at(i) - self._data.rho*EA)) / self._data.elePt.at(i)

        if abs(self._data.eleSCEta.at(i)) <= 1.479:
            pass_SigmaIEtaIEtaFull5x5 = self._data.eleSigmaIEtaIEtaFull5x5.at(i) < 0.0103
            pass_dEtaIn               = abs(self._data.eledEtaAtVtx.at(i)) < 0.0105
            pass_dPhiIn               = abs(self._data.eledPhiAtVtx.at(i)) < 0.115
            pass_HoverE               = self._data.eleHoverE.at(i) < 0.104
            pass_iso                  = EAcorrIso < 0.0893
            pass_ooEmooP              = self._data.eleEoverPInv.at(i) < 0.102
            pass_d0                   = abs(self._data.eleD0.at(i)) < 0.0261
            pass_dz                   = abs(self._data.eleDz.at(i)) < 0.41
            pass_missingHits          = self._data.eleMissHits.at(i) <= 2
            pass_convVeto             = self._data.eleConvVeto.at(i) == 1
        elif 1.479 < abs(self._data.eleSCEta.at(i)) < 2.5:
            pass_SigmaIEtaIEtaFull5x5 = self._data.eleSigmaIEtaIEtaFull5x5.at(i) < 0.0301
            pass_dEtaIn               = abs(self._data.eledEtaAtVtx.at(i)) < 0.00814
            pass_dPhiIn               = abs(self._data.eledPhiAtVtx.at(i)) < 0.182
            pass_HoverE               = self._data.eleHoverE.at(i) < 0.0897
            pass_iso                  = EAcorrIso < 0.121
            pass_ooEmooP              = self._data.eleEoverPInv.at(i) < 0.126
            pass_d0                   = abs(self._data.eleD0.at(i)) < 0.118
            pass_dz                   = abs(self._data.eleDz.at(i)) < 0.822
            pass_missingHits          = self._data.eleMissHits.at(i) <= 1
            pass_convVeto             = self._data.eleConvVeto.at(i) == 1

        return pass_SigmaIEtaIEtaFull5x5 and pass_dEtaIn and pass_dPhiIn and pass_HoverE and pass_iso and pass_ooEmooP and pass_d0 and pass_dz

    # Muon loose ID, for muon veto
    def muon_id_loose(self, i):
        pass_PFMuon               = self._data.muIsPFMuon.at(i)
        pass_globalMuon           = self._data.muIsGlobalMuon.at(i)
        pass_trackerMuon          = self._data.muIsTrackerMuon.at(i)
        muPhoPU                   = self._data.muPFNeuIso.at(i) + self._data.muPFPhoIso.at(i) - 0.5*self._data.muPFPUIso.at(i)
        tightIso_combinedRelative = (self._data.muPFChIso.at(i) + max(0., muPhoPU))/(self._data.muPt.at(i))
        pass_iso                  = tightIso_combinedRelative < 0.25;
        return pass_PFMuon and (pass_globalMuon or pass_trackerMuon)


    #################
    ### Utilities ###
    #################
    
    # add_file(): add an input file to run over (see the TChain documentation).
    def add_file(self, filename):
        self._data.Add(filename)

    # set_output_path(): specify the output path for saving.
    def set_output_path(self, output_path):
        self._output_path = output_path
        os.system("mkdir -pv {}".format(os.path.dirname(self._output_path)))

    # start_timer(): starts the timer for tracking the processing progress and estimating the time of completion.
    def start_timer(self):
        self._ts_start = time.time()
        print "[MonoPhotonHistogrammer::start_timer] INFO : Start time: {}".format(datetime.datetime.fromtimestamp(self._ts_start).strftime('%Y-%m-%d %H:%M:%S'))

    # print_progress: prints_the_progress. 
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
