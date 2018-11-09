#ifndef NtupleData_cxx
#define NtupleData_cxx

#include "MonoPhoton/DASAnalysis/interface/NtupleData.h"

NtupleData::NtupleData(TTree *tree) : NtupleBase(tree) {
    _isData = true;
}

void NtupleData::isData(bool isData) {
    _isData = isData;

    if (_isData) {
        // Turn off MC-only branches
        fChain->SetBranchStatus("pdf", 0);
        fChain->SetBranchStatus("pthat", 0);
        fChain->SetBranchStatus("processID", 0);
        fChain->SetBranchStatus("genWeight", 0);
        fChain->SetBranchStatus("nPUInfo", 0);
        fChain->SetBranchStatus("nPU", 0);
        fChain->SetBranchStatus("puBX", 0);
        fChain->SetBranchStatus("puTrue", 0);
        fChain->SetBranchStatus("nMC", 0);
        fChain->SetBranchStatus("mcPID", 0);
        fChain->SetBranchStatus("mcVtx", 0);
        fChain->SetBranchStatus("mcVty", 0);
        fChain->SetBranchStatus("mcVtz", 0);
        fChain->SetBranchStatus("mcPt", 0);
        fChain->SetBranchStatus("mcMass", 0);
        fChain->SetBranchStatus("mcEta", 0);
        fChain->SetBranchStatus("mcPhi", 0);
        fChain->SetBranchStatus("mcE", 0);
        fChain->SetBranchStatus("mcEt", 0);
        fChain->SetBranchStatus("mcGMomPID", 0);
        fChain->SetBranchStatus("mcMomPID", 0);
        fChain->SetBranchStatus("mcMomPt", 0);
        fChain->SetBranchStatus("mcMomMass", 0);
        fChain->SetBranchStatus("mcMomEta", 0);
        fChain->SetBranchStatus("mcMomPhi", 0);
        fChain->SetBranchStatus("mcIndex", 0);
        fChain->SetBranchStatus("mcStatusFlag", 0);
        fChain->SetBranchStatus("mcParentage", 0);
        fChain->SetBranchStatus("mcStatus", 0);
        fChain->SetBranchStatus("mcCalIsoDR03", 0);
        fChain->SetBranchStatus("mcTrkIsoDR03", 0);
        fChain->SetBranchStatus("mcCalIsoDR04", 0);
        fChain->SetBranchStatus("mcTrkIsoDR04", 0);
        fChain->SetBranchStatus("genMET", 0);
        fChain->SetBranchStatus("genMETPhi", 0);
    } else {
        // Turn off data-only branches
        fChain->SetBranchStatus("phomaxXtalenergyFull5x5", 0);
        fChain->SetBranchStatus("phoseedTimeFull5x5", 0);
        fChain->SetBranchStatus("phomaxXtalenergy", 0);
        fChain->SetBranchStatus("phoseedTime", 0);
        fChain->SetBranchStatus("phomipChi2", 0);
        fChain->SetBranchStatus("phomipTotEnergy", 0);
        fChain->SetBranchStatus("phomipSlope", 0);
        fChain->SetBranchStatus("phomipIntercept", 0);
        fChain->SetBranchStatus("phomipNhitCone", 0);
        fChain->SetBranchStatus("phomipIsHalo", 0);
    }
}


bool NtupleData::phoID(unsigned int i) {
    return ((*phoHoverE)[i] < 0.05) &&
             (phoSigmaIEtaIEtaFull5x5->at(i) < 0.0102) &&
             (phohasPixelSeed->at(i) == 0) &&
             (TMath::Max(((*phoPFChIso)[i]  - rho*EAcharged((*phoSCEta)[i])), 0.0) < 1.37)  &&
             (TMath::Max(((*phoPFNeuIso)[i] - rho*EAneutral((*phoSCEta)[i])), 0.0) < (1.06 + (0.014 * (*phoEt)[i]) + (0.000019 * pow((*phoEt)[i], 2.0))))  &&
             (TMath::Max(((*phoPFPhoIso)[i] - rho*EAphoton((*phoSCEta)[i])), 0.0) < (0.28 + (0.0053 * (*phoEt)[i]))
    );
}


// Effective area to be needed in PF Iso for photon ID
// https://indico.cern.ch/event/455258/contribution/0/attachments/1173322/1695132/SP15_253rd.pdf -- slide-5
Double_t NtupleData::EAcharged(Double_t eta){
    if (fabs(eta) >= 0.0   && fabs(eta) < 1.0) {
        return 0.0456;
    } else  if (fabs(eta) >= 1.0   && fabs(eta) < 1.479) {
        return 0.0500;
    } else  if (fabs(eta) >= 1.479 && fabs(eta) < 2.0) {
        return 0.0340;
    } else  if (fabs(eta) >= 2.0   && fabs(eta) < 2.2) {
        return 0.0383;
    } else  if (fabs(eta) >= 2.2   && fabs(eta) < 2.3) {
        return 0.0339;
    } else  if (fabs(eta) >= 2.3   && fabs(eta) < 2.4) {
        return 0.0303;
    } else {
        return 0.0240;
    }
}

Double_t NtupleData::EAneutral(Double_t eta) {
    if (fabs(eta) >= 0.0   && fabs(eta) < 1.0) {
        return 0.0599;
    } else  if (fabs(eta) >= 1.0   && fabs(eta) < 1.479) {
        return 0.0819;
    } else  if (fabs(eta) >= 1.479 && fabs(eta) < 2.0) {
        return 0.0696;
    } else  if (fabs(eta) >= 2.0   && fabs(eta) < 2.2) {
        return 0.0360;
    } else  if (fabs(eta) >= 2.2   && fabs(eta) < 2.3) {
        return 0.0360;
    } else  if (fabs(eta) >= 2.3   && fabs(eta) < 2.4) {
        return 0.0462;
    } else {
        return 0.0656;
    }
}

Double_t NtupleData::EAphoton(Double_t eta) {
    if (fabs(eta) >= 0.0   && fabs(eta) < 1.0) {
        return 0.1271;
    } else  if (fabs(eta) >= 1.0   && fabs(eta) < 1.479) {
        return 0.1101;
    } else  if (fabs(eta) >= 1.479 && fabs(eta) < 2.0) {
        return 0.0756;
    } else  if (fabs(eta) >= 2.0   && fabs(eta) < 2.2) {
        return 0.1175;
    } else  if (fabs(eta) >= 2.2   && fabs(eta) < 2.3) {
        return 0.1498;
    } else  if (fabs(eta) >= 2.3   && fabs(eta) < 2.4) {
        return 0.1857;
    } else {
        return 0.2183;
    } 
}



#endif