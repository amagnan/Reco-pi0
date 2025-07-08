import ROOT
from array import array

# Open the ROOT file and get the tree
file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up vectors for branches
pho_e = ROOT.std.vector('double')()
genpho_px = ROOT.std.vector('double')()
genpho_py = ROOT.std.vector('double')()
genpho_pz = ROOT.std.vector('double')()
genpho_e = ROOT.std.vector('double')()

tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("genPhotonPx", genpho_px)
tree.SetBranchAddress("genPhotonPy", genpho_py)
tree.SetBranchAddress("genPhotonPz", genpho_pz)
tree.SetBranchAddress("genPhotonE", genpho_e)

deltaR_even = []
nReco_even = []
deltaR_odd = []
nReco_odd = []

# Loop over events
for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    n_reco = pho_e.size()

    # Skip events with fewer than 2 gen photons
    if genpho_e.size() < 2:
        continue

    # Build list of TLorentzVectors for gen photons
    genpho_all = []
    for j in range(genpho_e.size()):
        p = ROOT.TLorentzVector(genpho_px[j], genpho_py[j], genpho_pz[j], genpho_e[j])
        genpho_all.append(p)

    genpho_remaining = genpho_all.copy()

    while len(genpho_remaining) >= 2:
        min_dm = float('inf')
        best_pair = None
        best_indices = (None, None)

        for m in range(len(genpho_remaining)):
            for n in range(m + 1, len(genpho_remaining)):
                p1 = genpho_remaining[m]
                p2 = genpho_remaining[n]
                inv_mass = (p1 + p2).M()
                dm = abs(inv_mass - 0.135)  # π⁰ mass in GeV
                if dm < min_dm:
                    min_dm = dm
                    best_pair = (p1, p2)
                    best_indices = (m, n)

        # If best pair found, compute ΔR and store it
        if best_pair:
            inv_mass = (best_pair[0] + best_pair[1]).M()
            delta_r = best_pair[0].DeltaR(best_pair[1])
            if abs(inv_mass - 0.135) < 0.005 and delta_r < 0.5:  # Tighter mass window and ΔR cut
                if n_reco % 2 == 0:
                    deltaR_even.append(delta_r)
                    nReco_even.append(n_reco)
                else:
                    deltaR_odd.append(delta_r)
                    nReco_odd.append(n_reco)
            # Remove both photons from list
            for idx in sorted(best_indices, reverse=True):
                del genpho_remaining[idx]
        else:
            break

# Plotting
graph_even = ROOT.TGraph(len(deltaR_even), array('f', deltaR_even), array('f', nReco_even))
graph_odd = ROOT.TGraph(len(deltaR_odd), array('f', deltaR_odd), array('f', nReco_odd))

graph_even.SetMarkerStyle(20)
graph_even.SetMarkerColor(ROOT.kBlue)
graph_even.SetTitle("nReco vs. ΔR of π⁰-like gen photon pairs")

graph_odd.SetMarkerStyle(20)
graph_odd.SetMarkerColor(ROOT.kRed)

canvas = ROOT.TCanvas("canvas", "nReco vs. Gen ΔR", 800, 600)
graph_even.Draw("AP")
graph_odd.Draw("P same")

graph_even.GetXaxis().SetTitle("ΔR between gen photon pairs (π⁰ candidates)")
graph_even.GetYaxis().SetTitle("Number of reconstructed photons")

legend = ROOT.TLegend(0.65, 0.75, 0.88, 0.88)
legend.AddEntry(graph_even, "Even nReco", "p")
legend.AddEntry(graph_odd, "Odd nReco", "p")
legend.Draw()

canvas.SaveAs("nReco_vs_pi0GenDeltaR.png")
