"""
This script processes a ROOT file containing a tree of reconstructed and gen-level photon data.
It calculates invariant mass distributions of photon pairs and classifies events based on the number of generated pi0 mesons.
It classifies events into four categories:
- Class A: 0 pi0 mesons
- Class B: 1 pi0 meson
- Class C: 2 pi0 mesons
- Class D: More than 2 pi0 mesons
and generates histograms for each class.
"""
import ROOT
from itertools import combinations

file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")
ROOT.gStyle.SetOptStat("eMRuo")

# Set up reconstructed photon branches.
pho_e = ROOT.std.vector('double')()
pho_px = ROOT.std.vector('double')()
pho_py = ROOT.std.vector('double')()
pho_pz = ROOT.std.vector('double')()
genpho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()
genpi0_e = ROOT.std.vector('double')()
genpi0_px = ROOT.std.vector('double')()
genpi0_py = ROOT.std.vector('double')()
genpi0_pz = ROOT.std.vector('double')()


n_class_A, n_class_B, n_class_C, n_class_D = 0, 0, 0, 0

# Classify eveents by the number of genpi0.
M_LOW, M_HIGH, N_BINS = 0.0, 300.0, 150
hist_by_class = {
    "A": ROOT.TH1F("invMass_classA", "Mass (Class A, 0 pi0); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH),
    "B": ROOT.TH1F("invMass_classB", "Mass (Class B, 1 pi0); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH),
    "C": ROOT.TH1F("invMass_classC", "Mass (Class C, 2 pi0); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH),
    "D": ROOT.TH1F("invMass_classD", "Mass (Class D, >2 pi0); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH),
}


hist_pi0count_vs_nreco = ROOT.TH2F("pi0count_vs_nreco", "gen pi0 count vs Reco photons; gen pi0s; Reco photons", 5, 0, 5, 10, 0, 10)
hist_nreco_vs_minDR = ROOT.TH2F("nreco_vs_minDR", "Reco photon count vs Min ΔR; Reco photons; Min ΔR", 10, 0, 10, 50, 0.0, 0.2)
hist_genDeltaR = ROOT.TH1F("genPhotonPairDeltaR", "ΔR between gen photon pairs; ΔR; Events", 100, 0, 0.1)
hist_genPhoDeltaR = ROOT.TH1F("genPhoDeltaR", "ΔR between gen photons from pi0 (M ≈ 135 MeV); ΔR; Events", 100, 0, 0.1)

tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)
tree.SetBranchAddress("genPhotonE", genpho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)
tree.SetBranchAddress("genPi0E", genpi0_e)
tree.SetBranchAddress("genPi0Px", genpi0_px)
tree.SetBranchAddress("genPi0Py", genpi0_py)
tree.SetBranchAddress("genPi0Pz", genpi0_pz)

hist_all = ROOT.TH1F("invMassHist_all", "pi0 Mass (all); Mass (MeV); Events", N_BINS, M_LOW, M_HIGH)
hist_cut = ROOT.TH1F("invMassHist_cut", "pi0 Mass with DR cut; Mass (MeV); Events", N_BINS, M_LOW, M_HIGH)
hist_2d = ROOT.TH2F("massDR", "Mass vs DR; Mass (MeV); DR", N_BINS, M_LOW, M_HIGH, 50, 0.0, 0.2)
hist_minDR = ROOT.TH2F("minDR", "Min DR vs Mass; Mass (MeV); Min DR", N_BINS, M_LOW, M_HIGH, 50, 0.0, 0.06)


cell_size = 0.005  # 5 mm
R_in = 2.15  # m
R_outer = 2.35  # m
# Given that the PF algorithm identify clusters, the cell size in min delta R calulation should be multiplied by 3.
min_deltaR_in= np.sqrt((cell_size * 3/R_in)**2 + (0.5*cell_size * 3/R_in)**2)  # Minimum ΔR based on ECAL geometry
min_deltaR_outer = np.sqrt((cell_size * 3/R_outer)**2 + (0.5*cell_size * 3/R_outer)**2)

n_skipped, n_all, n_cut = 0, 0, 0
n_genpi0 = 0

for evt_idx, evt in enumerate(tree):
    n = pho_e.size()
    n_pi0 = genpi0_e.size()
    n_genpi0 += n_pi0

    #  Fill reco-vs-truth count histogram.
    hist_pi0count_vs_nreco.Fill(n_pi0, n)

    # Event classification
    if n_pi0 == 0:
        n_class_A += 1
        class_key = "A"
    elif n_pi0 == 1:
        n_class_B += 1
        class_key = "B"
    elif n_pi0 == 2:
        n_class_C += 1
        class_key = "C"
    else:
        n_class_D += 1
        class_key = "D"

    if n < 2:
        n_skipped += 1
        continue

    photons = []
    for j in range(n):
        p4 = ROOT.TLorentzVector()
        p4.SetPxPyPzE(pho_px[j]*1e3, pho_py[j]*1e3, pho_pz[j]*1e3, pho_e[j]*1e3)
        photons.append(p4)

    inv_m = float('inf')
    DR = 0.
    p_T = 0.
    for a, b in combinations(photons, 2):
        m = (a + b).M()
        dr = a.DeltaR(b)
        pt = (a + b).Pt()
        sig = abs(m - 135)
        if sig < inv_m:
            inv_m = m
            DR = dr
            p_T = pt

    if DR < (2 * 135 / p_T):
        hist_cut.Fill(inv_m)
        n_cut += 1

    hist_by_class[class_key].Fill(inv_m)

    min_dr = float('inf')
    if genpho_e.size() > 0 and len(photons) > 0:
        for i in range(genpho_e.size()):
            gen_p4 = ROOT.TLorentzVector()
            gen_p4.SetPxPyPzE(genpho_px[i]*1e3, genpho_py[i]*1e3, genpho_pz[i]*1e3, genpho_e[i]*1e3)
            for reco in photons:
                dr = reco.DeltaR(gen_p4)
                if dr < min_dr:
                    min_dr = dr
        hist_minDR.Fill(inv_m, min_dr)
        hist_nreco_vs_minDR.Fill(n, min_dr)

        # >>>>>>>>>> Fill gen-level photon pair ΔR histogram
        for j, k in combinations(range(genpho_e.size()), 2):
            g1 = ROOT.TLorentzVector()
            g2 = ROOT.TLorentzVector()
            g1.SetPxPyPzE(genpho_px[j]*1e3, genpho_py[j]*1e3, genpho_pz[j]*1e3, genpho_e[j]*1e3)
            g2.SetPxPyPzE(genpho_px[k]*1e3, genpho_py[k]*1e3, genpho_pz[k]*1e3, genpho_e[k]*1e3)
            hist_genDeltaR.Fill(g1.DeltaR(g2))

            # >>>>>>>>>> New: Fill ΔR from gen photon pairs forming π⁰
            if class_key in ["B", "C", "D"]:
                pi0_candidate = g1 + g2
                if abs(pi0_candidate.M() - 135) < 10:
                    deltaR_gen = g1.DeltaR(g2)
                    hist_genPhoDeltaR.Fill(deltaR_gen)

    # Identify merged photons (lines 97-115)
    # For each gen pi0, check if a single reco photon matches its momentum (ΔR and energy) and if there is a photon pair with mass near 135 MeV
    merged_photon_found = False
    for g in range(genpi0_e.size()):
        genpi0_p4 = ROOT.TLorentzVector()
        genpi0_p4.SetPxPyPzE(genpi0_px[g]*1e3, genpi0_py[g]*1e3, genpi0_pz[g]*1e3, genpi0_e[g]*1e3)

        for reco in photons:
            energy_diff = abs(reco.E() - genpi0_p4.E())
            delta_r = reco.DeltaR(genpi0_p4)
            if energy_diff < 20 and delta_r < 0.05:  # 20 MeV energy window, 0.05 deltaR window.
                for a, b in combinations(photons, 2):
                    m = (a + b).M()
                    if abs(m - 135) < 10:
                        merged_photon_found = True
                        print(f"Event {evt_idx}: Merged photon candidate found. Reco E={reco.E():.1f} MeV, Gen pi0 E={genpi0_p4.E():.1f} MeV, ΔR={delta_r:.3f}, Pair mass={m:.1f} MeV")
                        # Optionally, fill a histogram or store info here
                        break
            if merged_photon_found:
                break
        if merged_photon_found:
            break

    hist_2d.Fill(inv_m, DR)
    hist_all.Fill(inv_m)
    n_all += 1

# [Fit and plot sections unchanged...]

out = ROOT.TFile("massDR_results.root", "RECREATE")
hist_all.Write()
hist_cut.Write()
hist_2d.Write()
hist_minDR.Write()
hist_pi0count_vs_nreco.Write()
hist_nreco_vs_minDR.Write()
hist_genDeltaR.Write()
hist_genPhoDeltaR.Write()
for hist in hist_by_class.values():
    hist.Write()
out.Close()

# >>>>>>>>>> Additional plots
c_pi0_vs_reco = ROOT.TCanvas("c_pi0_vs_reco", "gen π⁰ count vs Reco photons", 800, 600)
hist_pi0count_vs_nreco.Draw("COLZ")
c_pi0_vs_reco.SaveAs("pi0_vs_reco_photons.png")

c_nreco_vs_minDR = ROOT.TCanvas("c_nreco_vs_minDR", "Reco Count vs Min DR", 800, 600)
hist_nreco_vs_minDR.Draw("COLZ")
c_nreco_vs_minDR.SaveAs("nreco_vs_minDR.png")

c_genDR = ROOT.TCanvas("c_genDR", "ΔR Between Gen Photon Pairs", 800, 600)
hist_genDeltaR.Draw()
c_genDR.SaveAs("genPhotonPairDeltaR.png")

c_genPhoDR = ROOT.TCanvas("c_genPhoDR", "ΔR Between Gen Photons from π⁰", 800, 600)
hist_genPhoDeltaR.SetLineColor(ROOT.kRed+1)
hist_genPhoDeltaR.Draw()
c_genPhoDR.SaveAs("genPhoDeltaR_pi0.png")

for key, hist in hist_by_class.items():
    c = ROOT.TCanvas(f"c_class_{key}", f"Mass Distribution: Class {key}", 800, 600)
    hist.SetLineWidth(2)
    hist.SetLineColor(ROOT.kAzure + ord(key))
    hist.Draw()
    c.SaveAs(f"mass_by_class_{key}.png")

file.Close()
print("results saved")