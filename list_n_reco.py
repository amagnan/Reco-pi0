import ROOT

# Open the ROOT file and tree
file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")

# Set up reconstructed photon energy vector
pho_e = ROOT.std.vector('double')()
tree.SetBranchAddress("photonE", pho_e)

# Loop through events and print number of reconstructed photons
print("Event\tNumber of Reco Photons")
print("-" * 30)

for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    n_reco = pho_e.size()
    print(f"{i}\t{n_reco}")

file.Close()
