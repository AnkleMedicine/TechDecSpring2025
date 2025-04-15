import importlib
import MayaUtil
importlib.reload(MayaUtil)

from MayaUtil import *
from PySide2.QtWidgets import QPushButton, QVBoxLayout
import maya.cmds as mc

class ProxyRigger:
    def __init__(self):
        self.skin = ""
        self.model = ""
        self.jnt = []

    def CreateProxyRigFromSelectMesh(self):
        mesh = mc.ls(sl=True)[0]
        if not IsMesh(mesh):
            raise TypeError(f"{mesh} is not a mesh! please select a mesh")
        
        self.model = mesh
        modelShape = mc.listRelatives(self.model, s=True)[0]
        print(f"find mesh {mesh} and shape {modelShape}")

        skin = GetAllConnectIn(modelShape, GetUpperStream, 10,  IsSkin)
        if not skin:
            raise Exception(f"{mesh} has no skin! this tool only works with a rigged model")
        self.skin = skin[0]

        jnts = GetAllConnectIn(modelShape, GetUpperStream, 10, IsJoint)
        if not jnts:
            raise Exception(f"{mesh} has no joint bound! this tool only works with a rigged model")
        self.jnts = jnts

        print(f"start build with mesh: {self.model}, skin: {self.skin}, joints: {self.jnts}")

        jntVertMap = self.GenerateJntVertDic()
        segments = []
        ctrls = []
        for jnt, verts in jntVertMap.items():
            print(f"join {jnt} controls {verts} primarily")
        

    def GenerateJntVertDic(self):
        dict = {}
        for jnt in self.jnts:
            dict[jnt] = []

        verts = mc.ls(f"{self.model}.vtx[*]", fl=True)
        for vert in verts:
            owningJnt = self.GetJntWithMaxInfluence(vert, self.skin)
            dict[owningJnt].append(vert)

        return dict
    

    def GetJntWithMaxInfluence(self, vert, skin):
        weights = mc.skinPercent(skin, vert, q=True, v=True)
        jnts= mc.skinPercent(skin, vert, q=True, t=None)

        maxWeightIndex = 0
        maxWeight = weights[0]

        for i in range(1, len(weights)):
            if weights[i] > maxWeight:
                maxWeight = weights[i]
                maxWeightIndex = 1

        return jnts[maxWeightIndex]

class ProxyRiggerWIdget(QMayaWindow):
    def __init__(self):
        super().__init__()
        self.proxyRigger = ProxyRigger()
        self.setWindowTitle("Proxy Rigger")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)
        generateProxyRigBtn = QPushButton("Generate Proxy Rig")
        self.masterLayout.addWidget(generateProxyRigBtn)
        generateProxyRigBtn.clicked.connect(self.GenerateProxyRigButtonClicked)

    def GenerateProxyRigButtonClicked(self):
        self.proxyRigger.CreateProxyRigFromSelectMesh()

    def GetWindowHash(self):
        return "d40df30fea48030c4919e0b529f90b20"
    
    
proxyRiggerWidget = ProxyRiggerWIdget()
proxyRiggerWidget.show()
