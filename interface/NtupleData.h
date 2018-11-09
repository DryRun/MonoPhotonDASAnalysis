//////////////////////////////////////////////////////////
// This class has been automatically generated on
// Fri Sep 18 19:27:19 2015 by ROOT version 6.02/05
// from TTree EventTree/Event data
// found on file: /eos/uscms/store/user/bhawna/SinglePhoton_Run2015C_25ns.root
//////////////////////////////////////////////////////////

#ifndef NtupleData_h
#define NtupleData_h

#include "MonoPhoton/DASAnalysis/interface/NtupleBase.h"


/**
 * Class NtupleData
 * - Container for exposing ntuple data in python
 * - Inherits from NtupleBase, which is created using TTree::MakeClass()
 * - Augments the automatically generated class with commonly used functions, like photon ID and trigger names
 */
class NtupleData : public NtupleBase {
public:
   NtupleData(TTree *tree=0);
   void isData(bool isData);

   bool phoID(unsigned int i);
   Double_t EAcharged(Double_t eta);
   Double_t EAneutral(Double_t eta);
   Double_t EAphoton(Double_t eta);


   // Trigger bits, from https://github.com/cmkuo/ggAnalysis/blob/baf23ca964e87eb2a927183f6393fa10cfd861fc/ggNtuplizer/plugins/ggNtuplizer_globalEvent.cc
   enum HLTPhotonBit_t {
      kHLT_Photon22                                                                       =  0, //bit0(lowest)
      kHLT_Photon30                                                                       =  1, 
      kHLT_Photon36                                                                       =  2, 
      kHLT_Photon50                                                                       =  3, 
      kHLT_Photon75                                                                       =  4, 
      kHLT_Photon90                                                                       =  5, 
      kHLT_Photon120                                                                      =  6, 
      kHLT_Photon175                                                                      =  7, 
      kHLT_Photon250_NoHE                                                                 =  8, 
      kHLT_Photon300_NoHE                                                                 =  9, 
      kHLT_Photon500                                                                      = 10, 
      kHLT_Photon600                                                                      = 11, 
      kHLT_Photon165_HE10                                                                 = 12, 
      kHLT_Photon42_R9Id85_OR_CaloId24b40e_Iso50T80L_Photon25_AND_HE10_R9Id65_Eta2_Mass15 = 13,
      kHLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_Mass90                             = 14,
      kHLT_Diphoton30_18_R9Id_OR_IsoCaloId_AND_HE_R9Id_DoublePixelSeedMatch_Mass70        = 15,
      kHLT_Diphoton30PV_18PV_R9Id_AND_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55        = 16,
      kHLT_Diphoton30EB_18EB_R9Id_OR_IsoCaloId_AND_HE_R9Id_DoublePixelVeto_Mass55         = 17,
      kHLT_Photon135_PFMET100                                                             = 18, 
      kHLT_Photon120_R9Id90_HE10_Iso40_EBOnly_PFMET40                                     = 19,
      kHLT_Photon22_R9Id90_HE10_Iso40_EBOnly_VBF                                          = 20,
      kHLT_Photon90_CaloIdL_PFHT600                                                       = 21,
      kHLT_DoublePhoton60                                                                 = 22,
      kHLT_DoublePhoton85                                                                 = 23,
      kHLT_Photon22_R9Id90_HE10_IsoM                                                      = 24,
      kHLT_Photon50_R9Id90_HE10_IsoM                                                      = 25,
      kHLT_Photon75_R9Id90_HE10_IsoM                                                      = 26,
      kHLT_Photon90_R9Id90_HE10_IsoM                                                      = 27,
      kHLT_Photon120_R9Id90_HE10_IsoM                                                     = 28,
      kHLT_Photon165_R9Id90_HE10_IsoM                                                     = 29,
      kHLT_ECALHT800                                                                      = 30,
   };

   inline bool photonTriggerResult(HLTPhotonBit_t trigName) {
      return HLTPho>>trigName&1;
   }


private:
   bool _isData;
};

#endif
