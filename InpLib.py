import numpy as np

class PartSet:
    def __init__(self) -> None:
        self.name = ""
        self.type = ""

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
        self.Material

class assembly:
    pass

class step:
    pass

class interaction:
    pass

class load:
    pass