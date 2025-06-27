import numpy as np
import ROOT

# Open ROOT file
file = ROOT.TFile("miniTree.root")
tree = file.Get("outtree")  # double-check the tree name if needed

# Set up photon 4-vector branches
pho_e = ROOT.std.vector('float')()
pho_px = ROOT.std.vector('float')()
pho_py = ROOT.std.vector('float')()
pho_pz = ROOT.std.vector('float')()

tree.SetBranchAddress("photonE", pho_e)
tree.SetBranchAddress("photonPx", pho_px)
tree.SetBranchAddress("photonPy", pho_py)
tree.SetBranchAddress("photonPz", pho_pz)

min_mass = float('inf')
max_mass = 0.0

# Loop over events to find min and max invariant mass
for i in range(tree.GetEntries()):
    tree.GetEntry(i)

    if pho_e.size() >= 2:
        E = pho_e[0] + pho_e[1]
        px = pho_px[0] + pho_px[1]
        py = pho_py[0] + pho_py[1]
        pz = pho_pz[0] + pho_pz[1]

        m2 = E**2 - px**2 - py**2 - pz**2

        # Check m2 positive and reasonable
        if m2 > 0 and m2 < 1e6:  # 1e6 GeV^2 = 1 TeV^2, adjust if needed
            inv_mass = np.sqrt(m2)
            if inv_mass < min_mass:
                min_mass = inv_mass
            if inv_mass > max_mass:
                max_mass = inv_mass

print(f"Minimum invariant mass found: {min_mass:.3f} GeV")
print(f"Maximum invariant mass found: {max_mass:.3f} GeV")

file.Close()
