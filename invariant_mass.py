import ROOT
from itertools import combinations

file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up generator-level photon branches.
genpho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()

tree.SetBranchAddress("genPhotonE", genpho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)

# Parameters in MeV units:
MASS_LOW = 0.0
MASS_HIGH = 300.0
N_BINS = 150

# Create histograms with no cut, with ΔR cut, and 2D histogram for mass vs ΔR.
hist_all = ROOT.TH1F(
    "invMassHist_all", 
    "Two-Photon Invariant Mass (All Pairs); Mass (MeV); Events",
    N_BINS,
    MASS_LOW,
    MASS_HIGH
)

hist_cut = ROOT.TH1F(
    "invMassHist_cut", 
    "Two-Photon Invariant Mass (With #DeltaR Cut); Mass (MeV); Events",
    N_BINS,
    MASS_LOW,
    MASS_HIGH
)

hist_massDR = ROOT.TH2F(
    "massDR_hist",
    "Mass vs #DeltaR; Mass (MeV); #DeltaR",
    N_BINS,
    MASS_LOW,
    MASS_HIGH,
    50, 0.0, 1.0  # DR range from 0 to 1
)

n_skipped = 0
n_pairs_all = 0
n_pairs_cut = 0

for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    n_photons = genpho_e.size()
    # Skip events with fewer than 2 photons.
    if n_photons < 2:
        n_skipped += 1

    # Construct 4-vectors for each photon.
    photons = []
    for j in range(n_photons):
        p4 = ROOT.TLorentzVector()
        p4.SetPxPyPzE(
            genpho_px[j] * 1e3,  # Convert units from GeV to MeV.
            genpho_py[j] * 1e3,
            genpho_pz[j] * 1e3,
            genpho_e[j] * 1e3
        )
        photons.append(p4)

    # Fill all photon pairs
    for (i1, i2) in combinations(range(n_photons), 2):
        g1, g2 = photons[i1], photons[i2]
        pair = g1 + g2
        inv_mass = pair.M()
        delta_r = g1.DeltaR(g2)
        pair_pt = pair.Pt()

        # 2D histogram for mass vs ΔR.
        hist_massDR.Fill(inv_mass, delta_r)

        # Histogram for all pairs.
        hist_all.Fill(inv_mass)
        n_pairs_all += 1

        # Apply mass-dependent DR cut.
        mass = hist_cut.GetMean()
        delta_r_max = 2 * 135 / pair_pt  # DR = 2*m_{π0}/pT.
        if delta_r < delta_r_max:
            hist_cut.Fill(inv_mass)
            n_pairs_cut += 1

print(f"Skipped {n_skipped} events with <2 photons")
print(f"Total pairs: {n_pairs_all}")
print(f"Pairs passing DR cut: {n_pairs_cut} ({100.*n_pairs_cut/n_pairs_all:.1f}%)")

# Save results in root and png files.
out = ROOT.TFile("massDR_results.root", "RECREATE")
hist_all.Write()
hist_cut.Write()
hist_massDR.Write()
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
hist_massDR.Draw("COLZ")  # Color plot with Z scale.
c_2d.SaveAs("mass_vs_DR_2D.png")

file.Close()
print("results saved")
