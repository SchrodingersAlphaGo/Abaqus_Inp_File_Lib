from InpLib import *
import numpy as np
import vtk

fname = "./Job-1.inp"

with open(fname, "r") as f:
    inpFileContents = f.readlines()

part = Part()
nodeStartNumber = 0
nodeEndNumber = 0
elementStartNumber = 0
elementEndNumber = 0

# allSets = []
allSetStart = {}


for i in range(0, len(inpFileContents)):
    line = inpFileContents[i]
    if not part.start and partKeys in line:
        part.startLineNum = i
        part.start = True
    if nodeKeys in line:
        nodeStartNumber = i+1
    if elementKeys in line:
        elementStartNumber = i+1
        nodeEndNumber = i
    if endPartKeys in line:
        elementEndNumber = i
    if setKeys in line:
        llist = line.split(",")
        if llist[0] == "*Nset":
            name = llist[1].split("=")[-1]
            allSetStart[name] = i+1

# analyze nodes
allNodes = []
for i in range(nodeStartNumber, nodeEndNumber):
    llist = inpFileContents[i].split(",")
    p = np.array([float(llist[1]),float(llist[2]),float(llist[3])])
    allNodes.append(p)
numNodes = len(allNodes)
print("number of nodes : ", numNodes)

# analyze elements
allElements = []
for i in range(elementStartNumber, elementEndNumber):
    llist = inpFileContents[i].split(",")
    elist = [int(llist[j]) for j in range(1, len(llist))]
    allElements.append(elist)
numElements = len(allElements)
print("number of elements : ", numElements)

# analyze all sets
allNsets = {}
for setname,nline in allSetStart.items():
    i = nline  # number of line
    # print(i)
    while (True):
        if "generate" in inpFileContents[i-1]:
            llist = inpFileContents[i].split(",")
            # print(llist)
            allNsets[setname] = [int(llist[j]) for j in range(len(llist))]
            break
        else:
            if setname not in allNsets:
                allNsets[setname] = []
            llist = inpFileContents[i].split(",")
            try:
                a = int(llist[0])
                allNsets[setname] += [int(llist[j]) for j in range(len(llist))]
                i += 1
            except:
                break
# for k,v in allNsets.items():
    # print(k, len(v))

# split in z
# each layer
for setname, set in allNsets.items(): 
    if len(set) == 3: continue
    # create vtkPoints
    vpts = vtk.vtkPoints()
    for i in set:
        p = tuple(allNodes[i])
        vpts.InsertNextPoint(p)

    # create kdTree
    kdtree = vtk.vtkKdTree()
    kdtree.BuildLocatorFromPoints(vpts)

    # find first column points
    firstColumnPoints = []
    for i in set:
        # find closest 4 points
        pId = set[i]
        p = allNodes[pId] 
        idList = vtk.vtkIdList()
        kdtree.FindClosestNPoints(5, p, idList)
        for j in range(idList.GetNumberOfIds()):
            pIdj = idList.GetId(j)
            if pIdj == pId: continue
            pj = vpts.GetPoint(pIdj)
            

# 

# create fiber for each layer

# output
        
        


