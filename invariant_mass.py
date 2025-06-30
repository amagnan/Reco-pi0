import ROOT
from itertools import combinations

file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up reconstructed photon branches
pho_e = ROOT.std.vector('double')()
pho_px = ROOT.std.vector('double')()
pho_py = ROOT.std.vector('double')()
pho_pz = ROOT.std.vector('double')()

tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)

# Histogram setup (MeV units)
M_LOW, M_HIGH, N_BINS = 0.0, 300.0, 150
hist_all = ROOT.TH1F("invMassHist_all", "pi0 Mass (all); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH)
hist_cut = ROOT.TH1F("invMassHist_cut", "pi0 Mass with DR cut; Mass (MeV); Events", N_BINS, M_LOW, M_HIGH)
hist_2d = ROOT.TH2F("massDR", "Mass vs DR; Mass (MeV); DR", N_BINS, M_LOW, M_HIGH, 50, 0.0, 1.0)

n_skipped, n_all, n_cut = 0, 0, 0

for evt in tree:
    n = pho_e.size()
    if n < 2:
        n_skipped += 1
        continue

    photons = []
    for j in range(n):
        p4 = ROOT.TLorentzVector()
        # Convert from GeV to MeV
        p4.SetPxPyPzE(pho_px[j]*1e3, pho_py[j]*1e3, pho_pz[j]*1e3, pho_e[j]*1e3)
        photons.append(p4)

    for a, b in combinations(photons, 2):
        inv_m = (a + b).M()
        dr = a.DeltaR(b)
        pt = (a + b).Pt()

        hist_2d.Fill(inv_m, dr)
        hist_all.Fill(inv_m)
        n_all += 1

        if dr < (2 * 135 / pt):
            hist_cut.Fill(inv_m)
            n_cut += 1

print(f"Skipped {n_skipped} events (<2 photons)")
print(f"Total pairs: {n_all}, After cut: {n_cut} ({n_cut/n_all:.1%})")

# Save results in root and png files.
out = ROOT.TFile("massDR_results.root", "RECREATE")
hist_all.Write()
hist_cut.Write()
hist_2d.Write()
out.Close()

# Draw and save the three histograms.
c_all = ROOT.TCanvas("c_all", "All Pairs", 800, 600)
c_all.cd()
hist_all.SetLineColor(ROOT.kBlue)
hist_all.SetLineWidth(2)
hist_all.Draw()
c_all.SaveAs("mass_all_pairs.png")

c_cut = ROOT.TCanvas("c_cut", "With DR Cut", 800, 600)
c_cut.cd()
hist_cut.SetLineColor(ROOT.kRed)
hist_cut.SetLineWidth(2)
hist_cut.Draw()
c_cut.SaveAs("mass_with_dR_cut.png")

c_2d = ROOT.TCanvas("c_2d", "Mass vs DR", 800, 600)
c_2d.cd()
hist_2d.Draw("COLZ")  # Color plot with Z scale.
c_2d.SaveAs("mass_vs_DR_2D.png")

file.Close()
print("results saved")
