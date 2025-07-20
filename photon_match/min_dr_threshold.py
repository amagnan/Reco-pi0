"""
This script finds the delta R threshold for matching reco-photons to gen-photons.
It also calculates the energy ratio of reco photons to the total energy of the matched gen photon pairs.
"""

import ROOT
ROOT.gStyle.SetOptStat("eMRuo")

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
hist_minDR = ROOT.TH1F("minDR", "Minimum delta R", 100, 0, 0.1)
hist_energy_ratio = ROOT.TH1F("energy_ratio", "Reco / Gen Photon Energy Ratio", 100, 0, 2)
reco_theta = []
# Find the minimum and maximum theta values for reco photons.
for i_event in range(tree.GetEntries()):
    tree.GetEntry(i_event)

    if len(genpho_e) == 0 or len(pho_e) == 0:
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
for i in range(tree.GetEntries()):
    tree.GetEntry(i)  # Load event data
    if len(genpi0_e) == 0:
        continue

    reco_photons = []
    gen_photons = []

    # Build reco photon list (only store index and TLorentzVector)
    for j in range(pho_e.size()):
        p_reco = ROOT.TLorentzVector(pho_px[j], pho_py[j], pho_pz[j], pho_e[j])
        reco_photons.append(p_reco)

    # Build gen photon list (only store index and TLorentzVector)
    for j in range(genpho_e.size()):
        p_gen = ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j])
        gen_photons.append(p_gen)
  
    pairs = []
    used_gen = []
    
    for i_reco in range(len(reco_photons)):
        dR = []
        p_reco = reco_photons[i_reco]
        if len(gen_photons) == 0:
            continue
        for j_gen in range(len(gen_photons)):
            p_gen = gen_photons[j_gen]
            theta = p_gen.Theta()
            if theta < min_theta or theta > max_theta:
                continue
            dr = p_reco.DeltaR(p_gen)
            dR.append(dr)
        if not dR:
            continue  # Skip if no valid gen photons for this reco photon
        min_dr = min(dR)
        index_gen = dR.index(min_dr)
        #if min_dr > 0.04:  # Use min_dr here, not dr
            #continue
        if index_gen in used_gen:
            continue
        pairs.append((p_reco, gen_photons[index_gen]))
        used_gen.append(index_gen)

    for reco, gen in pairs:
        theta = gen.Theta()
        if theta < min_theta or theta > max_theta:
            continue
        dr = reco.DeltaR(gen)
        hist_minDR.Fill(dr)
        e_ratio = reco.E() / gen.E() if gen.E() > 0 else 0
        hist_energy_ratio.Fill(e_ratio)

    

# Draw and save ΔR histogram
canvas = ROOT.TCanvas("canvas", "Minimum Delta R Histogram", 800, 600)
hist_minDR.SetXTitle("Minimum Delta R")
hist_minDR.SetYTitle("Entries")
hist_minDR.SetLineColor(ROOT.kBlue)
hist_minDR.Draw()
canvas.SaveAs("min_delta_r_histogram.png")

fit_range_min = 0.6
fit_range_max = 1.4
hist_energy_ratio.GetXaxis().SetRangeUser(fit_range_min, fit_range_max)

fit_func = ROOT.TF1("fit_func", "gaus", fit_range_min, fit_range_max)
# Optional: Set initial parameter guesses: [constant, mean, sigma]
fit_func.SetParameters(hist_energy_ratio.GetMaximum(), 1.0, 0.1)

fit_result = hist_energy_ratio.Fit(fit_func, "RS")  # R = fit in range, S = return fit result

mean = fit_func.GetParameter(1)
sigma = fit_func.GetParameter(2)
print(f"Gaussian Fit Mean = {mean:.4f}")
print(f"Gaussian Fit Sigma = {sigma:.4f}")
# Histograms for the new energy ratio plots
hist_ratio_1reco = ROOT.TH1F("ratio_1reco", "Reco/Gen Energy Ratio (1 Reco Photon);RecoE / (GenE1 + GenE2);Entries", 100, 0, 2)
hist_ratio_2reco_1 = ROOT.TH1F("ratio_2reco_1", "Reco/Gen Energy Ratio (2 Reco Photons) - Photon 1", 100, 0, 2)
hist_ratio_2reco_2 = ROOT.TH1F("ratio_2reco_2", "Reco/Gen Energy Ratio (2 Reco Photons) - Photon 2", 100, 0, 2)

# Group pairs by gen photon pair (assumes every two gen photons form a pi0)
if len(gen_photons) >= 2:
    for i in range(0, len(gen_photons) - 1, 2):
        theta = gen_photons[i].Theta()
        # Apply theta cut.
        if theta < min_theta or theta > max_theta:
            continue
        gen1 = gen_photons[i]
        gen2 = gen_photons[i+1]
        theta2 = gen_photons[i+1].Theta()
        if theta2 < min_theta or theta2 > max_theta:
            continue
        sum_genE = gen1.E() + gen2.E()

        # Find reco photons matched to either gen1 or gen2
        matched_recos = []
        for reco, gen in pairs:
            if gen == gen1 or gen == gen2:
                matched_recos.append(reco)

        if len(matched_recos) == 1:
            ratio = matched_recos[0].E() / sum_genE if sum_genE > 0 else 0
            hist_ratio_1reco.Fill(ratio)

        elif len(matched_recos) == 2:
            ratio1 = matched_recos[0].E() / sum_genE if sum_genE > 0 else 0
            ratio2 = matched_recos[1].E() / sum_genE if sum_genE > 0 else 0
            hist_ratio_2reco_1.Fill(ratio1)
            hist_ratio_2reco_2.Fill(ratio2)


# Draw and save energy ratio histogram with fit overlay
canvas2 = ROOT.TCanvas("canvas2", "Reco / Gen Energy Ratio", 800, 600)
hist_energy_ratio.SetXTitle("Reco / Gen Photon Energy")
hist_energy_ratio.SetYTitle("Entries")
hist_energy_ratio.SetLineColor(ROOT.kRed)
hist_energy_ratio.Draw()

canvas2.SaveAs("reco_gen_energy_ratio_fit.png")

# Plotting all three histograms
canvas3 = ROOT.TCanvas("canvas3", "Reco/Gen Energy Ratios", 800, 600)
hist_ratio_1reco.SetLineColor(ROOT.kRed + 1)
hist_ratio_2reco_1.SetLineColor(ROOT.kBlue + 1)
hist_ratio_2reco_2.SetLineColor(ROOT.kGreen + 2)

hist_ratio_1reco.SetLineWidth(2)
hist_ratio_2reco_1.SetLineWidth(2)
hist_ratio_2reco_2.SetLineWidth(2)

hist_ratio_1reco.Draw("hist")
hist_ratio_2reco_1.Draw("hist same")
hist_ratio_2reco_2.Draw("hist same")

legend = ROOT.TLegend(0.6, 0.7, 0.88, 0.88)
legend.AddEntry(hist_ratio_1reco, "1 Reco Photon", "l")
legend.AddEntry(hist_ratio_2reco_1, "2 Reco - Photon 1", "l")
legend.AddEntry(hist_ratio_2reco_2, "2 Reco - Photon 2", "l")
legend.Draw()

canvas3.SaveAs("reco_gen_pair_energy_ratios.png")


# Save histograms to ROOT file
out_file = ROOT.TFile("min_delta_r_results.root", "RECREATE")
hist_minDR.Write()
hist_energy_ratio.Write()
out_file.Close()

# Close input file
file.Close()
