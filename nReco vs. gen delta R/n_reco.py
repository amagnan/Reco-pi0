"""
    This script pairs gen photons and matches them to reconstructed photons. The 2d plot of nReco vs. ΔR is generated,
    showing the number of matched reconstructed photons for each pair of gen photons.
    It also visualizes the energy and theta distribution of matched gen and reco photons.
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

# Constants:
PI0_MASS = 0.135  # GeV
MASS_WINDOW = 0.05  # 50 MeV mass tolerance for π⁰
cell_size = 0.005
R_in = 2.15  # Inner ECAL radius in meters
R_outer = 2.35
# Given that the PF algorithm identify clusters, the cell size in min delta R calulation should be multiplied by 3.
min_deltaR_in= np.sqrt((cell_size * 3/R_in)**2 + (0.5*cell_size * 3/R_in)**2)  # Minimum ΔR based on ECAL geometry
min_deltaR_outer = np.sqrt((cell_size * 3/R_outer)**2 + (0.5*cell_size * 3/R_outer)**2)
# Lists for plotting
deltaR = []
nReco = []
reco_theta = []
max_e = 19
# Optional histogram for valid ΔR between gen photons
hist_valid_dR = ROOT.TH1F("genPhotonDeltaR", "ΔR of gen photon pairs (π⁰ candidates)", 100, 0, 0.5)
hist_gen_energy = ROOT.TH1F("genPhotonEnergy", "Gen Photon Energy;E [GeV];Counts", 100, 0, max_e)
hist_reco_energy = ROOT.TH1F("recoPhotonEnergy", "Reco Photon Energy;E [GeV];Counts", 100, 0, max_e)
hist_gen_theta = ROOT.TH1F("genPhotonTheta", "Gen Photon Theta;Theta [rad];Counts", 100, 0, np.pi)
hist_reco_theta = ROOT.TH1F("recoPhotonTheta", "Reco Photon Theta;Theta [rad];Counts", 100, 0, np.pi)
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
theta_cut_failed = 0
theta_cut_passed = 0
# Loop over events
for i_event in range(tree.GetEntries()):
    tree.GetEntry(i_event)

    if len(genpho_e) == 0 or len(genpi0_m) == 0:
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
            theta1 = gen_photons[i].Theta()
            theta2 = gen_photons[j].Theta()
            # Count gen photons for theta cut

            if theta1 < min_theta or theta1 > max_theta:
                theta_cut_failed += 1
                continue
            if theta2 < min_theta or theta2 > max_theta:
                theta_cut_failed += 1
                continue
            theta_cut_passed += 2

            if j in used_gen_indices:
                continue

            p1 = gen_photons[i]
            p2 = gen_photons[j]
            dr = p1.DeltaR(p2)
            pair_mass = (p1 + p2).M()

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
                    hist_gen_energy.Fill(gen_photon.E())
                    hist_gen_theta.Fill(gen_photon.Theta())
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
                        hist_reco_energy.Fill(reco_photons[best_reco_idx].E())
                        hist_reco_theta.Fill(reco_photons[best_reco_idx].Theta())

                deltaR.append(p1.DeltaR(p2))
                nReco.append(n_reco)
                hist_valid_dR.Fill(p1.DeltaR(p2))

max_dr = max(deltaR)
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
legend = ROOT.TLegend(0.35, 0.75, 0.65, 0.88)
legend.AddEntry(line_inner, f"Inner ECAL #DeltaR ({min_deltaR_in:.3})", "l")
legend.AddEntry(line_outer, f"Outer ECAL #DeltaR ({min_deltaR_outer:.3})", "l")
legend.Draw()

canvas.SaveAs("th2_nReco_vs_deltaR.png")

# After filling histograms, set the x-axis range to the maximum value
# Find the maximum energy value from both histograms to cover all data
max_gen_e = hist_gen_energy.GetBinLowEdge(hist_gen_energy.GetNbinsX()) + hist_gen_energy.GetBinWidth(hist_gen_energy.GetNbinsX())
max_reco_e = hist_reco_energy.GetBinLowEdge(hist_reco_energy.GetNbinsX()) + hist_reco_energy.GetBinWidth(hist_reco_energy.GetNbinsX())
max_e = max(max_gen_e, max_reco_e)

hist_gen_energy.GetXaxis().SetRangeUser(0, max_e)
hist_reco_energy.GetXaxis().SetRangeUser(0, max_e)

# Draw and save overlaid energy histogram with error bars
canvas_energy = ROOT.TCanvas("canvas_energy", "Gen vs Reco Photon Energy", 800, 600)
hist_gen_energy.SetLineColor(ROOT.kBlue)
hist_gen_energy.SetLineWidth(2)
hist_gen_energy.SetTitle("Gen vs Reco Photon Energy")
hist_gen_energy.GetXaxis().SetTitle("Photon Energy [GeV]")
hist_gen_energy.GetYaxis().SetTitle("Counts")
hist_gen_energy.Draw("E")  # "E" option draws error bars
hist_reco_energy.SetLineColor(ROOT.kRed)
hist_reco_energy.SetLineWidth(2)
hist_reco_energy.Draw("E SAME")  # "E SAME" overlays with error bars

legend_energy = ROOT.TLegend(0.35, 0.75, 0.65, 0.88)
legend_energy.AddEntry(hist_gen_energy, "Gen Photon", "l")
legend_energy.AddEntry(hist_reco_energy, "Reco Photon", "l")
legend_energy.Draw()
canvas_energy.SaveAs("hist_energy_gen_vs_reco.png")

# Draw and save overlaid theta histogram with error bars
canvas_theta = ROOT.TCanvas("canvas_theta", "Gen vs Reco Photon Theta", 800, 600)
hist_gen_theta.SetLineColor(ROOT.kBlue)
hist_gen_theta.SetLineWidth(2)
hist_gen_theta.SetTitle("Gen vs Reco Photon Theta")
hist_gen_theta.GetXaxis().SetTitle("Photon Theta [rad]")
hist_gen_theta.GetYaxis().SetTitle("Counts")
hist_gen_theta.Draw("E")
hist_reco_theta.SetLineColor(ROOT.kRed)
hist_reco_theta.SetLineWidth(2)
hist_reco_theta.Draw("E SAME")
legend_theta = ROOT.TLegend(0.35, 0.75, 0.65, 0.88)
legend_theta.AddEntry(hist_gen_theta, "Gen Photon", "l")
legend_theta.AddEntry(hist_reco_theta, "Reco Photon", "l")
legend_theta.Draw()
canvas_theta.SaveAs("hist_theta_gen_vs_reco.png")

canvas.Update()
print(f"Number of entries in TH2:{hist2d.GetEntries()}")
print(f"Number of entries in gen histo: {hist_gen_theta.GetEntries()}")
print(f"Number of entries in reco histo: {hist_reco_theta.GetEntries()}")

print(f"Number of entries in gen histo: {hist_gen_energy.GetEntries()}")
print(f"Number of entries in reco histo: {hist_reco_energy.GetEntries()}")
print(f"Number of gen photons passing theta cut: {theta_cut_passed}")
print(f"Number of gen photons NOT passing theta cut: {theta_cut_failed}")
