import ROOT
from itertools import combinations

file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up reconstructed photon branches. Extract energy and momenta from the tree.
pho_e = ROOT.std.vector('double')()
pho_px = ROOT.std.vector('double')()
pho_py = ROOT.std.vector('double')()
pho_pz = ROOT.std.vector('double')()
genpho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()
genpi0_e = ROOT.std.vector('double')()

# Set branch addresses so the vectors are filled for each event
tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)
tree.SetBranchAddress("genPhotonE", genpho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)
tree.SetBranchAddress("genPi0E", genpi0_e)

# Histograms
hist_minDR = ROOT.TH1F("minDR", "Minimum delta R", 100, 0, 0.05)
hist_energy_ratio = ROOT.TH1F("energy_ratio", "Reco / Gen Photon Energy Ratio", 100, 0, 2)

# Loop over events
for i in range(tree.GetEntries()):
    tree.GetEntry(i)  # Load event data

    reco_photons = []
    gen_photons = []

    # Build reco photon list
    for j in range(pho_e.size()):
        p_reco = ROOT.TLorentzVector(pho_px[j], pho_py[j], pho_pz[j], pho_e[j])
        reco_photons.append((p_reco, pho_e[j]))

    # Build gen photon list
    for j in range(genpho_e.size()):
        p_gen = ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j])
        gen_photons.append((p_gen, genpho_e[j]))

    used_gen = set()

    for p_reco, e_reco in reco_photons:
        # Skip if no gen photons in event
        if len(gen_photons) == 0:
            continue

        min_dr = float("inf")
        best_gen_idx = -1

        # Find best match by ΔR
        for idx, (p_gen, e_gen) in enumerate(gen_photons):
            if idx in used_gen:
                continue
            dr = p_reco.DeltaR(p_gen)
            if dr < min_dr:
                min_dr = dr
                best_gen_idx = idx

        # Fill min ΔR histogram
        hist_minDR.Fill(min_dr)

        # Fill energy ratio histogram if match found
        if best_gen_idx != -1:
            e_gen = gen_photons[best_gen_idx][1]
            if e_gen > 0:
                energy_ratio = e_reco / e_gen
                hist_energy_ratio.Fill(energy_ratio)
                used_gen.add(best_gen_idx)

# Draw and save ΔR histogram
canvas = ROOT.TCanvas("canvas", "Minimum Delta R Histogram", 800, 600)
hist_minDR.SetXTitle("Minimum Delta R")
hist_minDR.SetYTitle("Entries")
hist_minDR.SetLineColor(ROOT.kBlue)
hist_minDR.Draw()
canvas.SaveAs("min_delta_r_histogram.png")

# Draw and save energy ratio histogram
canvas2 = ROOT.TCanvas("canvas2", "Reco / Gen Energy Ratio", 800, 600)
hist_energy_ratio.SetXTitle("Reco / Gen Photon Energy")
hist_energy_ratio.SetYTitle("Entries")
hist_energy_ratio.SetLineColor(ROOT.kRed)
hist_energy_ratio.Draw()
canvas2.SaveAs("reco_gen_energy_ratio.png")

# Save histograms to ROOT file
out_file = ROOT.TFile("min_delta_r_results.root", "RECREATE")
hist_minDR.Write()
hist_energy_ratio.Write()
out_file.Close()

# Close input file
file.Close()
