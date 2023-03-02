# generate fiber of all disc

# from InpLib import *
import numpy as np
import vtk
import matplotlib.pyplot as plt

# fname = "./Job-1.inp"
fname = r"F:\ZAY\Code\abaqus\Abaqus_Inp_File_Lib\Job-3.inp"

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
        self.Nsets = {}
        self.czLines = {}
        self.sortedLines = {}
        self.fibers = {}

class Nset:
    def __init__(self) -> None:
        self.setName = ""
        self.instance = ""
        self.isGenerate = False
        self.setList = []


instanceDict = {}

currentInstanceOpened = False
nodeOpened = False
elementOpend = False
setLineNoList = []


for i in range(len(inpFileContents)):
    row = inpFileContents[i]
    rowSplited = row.split(",")
    if "*Instance," in row:
        currentInstance = Instance()
        currentInstance.name = rowSplited[1].split("=")[-1].strip()
        currentInstance.part = rowSplited[2].split("=")[-1].strip()
        currentInstanceOpened = True
    if currentInstanceOpened and "*Node" in row:
        nodeOpened = True
        continue

    if nodeOpened:
        try:
            tmp = int(rowSplited[0])
            pos = np.zeros(3)
            pos[0],pos[1],pos[2] = float(rowSplited[1]),float(rowSplited[2]),float(rowSplited[3])
            currentInstance.node.append(pos)
            continue
        except:
            nodeOpened = False

    if currentInstanceOpened and "*Element, " in row:
        elementOpend = True
        for x in rowSplited:
            if "type=" in x:
                currentInstance.element.type = (x.split("=")[-1]).strip()
                break
        continue

    if elementOpend:
        try:
            tmp = int(rowSplited[0])
            nlist = [int(x) for x in rowSplited[1:]]
            currentInstance.element.elementList.append(nlist)
            continue
        except:
            elementOpend = False

    if currentInstanceOpened and "*End Instance" in row:
        currentInstanceOpened = False
        instanceDict[currentInstance.name] = currentInstance
        continue

    if "*Nset, " in row:
        setLineNoList.append(i)
        continue

print("number of Instance : ", len(instanceDict))

nn = 0; en = 0
for name,inst in instanceDict.items():
    # print("Instance : ", inst.name)
    nl = len(inst.node)
    el = len(inst.element.elementList)
    # print("number of Nodes : ", nl)
    # print("number of elements : ", el)
    # print("--"*20)
    nn += nl
    en += el
print("number of all nodes : ", nn)
print("number of all elements : ", en)

print("number of Nset : ", len(setLineNoList))

# exit()
setDict = {}

# read Nset
for i in setLineNoList:
    setOpened = True
    currentNset = Nset()
    row = inpFileContents[i]
    rowSplited = row.split(",")
    if "generate" in row:
        currentNset.isGenerate = True
    currentNset.setName = rowSplited[1].split('=')[-1].strip()
    currentNset.instance = rowSplited[2].split('=')[-1].strip()
    setDict[currentNset.setName] = currentNset

    ii = i+1
    if currentNset.isGenerate:
        row = inpFileContents[ii]
        rowSplited = row.split(",")
        currentNset.setList = [x-1 for x in range(int(rowSplited[0]),int(rowSplited[1])+1)]
        continue

    while setOpened:
        row = inpFileContents[ii]
        rowSplited = row.split(",")
        try:
            tmp = int(rowSplited[0])
            tempList = [int(x)-1 for x in rowSplited]
            currentNset.setList.extend(tempList)
            ii += 1
            continue
        except:
            setOpened = False

print("number Nset : ", len(setDict))
# for name, set in setDict.items():
#     print(name,', ', len(set.setList))

# === generate f ===
# separate Nsets by Instance
for name, nset in setDict.items():
    # print(name)
    nameSplited = name.split('-')
    # annulusNo = nameSplited[1]
    currInst = instanceDict[nset.instance]
    layerType = nameSplited[2]
    layerNo = int(nameSplited[3])
    # if "layer" in name:
    if layerType not in currInst.Nsets:
            currInst.Nsets[layerType] = {}
    currInst.Nsets[layerType][layerNo] = nset.setList
    

def generateFibers(ins:Instance) -> None:
    layers = ins.Nsets["layer"]
    zs = ins.Nsets['z']
    nodes = ins.node
    # find each z line for each layer
    for lyNo, lyList in layers.items():
        for zNo, zList in zs.items():
            czName = "c-%d-z-%d"%(lyNo, zNo)
            ins.czLines[czName] = list(set(lyList) & set(zList))
            # print(czName, len(ins.czLines[czName]))
            # input()
    # sort z-0 line for each circular
    for i in range(1,7): # each circular layer
        czName = "c-%d-z-0"%i
        z0list = ins.czLines[czName]

        vpts = vtk.vtkPoints()
        for j in z0list:
            p = nodes[j]
            vpts.InsertNextPoint(p)
        kdtree = vtk.vtkKdTree()
        kdtree.BuildLocatorFromPoints(vpts)

        initId = 0
        sortedIList = [initId]
        sortedNodeIds = [z0list[sortedIList[0]]]
        ending = False
        while True:
            p = nodes[sortedNodeIds[-1]]
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
                p1 = nodes[nId]
                dz = p1[2] - p[2]
                if np.abs(dz) > 0.5:
                    print("dz = ", dz)
            elif len(newIds) == 2:
                p0 = np.array(p)
                id1 = newIds[0]
                nid1 = z0list[id1]
                p1 = nodes[nid1]
                id2 = newIds[1]
                nid2 = z0list[id2]
                p2 = nodes[nid2]
                d01 = np.linalg.norm(p0-p1)
                d02 = np.linalg.norm(p0-p2)
                dz1 = p0[2] - p1[2]
                dz2 = p0[2] - p2[2]
                if d01 < d02:
                    sortedIList.append(id1)
                    sortedNodeIds.append(nid1)
                else:
                    sortedIList.append(id2)
                    sortedNodeIds.append(nid2)
            else:
                print("len newIds = ", len(newIds))
                exit()
            if len(sortedIList) == len(z0list):
                break
        
        ins.sortedLines[czName] = sortedNodeIds

    # sort other z line for each circular
    for i in range(1,7): # each circular layer
        nz = len(zs)
        sortedZ0List = ins.sortedLines["c-%d-z-0"%i]
        for k in range(1, nz):
            czName = "c-%d-z-%d"%(i,k)
            zlayerIds = ins.czLines[czName]
            sortedList = []

            vpts = vtk.vtkPoints()
            for i in zlayerIds:
                p = nodes[i]
                vpts.InsertNextPoint(p)

            kdtree = vtk.vtkKdTree()
            kdtree.BuildLocatorFromPoints(vpts)

            for i in sortedZ0List:
                p = nodes[i]
                id = vtk.vtkIdList()
                kdtree.FindClosestNPoints(1,p,id)
                nodeId = zlayerIds[id.GetId(0)]
                sortedList.append(nodeId)
            ins.sortedLines[czName] = sortedList

    # generate T3D2 elements
    


# for each Instance
for name, inst in instanceDict.items():
    print(name)
    generateFibers(inst)

# exit()

# '''


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
'''
