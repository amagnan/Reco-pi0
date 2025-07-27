# Reco‑π⁰: π⁰ Reconstruction Study in FCC‑ee Si‑W ECAL

This project investigates the performance of neutral pion (π⁰) reconstruction in the CLD detector concept for the FCC‑ee, using simulation datasets with varying Si‑W electromagnetic calorimeter (ECAL) cell sizes: 5 mm × 5 mm, 1 cm × 1 cm, 1.5 cm × 1.5 cm, and 2 cm × 2 cm.

## 🧪 Overview

- **Simulation**:  
  The process simulated is \( Z \rightarrow \tau^+ \tau^- \), where subsequent tau decays produce neutral pions:  
  \( \tau \rightarrow \pi^0 \rightarrow \gamma\gamma \).  
  The output of each simulation is stored in a ROOT file containing both generator-level and reconstructed photon information. Each event includes the following structure (sample output from `TTree::Show(1)`):

  
The goal is to evaluate how ECAL granularity impacts π⁰ → γγ reconstruction performance, including efficiency, purity, merging effects, and implications for data acquisition (DAQ) requirements. The analysis workflow uses a ROOT-based pipeline to:

- Match reconstructed photons to generator-level photons using angular distance (ΔR)
- Reconstruct π⁰ candidates from photon pairs
- Compute observables such as ΔR distributions, invariant mass, energy ratios, and thresholds
- Produce 2D histograms (e.g., number of reco photons vs. π⁰ ΔR) and profile plots to study detection performance and shower overlap

This study informs detector optimization by quantifying the trade-offs between calorimeter granularity, photon separation power, and reconstruction reliability.
