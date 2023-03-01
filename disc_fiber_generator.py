# generate fiber of all disc

# from InpLib import *
import numpy as np
import vtk
import matplotlib.pyplot as plt

# fname = "./Job-1.inp"
fname = "../Job-3.inp"

with open(fname, "r") as f:
    inpFileContents = f.readlines()

class Element:
    def __init__(self) -> None:
        self.type = None
        self.elementList = []

class Instance:
    def __init__(self) -> None:
        self.name = ""
        self.part = ""
        self.node = []
        self.element = Element()
        # self.closed = False

class Nset:
    def __init__(self) -> None:
        self.nset = ""
        self.instance = ""
        self.isGenerated = False
        self.setList = []


instanceDict = {}

for i in range(len(inpFileContents)):
    row = inpFileContents[i]
    if "*Instance," in row:
        splitedRow = row.split(",")
        currentInstance = Instance()
        currentInstance.name = splitedRow[1].split("=")[-1]
        currentInstance.part = splitedRow[2].split("=")[-1]
        currentInstanceOpened = True
        print(currentInstance.name)
        print(currentInstance.part)
    

    if currentInstanceOpened and "*End Instance" in row:
        currentInstanceOpened = False

exit()
part = Part()
nodeStartNumber = 0
nodeEndNumber = 0
elementStartNumber = 0
elementEndNumber = 0

# allSets = []
allSetStart = {}

# analyze starting and ending line of each part
for i in range(0, len(inpFileContents)):
    line = inpFileContents[i]
    if not part.start and partKeys in line:
        part.startLineNum = i
        part.start = True
    if part.start and nodeKeys in line:
        nodeStartNumber = i+1
    if part.start and elementKeys in line:
        elementStartNumber = i+1
        nodeEndNumber = i
    if part.start and endPartKeys in line:
        elementEndNumber = i
        part.start = False
        part.end = True
    if setKeys in line:             # get start line of each node set
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
            break  # only one line in this set 
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

# separate circular layers and z layers
circularLayerDict = {}
zLayerDict = {}
for setname, setList in allNsets.items():
    if len(setList) == 3 and setList[-1] == 1:          
        # expand 'generate set'
        tempList = [i-1 for i in range(setList[0], setList[1]+1)]
    elif len(setList) > 3:
        tempList = [i-1 for i in setList]
    if "layer-" in setname:
        circularLayerDict[setname] = (tempList)
    elif "z-" in setname:
        zLayerDict[setname] = (tempList)

# check len of each layer
# for k,v in circularLayerDict.items():
#     print(k, len(allNsets[k]),len(v))
# for k,v in zLayerDict.items():
#     print(k, len(allNsets[k]),len(v))

# get each z layer for each circular layer
# for each circular layer
separatedCircularSets = {}
for cSetName, cList in circularLayerDict.items():
    separatedCircularSets[cSetName] = {}
    # for each all z layer
    for zSetName, zList in zLayerDict.items():
        # get union of two set
        separatedCircularSets[cSetName][zSetName] = list(set(cList) & set(zList))

# sort z-0 layer of each circular layer
sortedZ0Dict = {}
for setName, cSet in separatedCircularSets.items():
    # print("circular layer name: ", setName)
    vpts = vtk.vtkPoints()
    # sort z-0 layer
    
    z0SetName = "z-0"
    z0list = cSet[z0SetName] # layer-0, z-0
    for x in z0list:
        p = allNodes[x]
        vpts.InsertNextPoint(tuple(p))
    # print("number of points: ", vpts.GetNumberOfPoints())

    kdtree = vtk.vtkKdTree()
    kdtree.BuildLocatorFromPoints(vpts)
    
    # print("layer0, z0: ",z0list)
    # for i in range(len(z0list)):
        # print(i,z0list[i])

    initId = 0
    sortedIList = [initId]
    sortedNodeIds = [z0list[sortedIList[0]]]
    ending = False
    while True:
        p = allNodes[sortedNodeIds[-1]]
        idList = vtk.vtkIdList()
        kdtree.FindClosestNPoints(3, p, idList)
        newIds = []
        for i in range(idList.GetNumberOfIds()):
            id = idList.GetId(i)
            if id not in sortedIList:
                newIds.append(id)

        if len(newIds) == 1:
            id = newIds[0]
            nId = z0list[id]
            # print(id, nId)
            sortedIList.append(id)
            sortedNodeIds.append(nId)
            p1 = allNodes[nId]
            dz = p1[2] - p[2]
            if np.abs(dz) > 0.5:
                print("dz = ", dz)
        elif len(newIds) == 2:
            p0 = np.array(p)
            id1 = newIds[0]
            nid1 = z0list[id1]
            p1 = allNodes[nid1]
            id2 = newIds[1]
            nid2 = z0list[id2]
            p2 = allNodes[nid2]
            d01 = np.linalg.norm(p0-p1)
            d02 = np.linalg.norm(p0-p2)
            dz1 = p0[2] - p1[2]
            dz2 = p0[2] - p2[2]
            if d01 < d02:
                sortedIList.append(id1)
                sortedNodeIds.append(nid1)
                # if np.abs(dz1) > 0.5:
                    # print("dz = ", dz)
            else:
                sortedIList.append(id2)
                sortedNodeIds.append(nid2)
                # if np.abs(dz2) > 0.5:
                    # print("dz = ", dz)

        else:
            print("len newIds = ", len(newIds))
            exit()
        if len(sortedIList) == len(z0list):
            break
    
    sortedZ0Dict[setName] = sortedNodeIds

    # print(sortedIList)
    # print(sorted(sortedIList))
    # print(sortedNodeIds)
    # print(sorted(z0list))
    # print(sorted(sortedNodeIds))
    # sz0list = sorted(z0list)
    # ssortedNodeIds = sorted(sortedNodeIds)
    # for i in range(len(sz0list)):
    #     dd = sz0list[i] - ssortedNodeIds[i]
    #     if np.abs(dd) > 0.1:
    #         print(sz0list[i], ssortedNodeIds[i])
    # x = [allNodes[i][0] for i in sortedNodeIds]
    # y = [allNodes[i][1] for i in sortedNodeIds]

    # plt.plot(x,y,'o-')
    # plt.show()

    # exit()

# sort other z layer of each circular layer
sortedZDict = {}
for setName, cSet in separatedCircularSets.items():
    sortedZDict[setName] = {}
    sortedZ0List = sortedZ0Dict[setName]
    sortedZDict[setName]["z-0"] = sortedZ0List
    for nzLayer in range(1,7): # other z layer
        zlayerName = "z-" + str(nzLayer)
        zlayerIds = cSet[zlayerName]
        sortedZDict[setName][zlayerName] = []

        vpts = vtk.vtkPoints()
        for i in zlayerIds:
            p = allNodes[i]
            vpts.InsertNextPoint(p)

        kdtree = vtk.vtkKdTree()
        kdtree.BuildLocatorFromPoints(vpts)

        for i in sortedZ0List:
            p = allNodes[i]
            id = vtk.vtkIdList()
            kdtree.FindClosestNPoints(1,p,id)
            nodeId = zlayerIds[id.GetId(0)]
            sortedZDict[setName][zlayerName].append(nodeId)
        # x = [allNodes[i][0] for i in sortedZDict[setName][zlayerName]]
        # y = [allNodes[i][1] for i in sortedZDict[setName][zlayerName]]
        # plt.plot(x,y,"o-")
        # plt.title(setName + "-" + zlayerName)
        # plt.show()

# create T3D2 elements
# nodes
nodes = "*Node\n"
for i in range(nodeStartNumber, nodeEndNumber):
    row = inpFileContents[i]
    nodes += row

fiberParts = {}
outputStr = ""
for setName, zDics in sortedZDict.items():
    # fiberParts[setName] = {}
    # fiberParts[setName]["partname"] = "*Part, name=Part-" + setName + "\n"
    # fiberParts[setName]["elements"] = "*Element, type=T3D2\n"
    outputStr += "*Part, name=Part-" + setName + "\n"
    outputStr += nodes
    outputStr += "*Element, type=T3D2\n"
    
    lenZ0 = len(zDics["z-0"])
    nele = 1
    elementStr = ""
    # print(zDics.keys())
    for i in range(0,lenZ0): # each node in z-0 line
        for j in range(0,6): # each z layer
            iid = i+j
            if iid >= lenZ0:
                iid = iid - lenZ0
            jid = i+j+1
            if jid >= lenZ0:
                jid = jid - lenZ0
            # zin = "z-" + str(j)
            # print(zDics[zin])
            zi = zDics["z-" + str(j)][iid] + 1
            zj = zDics["z-" + str(j+1)][jid] + 1
            row = "\t%d, %d, %d\n" %(nele, zi, zj)
            elementStr += row
            nele += 1

            iid = i-j
            jid = i-j-1
            zi = zDics["z-" + str(j)][iid] + 1
            zj = zDics["z-" + str(j+1)][jid] + 1
            row = "\t%d, %d, %d\n" %(nele, zi, zj)
            elementStr += row
            nele += 1
    outputStr += elementStr
    outputStr += "*End Part\n"
        
for setName in sortedZDict.keys():
    row = "*Instance, name=Part-" + setName \
        + "-1, part=Part-" + setName \
            + "\n*End Instance\n"
    outputStr += row


with open("fibers.txt",'w',newline='') as f:
    f.write(outputStr)

    #     f.write(fiberParts[setName]["partname"])
    #     f.write(nodes)
    #     f.write(fiberParts[setName]["elements"])
    #     f.write("*End Part")

    # exit()
# part name
# truss elements
# output