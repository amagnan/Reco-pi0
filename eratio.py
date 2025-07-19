"""
This script match the gen-photon pairs and find the corresponding reco-photon pairs.
A theta cut is applied to the gen-photon to ensure they are within the range of reco-photon angles.
It calculates the energy ratio of reco photons to the total energy of the matched gen photon pairs.
It also plots the energy ratio histograms for cases with one and two reco photons.
"""
 
import ROOT
import numpy as np
from array import array
ROOT.gStyle.SetOptStat("eMRuo")

# Open ROOT file and access the tree
file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Define vectors for branches
pho_e = ROOT.std.vector('double')()
pho_px = ROOT.std.vector('double')()
pho_py = ROOT.std.vector('double')()
pho_pz = ROOT.std.vector('double')()
genpho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()
genpi0_e = ROOT.std.vector('double')()
genpi0_m = ROOT.std.vector('double')()

# Set branch addresses
tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)
tree.SetBranchAddress("genPhotonE", genpho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)
tree.SetBranchAddress("genPi0E", genpi0_e)
tree.SetBranchAddress("genPi0M", genpi0_m)

# Constants
PI0_MASS = 0.135  # GeV
MASS_WINDOW = 0.05  # 50 MeV mass tolerance

# Histograms
hist_ratio_1reco = ROOT.TH1F("ratio_1reco", "Reco / Gen Energy Ratio;Reco Energy / Gen Pair Energy;Events", 50, 0, 1.5)
hist_ratio_2reco = ROOT.TH1F("ratio_2reco", "Reco / Gen Energy Ratio (2 reco photons);Reco Energy / Gen Pair Energy;Events", 50, 0, 1.5)

reco_theta = []
# Optional histogram for valid ΔR between gen photons
for i_event in range(tree.GetEntries()):
    tree.GetEntry(i_event)

    if len(genpho_e) == 0 or len(pho_e) == 0 or len(genpi0_m) == 0:
        continue

    # Construct TLorentzVectors
    reco_photons = [ROOT.TLorentzVector(pho_px[j], pho_py[j], pho_pz[j], pho_e[j]) for j in range(pho_e.size())]
    gen_photons = [ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j]) for j in range(genpho_e.size())]

    for reco in reco_photons:
        theta = reco.Theta()
        reco_theta.append(theta)
min_theta = min(reco_theta)
max_theta = max(reco_theta)

# Loop over events
for i_event in range(tree.GetEntries()):
    tree.GetEntry(i_event)

    if len(genpho_e) < 2 or len(genpi0_m) == 0:
        continue

    # Create TLorentzVectors
    reco_photons = [ROOT.TLorentzVector(pho_px[j], pho_py[j], pho_pz[j], pho_e[j]) for j in range(pho_e.size())]
    gen_photons = [ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j]) for j in range(genpho_e.size())]

    used_gen_indices = set()
    used_pi0_indices = set()

    # Loop over gen photon pairs
    for i in range(len(gen_photons)):
        if i in used_gen_indices:
            continue
        theta1 = gen_photons[i].Theta()
        if theta1 < min_theta or theta1 > max_theta:
            continue
        for j in range(i + 1, len(gen_photons)):
            if j in used_gen_indices:
                continue
            
            theta2 = gen_photons[j].Theta()
            if theta2 < min_theta or theta2 > max_theta:
                continue

            p1 = gen_photons[i]
            p2 = gen_photons[j]
            pair_mass = (p1 + p2).M()
            if abs(pair_mass - PI0_MASS) > MASS_WINDOW:
                continue

            # Match to genpi0 by mass.
            min_mass_diff = float('inf')
            best_pi0_idx = -1
            for k in range(len(genpi0_m)):
                if k in used_pi0_indices:
                    continue
                mass_diff = abs(pair_mass - genpi0_m[k])
                if mass_diff < min_mass_diff:
                    min_mass_diff = mass_diff
                    best_pi0_idx = k

            if best_pi0_idx >= 0:
                used_pi0_indices.add(best_pi0_idx)
                used_gen_indices.update([i, j])

                # Match gen photons to reco photons
                matched_reco = []
                used_reco_indices = set()
                for gen_photon in [p1, p2]:
                    theta = gen_photon.Theta()
                    best_dr = float('inf')
                    best_reco_idx = -1
                    for idx, reco_photon in enumerate(reco_photons):
                        if idx in used_reco_indices:
                            continue
                        dr = reco_photon.DeltaR(gen_photon)
                        if dr < best_dr:
                            best_dr = dr
                            best_reco_idx = idx
                    if best_dr < 0.04 and best_reco_idx != -1:
                        matched_reco.append(reco_photons[best_reco_idx])
                        used_reco_indices.add(best_reco_idx)

                total_gen_energy = p1.E() + p2.E()
                if len(matched_reco) == 1:
                    hist_ratio_1reco.Fill(matched_reco[0].E() / total_gen_energy)
                elif len(matched_reco) == 2:
                    for reco in matched_reco:
                        hist_ratio_2reco.Fill(reco.E() / total_gen_energy)

# Adjust Y-axis maximum
max_y = max(hist_ratio_1reco.GetMaximum(), hist_ratio_2reco.GetMaximum())
hist_ratio_1reco.SetMaximum(1.2 * max_y)

# Draw histograms
canvas = ROOT.TCanvas("c_ratio", "Reco / Gen Energy Ratio", 800, 600)
hist_ratio_1reco.SetLineColor(ROOT.kBlue + 2)
hist_ratio_1reco.SetLineWidth(2)
hist_ratio_1reco.Draw("HIST")

hist_ratio_2reco.SetLineColor(ROOT.kRed + 1)
hist_ratio_2reco.SetLineStyle(2)
hist_ratio_2reco.SetLineWidth(2)
hist_ratio_2reco.Draw("HIST SAME")

# Legend
legend = ROOT.TLegend(0.55, 0.70, 0.88, 0.88)
legend.AddEntry(hist_ratio_1reco, "1 Reco Photon", "l")
legend.AddEntry(hist_ratio_2reco, "2 Reco Photons (each)", "l")
legend.Draw()

canvas.SaveAs("Reco_Gen_Energy_Ratio.png")
print(min_theta, max_theta)