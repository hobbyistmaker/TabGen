class FingerFace:

    def __init__(self, bface, ui):
        self.__ui = ui
        self.__bface = bface
        self.__evaluator = bface.evaluator
        pRange = self.evaluator.parametricRange()

        self.__xlen = pRange.maxPoint.x - pRange.minPoint.x
        self.__ylen = pRange.maxPoint.y - pRange.minPoint.y

        self.__width = min(self.__xlen, self.__ylen)
        self.__length = max(self.__xlen, self.__ylen)

        self.__xy = False
        self.__xz = False
        self.__yz = False

        self.__connected = []

        self.__find_axes()

    def __find_axes(self, start_tab=True):
        if self.__bface.vertices:
            xlen, ylen, zlen = (0, 0, 0)
            xaxis, yaxis, zaxis = (0, 0, 0)
            xmax, ymax, zmax = (0, 0, 0)
            xmin, ymin, zmin = (0, 0, 0)

            point = self.__bface.vertices.item(0).geometry
            for j in range(1, self.__bface.vertices.count):
                vertex = self.__bface.vertices.item(j).geometry
                xaxis = 0 if (vertex.x == point.x) and not xaxis else 1
                yaxis = 0 if (vertex.y == point.y) and not yaxis else 1
                zaxis = 0 if (vertex.z == point.z) and not zaxis else 1

                xlen = max(xlen, vertex.x)
                ylen = max(ylen, vertex.y)
                zlen = max(zlen, vertex.z)

                xmax = max(xmax, vertex.x)
                xmin = min(xmin, vertex.x)
                ymax = max(ymax, vertex.y)
                ymin = min(ymin, vertex.y)
                zmax = max(zmax, vertex.z)
                zmin = min(zmin, vertex.z)

            if xaxis and yaxis:
                self.__xy = True
                if xlen == self.__width:
                    self.__axis = self.parent.yConstructionAxis
                else:
                    self.__axis = self.parent.xConstructionAxis

            elif xaxis and zaxis:
                self.__xz = True

                if xlen == self.__width:
                    self.__axis = self.parent.zConstructionAxis
                else:
                    self.__axis = self.parent.xConstructionAxis

            elif yaxis and zaxis:
                self.__yz = True

                if ylen == self.__width:
                    self.__axis = self.parent.zConstructionAxis
                else:
                    self.__axis = self.parent.yConstructionAxis

    @property
    def axis(self):
        return self.__axis

    @property
    def bface(self):
        return self.__bface

    @property
    def body(self):
        return self.__bface.body

    @property
    def planes(self):
        return self.parent.constructionPlanes

    @property
    def evaluator(self):
        return self.__bface.evaluator

    @property
    def extrudes(self):
        return self.parent.features.extrudeFeatures

    @property
    def length(self):
        return self.__length

    @property
    def mirrors(self):
        return self.parent.features.mirrorFeatures

    @property
    def parent(self):
        return self.__bface.body.parentComponent

    @property
    def patterns(self):
        return self.parent.features.rectangularPatternFeatures

    @property
    def perpendicular_faces(self):
        connected = []
        edges = self.__bface.edges
        for j in range(0, edges.count):
            edge = edges.item(j)
            if edge.length == self.__width:
                faces = edge.faces
                for i in range(0, faces.count):
                    face = faces.item(i)
                    if face != self.__bface:
                        connected.append(face)

        return connected

    @property
    def vertical(self):
        if self.__xlen == self.__width:
            return True
        return False

    @property
    def width(self):
        return self.__width

    @property
    def xy(self):
        return self.__xy

    @property
    def xz(self):
        return self.__xz

    @property
    def yz(self):
        return self.__yz

