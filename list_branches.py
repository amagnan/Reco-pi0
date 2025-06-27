import ROOT

f = ROOT.TFile("miniTree.root")
tree = f.Get("outtree")
if not tree:
    print("Tree 'outtree' not found!")
    exit(1)

print("Branches in 'outtree':")
for branch in tree.GetListOfBranches():
    print(branch.GetName())

f.Close()