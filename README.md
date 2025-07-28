# Reco‑π⁰: π⁰ Reconstruction Study in FCC‑ee Si‑W ECAL

This project investigates the performance of neutral pion (π⁰) reconstruction in the CLD detector concept for the FCC‑ee, using simulation datasets with varying Si‑W electromagnetic calorimeter (ECAL) cell sizes: 5 mm × 5 mm, 1 cm × 1 cm, 1.5 cm × 1.5 cm, and 2 cm × 2 cm.

## Overview

- **Simulation**:  
 The process simulated is $Z \rightarrow \tau^+ \tau^-$, where $\tau$ decay generates $\pi^0$, and $\pi^0 \rightarrow \gamma\gamma$. 
  The output of each simulation is stored in a ROOT file containing both generator-level and reconstructed photon information. Each event includes the following structure (sample output from `TTree::Show(1)`):
```
root [3] outtree->Show(1)
======> EVENT:1
 beamE           = 45.5991
 nPhotons        = 0
 nGenPhotons     = 4
 nGenPi0s        = 0
 nGenTaus        = 2
 nRecoTausHad    = 1
 photonP         = (vector<double>*)0x2ea9fb0
 photonE         = (vector<double>*)0x2ea9f60
 photonPx        = (vector<double>*)0x31cc7a0
 photonPy        = (vector<double>*)0x2e45e20
 photonPz        = (vector<double>*)0x31ee420
 photonM         = (vector<double>*)0x2fb6710
 genPhotonP      = (vector<double>*)0x32100a0
 genPhotonE      = (vector<double>*)0x27ded90
 genPhotonPx     = (vector<double>*)0x27e02e0
 genPhotonPy     = (vector<double>*)0x3243ee0
 genPhotonPz     = (vector<double>*)0x3253920
 genPhotonM      = (vector<double>*)0x3263360
 genPi0P         = (vector<double>*)0x3272da0
 genPi0E         = (vector<double>*)0x32827e0
 genPi0Px        = (vector<double>*)0x3292220
 genPi0Py        = (vector<double>*)0x32a1c60
 genPi0Pz        = (vector<double>*)0x32b16a0
 genPi0M         = (vector<double>*)0x32c10e0
```
miniTree.root is data with photon energy > 0.1 GeV and cell size 5 x 5mm. The other ROOT files has lower energy cut. File end with modifEcal1 corresponds to cell size 1cm, file end with modifEcal1p5 conrresponds to cell size 1.5x1.5cm, and file end with modifEcal2 corresponds to cell size 2x2cm. There are other simulation outputs with one milion events: https://www.hep.ph.ic.ac.uk/~magnan/miniTree_1M.root and http://wwwae.ciemat.es/~cepeda/FCC/miniTree_1M_22Jul.root. They both simulates cell size 5x5mm, but later one has a lower energy cut.

- **Objective**:  
Assess the effect of ECAL transverse granularity on π⁰ → γγ reconstruction, with a focus on:
-photon matching (gen-level photon and reco-level photon)
-angular & energy resolution
-detector threshold behavior
-energy reconstruction

- **Analysis Strategy**:Threshold detection behavior

Energy reconstruction performance

Analysis Strategy

1.`pi0_mass/`:
Classify events by the number of gen-level π⁰. For each class, compute π⁰ invariant mass from two matched reco-photons and study its distribution along with the corresponding $\Delta R$.

2.`photon_match/`:
Match gen-level photons (from π⁰ decay) to reco-level photons based on the smallest angular separation, and evaluate matching accuracy.

3.`nReco_vs_gen_dR/`:
Analyze the number of reco-photons associated with each gen-photon pair as a function of their gen-level $\Delta R$. Overlay theoretical angular resolution limits for different cell sizes.

4.`energy_ratio/`:
Compare the energy of each reco-photon to the total energy of its corresponding gen-photon pair. A ratio near 1 suggests photon merging (i.e., two photons reconstructed as one).

5.`E_threshold/`:
Investigate energy deposition thresholds in Si-W cells. Plots reveal a clear onset in detection efficiency tied to cell granularity and material properties.


