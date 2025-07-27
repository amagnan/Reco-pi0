# Reco‑π⁰: π⁰ Reconstruction Study in FCC‑ee Si‑W ECAL

This project investigates the performance of neutral pion (π⁰) reconstruction in the CLD detector concept for the FCC‑ee, using simulation datasets with varying Si‑W electromagnetic calorimeter (ECAL) cell sizes: 5 mm × 5 mm, 1 cm × 1 cm, 1.5 cm × 1.5 cm, and 2 cm × 2 cm.

## 🧪 Overview

- **Simulation**:  
 The process simulated is $Z \rightarrow \tau^+ \tau^-$, where $\tau \rightarrow \pi^0 \rightarrow \gamma\gamma$. 
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

- **Analysis Strategy**:
1. In "pi0 mass", events are classified based on the number of gen-level $\pi^0$. In each type of events, the mass of $\pi^0$ is calculated using the invariant mass of two matched reco-level photons, and the distribution of mass and $\Delta R$ between these two photons are plotted.
2. In "photon_match", the script describe the matching between gen-level photon pair and between gen-level and reco-level photons.
3. in "nReco vs. gen delta R", the script calcualtes the distribution of the number of reco-photon matched with each gen-photon pair with respect to the $\Delta R$ between the gen-photon pair. With the theoretical calculated min $\Delta R$ resolutions of different cell sizes, it illustrate the granularity on reconstruction.
4. In "energy_ratio", the scirpt calculate the energy of each reco-photon and total energy of corresponding gen-photon pair with variying granularities. The ratio around one is identified as the case merged photon, since a single reco-photon has similar mass with $\pi^0$.
5. In "E_threshold", the script investigates the effect of minimum energy for deposition on Si-W cells. From the plot, a clear threshold can be observed.


- **Data**:  
ROOT files containing simulation outputs for each cell size configuration. The analysis compares reconstruction performance across all four granularity setups.

---

