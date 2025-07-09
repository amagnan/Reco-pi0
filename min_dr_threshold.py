import ROOT

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

# Loop over events
for i in range(tree.GetEntries()):
    tree.GetEntry(i)  # Load event data

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
    
    for i in range(len(reco_photons)):
        dR = []
        p_reco = reco_photons[i]
        if len(gen_photons) == 0:
            continue
        for j in range(len(gen_photons)):
            p_gen = gen_photons[j]
            dr = p_reco.DeltaR(p_gen)
            dR.append(dr)
        min_dr = min(dR)
        index_gen = dR.index(min_dr)
        if dr > 0.04:
            continue
        if index_gen in used_gen:
            continue
        pairs.append((p_reco,gen_photons[index_gen]))
        used_gen.append(index_gen)

    for reco, gen in pairs:
        dr = reco.DeltaR(gen)
        hist_minDR.Fill(dr)
        e_ratio = reco.E() / gen.E() if gen.E() >0 else 0
        hist_energy_ratio.Fill(e_ratio)

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
# Close input file
file.Close()
file.Close()
# Close input file
file.Close()

