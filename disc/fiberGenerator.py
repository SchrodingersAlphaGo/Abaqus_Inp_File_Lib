import numpy as np
import sys
sys.path.append("../../../coding/GitHub/Abaqus_Inp_File_Lib/")
from InpLib import *

fname = "./Job-1.inp"

partSymbol = "*Part, name=disc-2"
nodeSymbol = "*Node"
elementSymbol = "*Element, type=C3D8R"
endPartSymbol = "*End Part"


# read nodes, elements
with open(fname, 'r') as f:
    inpFileContent = f.readlines()

nodeStartLine = 0
nodeEndLine = 0

elementStartLine = 0
elementEndLine = 0

for line in inpFileContent:


