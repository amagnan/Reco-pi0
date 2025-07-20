import ROOT
ROOT.gStyle.SetOptStat("eMRuo")

# Open file and tree
file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up branch addresses
pho_e = ROOT.std.vector('double')()
pho_px = ROOT.std.vector('double')()
pho_py = ROOT.std.vector('double')()
pho_pz = ROOT.std.vector('double')()
genpho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()

tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)
tree.SetBranchAddress("genPhotonE", genpho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)

# Create histograms
hist_matched = ROOT.TH1F("hist_matched", "Gen Photon Energy;E [GeV];Counts", 100, 0, 5)
hist_unmatched = ROOT.TH1F("hist_unmatched", "Gen Photon Energy;E [GeV];Counts", 100, 0, 5)

# Create 2D histogram: x = gen photon energy, y = matched (1) or unmatched (0)
hist2d = ROOT.TH2F("hist2d", "Matched/Unmatched vs. Gen Photon Energy;Gen Photon Energy [GeV];Matched (1) / Unmatched (0)",
                   100, 0, 10, 2, 0, 1.2)

# Event loop
for i_event in range(tree.GetEntries()):
    tree.GetEntry(i_event)

    if len(genpho_e) == 0 or len(pho_e) == 0:
        continue

    # Build TLorentzVectors
    reco_photons = [ROOT.TLorentzVector(pho_px[i], pho_py[i], pho_pz[i], pho_e[i]) for i in range(pho_e.size())]
    gen_photons = [ROOT.TLorentzVector(genpho_px[i], genpho_py[i], genpho_pz[i], genpho_e[i]) for i in range(genpho_e.size())]

    # Check each gen photon for match
    for gen_photon in gen_photons:
        matched = False
        for reco_photon in reco_photons:
            if gen_photon.DeltaR(reco_photon) < 0.04:
                matched = True
                break
        if matched:
            hist_matched.Fill(gen_photon.E())
            hist2d.Fill(gen_photon.E(), 1)
        else:
            hist_unmatched.Fill(gen_photon.E())
            hist2d.Fill(gen_photon.E(), 0)

# Plot
canvas = ROOT.TCanvas("c", "Gen Photon Matching Energy", 800, 600)

hist_matched.SetLineColor(ROOT.kGreen+2)
hist_matched.SetLineWidth(2)
hist_matched.Draw("HIST")

hist_unmatched.SetLineColor(ROOT.kRed)
hist_unmatched.SetLineStyle(2)
hist_unmatched.SetLineWidth(2)
hist_unmatched.Draw("HIST SAME")

legend = ROOT.TLegend(0.6, 0.75, 0.88, 0.88)
legend.AddEntry(hist_matched, "Matched Gen Photons", "l")
legend.AddEntry(hist_unmatched, "Unmatched Gen Photons", "l")
legend.Draw()

canvas.SaveAs("genPhoton_energy_matched_vs_unmatched.png")

# Plot 2D histogram and profile
canvas2 = ROOT.TCanvas("c2", "Matched/Unmatched vs. Gen Photon Energy", 800, 600)
hist2d.Draw("COLZ")

profile = hist2d.ProfileX()
profile.SetLineColor(ROOT.kRed + 1)
profile.SetLineWidth(2)
profile.Draw("same")

canvas2.SaveAs("genPhoton_matched_vs_energy_2d.png")
