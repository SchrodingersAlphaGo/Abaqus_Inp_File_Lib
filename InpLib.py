import numpy as np

headingKeys = "*Heading"
partKeys = "*Part, "
nodeKeys = "*Node"
elementKeys = "*Element, "
endPartKeys = "*End Part"
assemblyKeys = "Assembly, "
instanceKeys = "*Instance, "
instanceEndKeys = "*End Instance"
setKeys = "set, "

class XSet:
    def __init__(self) -> None:
        self.name = ""
        self.type = ""
        self.instance = ""
        self.pattern = ""
        self.generate = []
        self.list = []

class Material:
    def __init__(self) -> None:
        self.name = ""
        self.Density = 0
        self.YoungsModulus = 0
        self.PoissonRatio = 0

class Module:
    def __init__(self) -> None:
        self.start = False
        self.startLineNum = 0
        self.end = False
        self.endLineNum = 0

class Header(Module):
    def __init__(self) -> None:
        super().__init__()
        self.description = ""
        self.jobName = ""
        self.ModelName = ""
        self.software = ""
        self.softwareVersion = ""

class Part(Module):
    def __init__(self) -> None:
        super().__init__()
        self.partName = ""
        self.nodes = ""
        self.elements = ""
        self.sets = []

class Property(Module):
    def __init__(self) -> None:
        super().__init__()
        self.Material = 0

class Instance:
    def __init__(self) -> None:
        self.name = ""
        self.part = ""

class assembly:
    pass

class step:
    pass

class interaction:
    pass

class load:
    pass

