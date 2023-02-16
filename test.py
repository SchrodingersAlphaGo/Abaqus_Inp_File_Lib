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
for setname, setList in allNsets.items():
    print("set name : ", setname)
    setListLen = len(setList)
    if setListLen == 3: 
        continue
    # create vtkPoints
    vpts = vtk.vtkPoints()
    for i in range(setListLen):
        p = tuple(allNodes[setList[i]])
        vpts.InsertNextPoint(p)
        # vpts.SetPoint(i, p)

    # create kdTree
    kdtree = vtk.vtkKdTree()
    kdtree.BuildLocatorFromPoints(vpts)

    # find first column points
    pId = 0
    firstColumnPoints = [pId]
    for i in range(10):
        if i >= len(firstColumnPoints):
            break
        p = vpts.GetPoint(pId)
        print("p : ", p)
        idList = vtk.vtkIdList()
        kdtree.FindClosestNPoints(6, p, idList)
        zAxisPtsId = []
        zAxisDz = []
        xyAxisPtsId = []

        for j in range(idList.GetNumberOfIds()):
            pIdj = idList.GetId(j)
            # print("pidj : ", pIdj)
            if pIdj == pId: 
                continue
            pj = vpts.GetPoint(pIdj)
            # print(pj[2] , p[2])
            dz = pj[2] - p[2]
            if np.abs(dz) < 5e-1:
                xyAxisPtsId.append(pIdj)
            else:
                zAxisPtsId.append(pIdj)
                zAxisDz.append(dz)
            print(pId, pIdj, dz, pj)
        continue
        # print(xyAxisPtsId)
        # print(zAxisPtsId)
        # exclude z axial neighbor point at same side
        rmPid = []
        for m in range(len(zAxisDz)):
            for n in range(m+1, len(zAxisDz)):
                if zAxisDz[m] * zAxisDz[n] > 0:
                    if np.abs(zAxisDz[m]) < np.abs(zAxisDz[n]):
                        rmPid.append(zAxisPtsId[n])
                    else:
                        rmPid.append(zAxisPtsId[m])

        # if len(zAxisDz) == 2 and zAxisDz[0] * zAxisDz[1] > 0:
        #     if np.abs(zAxisDz[0]) < np.abs(zAxisDz[1]):
        #         zAxisPtsId.pop(1)
        #     else:
        #         zAxisPtsId.pop(0)
        # elif len(zAxisDz) == 3:
        #     if zAxisDz[0] * zAxisDz[1] > 0:
        #         if np.abs(zAxisDz[0]) < np.abs(zAxisDz[1]):
        #             zAxisPtsId.pop(1)
        #         else:
        #             zAxisPtsId.pop(0)
        for x in rmPid:
            zAxisPtsId.remove(x)

        colUpdated = False
        for x in zAxisPtsId:
            if x not in firstColumnPoints:
                firstColumnPoints.append(x)
                colUpdated = True
        print("zids : ", zAxisPtsId)
        print("1st col : ",firstColumnPoints)
        if colUpdated:
            pId = firstColumnPoints[i+1]
        print("pId : ", pId)
    # for id in firstColumnPoints:
        # p = vpts.GetPoint(id)
        # print(id, p[2])
    exit()

# 

# create fiber for each layer

# output
        
        


