"""
    This script pairs gen photons and matches them to reconstructed photons. The 2d plot of nReco vs. ΔR is generated,
    showing the number of matched reconstructed photons for each pair of gen photons.
"""
import ROOT
import numpy as np
from array import array
ROOT.gStyle.SetOptStat("eMRuo")

# Open ROOT file and access the tree
file = ROOT.TFile("miniTree_1M.root")
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
DELTA_R_CUT = 0.5
MASS_WINDOW = 0.05  # 50 MeV mass tolerance for π⁰
cell_size = 0.005
R_in = 2.15  # Inner ECAL radius in meters
R_outer = 2.35
min_deltaR_in= np.sqrt((cell_size * 3/R_in)**2 + (0.5*cell_size * 3/R_in)**2)  # Minimum ΔR based on ECAL geometry
min_deltaR_outer = np.sqrt((cell_size * 3/R_outer)**2 + (0.5*cell_size * 3/R_outer)**2)
# Lists for plotting
deltaR = []
nReco = []
reco_theta = []
# Optional histogram for valid ΔR between gen photons
hist_valid_dR = ROOT.TH1F("genPhotonDeltaR", "ΔR of gen photon pairs (π⁰ candidates)", 100, 0, 0.5)
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

    if len(genpho_e) == 0 or len(pho_e) == 0 or len(genpi0_m) == 0:
        continue

    # Construct TLorentzVectors
    reco_photons = [ROOT.TLorentzVector(pho_px[j], pho_py[j], pho_pz[j], pho_e[j]) for j in range(pho_e.size())]
    gen_photons = [ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j]) for j in range(genpho_e.size())]        

    used_gen_indices = set()
    used_pi0_indices = set()

    # Pair gen photons with π⁰ candidates
    for i in range(len(gen_photons)):
        if i in used_gen_indices:
            continue
        for j in range(i + 1, len(gen_photons)):
            theta = gen_photons[i].Theta()
            if theta < min_theta or theta > max_theta:
                continue

            if j in used_gen_indices:
                continue

            p1 = gen_photons[i]
            p2 = gen_photons[j]
            dr = p1.DeltaR(p2)
            pair_mass = (p1 + p2).M()

            # ΔR and mass window cuts
            if dr > DELTA_R_CUT:
                continue
            if abs(pair_mass - PI0_MASS) > MASS_WINDOW:
                continue

            # Match pair to closest gen π⁰ by mass
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

                # Match each gen photon to reco photon
                used_reco_indices = set()
                n_reco = 0
                for gen_photon in [p1, p2]:
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
                        n_reco += 1
                        used_reco_indices.add(best_reco_idx)

                deltaR.append(p1.DeltaR(p2))
                nReco.append(n_reco)
                hist_valid_dR.Fill(p1.DeltaR(p2))

max_dr = max(deltaR)
# Split data into even/odd reco photon count
deltaR_even, nReco_even = [], []
deltaR_odd, nReco_odd = [], []

for dr, nr in zip(deltaR, nReco):
    if nr % 2 == 0:
        deltaR_even.append(dr)
        nReco_even.append(nr)
    else:
        deltaR_odd.append(dr)
        nReco_odd.append(nr)

# Create TGraphs
hist2d = ROOT.TH2F("hist2d", "nReco vs. #DeltaR between gen photon pairs (5mm x 5mm)",
                   50, 0, 0.03,   # ΔR bins
                   5, -0.5, 4.5)  # nReco bins (0 to 4)

# Fill TH2F
for dr, nr in zip(deltaR, nReco):
    
    hist2d.Fill(dr, nr)

# Draw 2D histogram
canvas = ROOT.TCanvas("canvas", "nReco vs. Gen #DeltaR", 800, 600)
hist2d.GetXaxis().SetTitle("#DeltaR between gen photon pairs (pi^{0} candidates)")
hist2d.GetYaxis().SetTitle("Number of matched reco photons")
hist2d.SetStats(0)
hist2d.Draw("COLZ")

profile = hist2d.ProfileX()
profile.SetLineColor(ROOT.kRed + 1)
profile.SetLineWidth(2)
profile.Draw("same")  # Overlay on 2D histogram

# Draw vertical resolution lines
line_inner = ROOT.TLine(min_deltaR_in, -0.5, min_deltaR_in, 4.5)
line_outer = ROOT.TLine(min_deltaR_outer, -0.5, min_deltaR_outer, 4.5)
line_inner.SetLineColor(ROOT.kGreen+2)
line_inner.SetLineStyle(2)
line_inner.SetLineWidth(2)
line_outer.SetLineColor(ROOT.kMagenta+2)
line_outer.SetLineStyle(2)
line_outer.SetLineWidth(2)
line_inner.Draw()
line_outer.Draw()

# Add legend
legend = ROOT.TLegend(0.60, 0.75, 0.88, 0.88)
legend.AddEntry(line_inner, f"Inner ECAL #DeltaR ({min_deltaR_in:.3})", "l")
legend.AddEntry(line_outer, f"Outer ECAL #DeltaR ({min_deltaR_outer:.3})", "l")
legend.Draw()

canvas.SaveAs("th2_nReco_vs_deltaR.png")

            # Pairing logic explanation:
            # For each unique pair of gen photons (i, j):
            #   - Only consider pairs where both photons are not already used in another pair.
            #   - Calculate the angle theta of the first photon and require it to be within the range of reco photon thetas.
            #   - Compute the ΔR (angular separation) between the two gen photons.
            #   - Compute the invariant mass of the pair.
            #   - Apply two selection cuts:
            #       1. ΔR must be less than DELTA_R_CUT (e.g., 0.5).
            #       2. The pair mass must be within MASS_WINDOW (e.g., 0.05 GeV) of the nominal π⁰ mass (PI0_MASS).
            #   - For pairs passing both cuts, find the closest unused gen π⁰ candidate by mass.
            #   - If a gen π⁰ is found, mark both gen photons and the π⁰ as used (so they can't be reused).
            #   - For each photon in the selected pair, match to the closest unused reco photon (ΔR < 0.04, each reco used once).
            #   - Count the number of matched reco photons (n_reco) for the pair.
            #   - Store ΔR between the gen photon pair and n_reco for later plotting.
